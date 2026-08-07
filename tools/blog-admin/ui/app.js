(function () {
  'use strict';

  var state = {
    token: '',
    posts: [],
    config: {},
    git: null,
    currentPost: null,
    filter: 'all',
    query: '',
    dirty: false,
    previewTimer: null,
    toastTimer: null
  };

  var viewMeta = {
    posts: ['CONTENT', '文章管理'],
    editor: ['EDITOR', '文章编辑器'],
    settings: ['CONFIG', '站点设置'],
    publish: ['DEPLOY', '发布博客']
  };

  function element(selector, root) {
    return (root || document).querySelector(selector);
  }

  function elements(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char];
    });
  }

  async function api(path, options) {
    var request = options || {};
    request.headers = Object.assign({}, request.headers || {}, {
      'Accept': 'application/json'
    });
    if (request.method && request.method !== 'GET') {
      request.headers['Content-Type'] = 'application/json';
      request.headers['X-Blog-Admin-Token'] = state.token;
    }
    var response = await fetch(path, request);
    var payload;
    try {
      payload = await response.json();
    } catch (error) {
      throw new Error('本地服务返回了无法识别的内容。');
    }
    if (!response.ok) throw new Error(payload.error || '操作失败。');
    return payload;
  }

  function showToast(message, isError) {
    var toast = element('#toast');
    toast.textContent = message;
    toast.classList.toggle('is-error', Boolean(isError));
    toast.classList.add('is-visible');
    clearTimeout(state.toastTimer);
    state.toastTimer = setTimeout(function () { toast.classList.remove('is-visible'); }, 3600);
  }

  function setBusy(button, busy, busyText) {
    if (!button) return;
    if (busy) {
      button.dataset.originalText = button.textContent;
      button.textContent = busyText || '处理中…';
      button.disabled = true;
    } else {
      button.textContent = button.dataset.originalText || button.textContent;
      button.disabled = false;
    }
  }

  function setDirty(dirty) {
    state.dirty = dirty;
    var indicator = element('#save-state');
    indicator.textContent = dirty ? '有未保存修改' : '已同步';
    indicator.classList.toggle('is-dirty', dirty);
  }

  function showView(name) {
    if (!viewMeta[name]) return;
    elements('.view').forEach(function (view) {
      view.classList.toggle('is-active', view.dataset.view === name);
    });
    elements('.nav-item[data-view-target]').forEach(function (item) {
      item.classList.toggle('is-active', item.dataset.viewTarget === name);
    });
    element('#view-eyebrow').textContent = viewMeta[name][0];
    element('#view-title').textContent = viewMeta[name][1];
    document.body.classList.remove('is-menu-open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (name === 'publish') refreshGitStatus();
  }

  function formatDate(value) {
    if (!value) return '未设置日期';
    return String(value).replace('T', ' ').slice(0, 16);
  }

  function visiblePosts() {
    var query = state.query.trim().toLowerCase();
    return state.posts.filter(function (post) {
      if (state.filter !== 'all' && post.status !== state.filter) return false;
      if (!query) return true;
      var haystack = [post.title, post.subtitle, post.excerpt].concat(post.tags || []).join(' ').toLowerCase();
      return haystack.indexOf(query) >= 0;
    });
  }

  function renderPostList() {
    var list = element('#post-list');
    var posts = visiblePosts();
    list.innerHTML = '';
    element('#count-all').textContent = String(state.posts.length);
    element('#count-published').textContent = String(state.posts.filter(function (post) { return post.status === 'published'; }).length);
    element('#count-drafts').textContent = String(state.posts.filter(function (post) { return post.status === 'draft'; }).length);

    if (!posts.length) {
      list.innerHTML = '<div class="empty-state"><strong>没有匹配的文章</strong><span>可以调整筛选条件，或者新建一篇文章。</span></div>';
      return;
    }

    posts.forEach(function (post) {
      var row = document.createElement('article');
      row.className = 'post-row';
      row.tabIndex = 0;
      row.dataset.file = post.file;
      var content = document.createElement('div');
      var title = document.createElement('h3');
      title.textContent = post.title;
      var excerpt = document.createElement('p');
      excerpt.textContent = post.subtitle || post.excerpt || '暂无摘要';
      var meta = document.createElement('div');
      meta.className = 'post-meta';
      (post.tags || []).slice(0, 5).forEach(function (tag) {
        var chip = document.createElement('span');
        chip.className = 'post-tag';
        chip.textContent = tag;
        meta.appendChild(chip);
      });
      if (post.mathjax) {
        var math = document.createElement('span');
        math.className = 'post-tag';
        math.textContent = 'MathJax';
        meta.appendChild(math);
      }
      content.append(title, excerpt, meta);
      var badge = document.createElement('span');
      badge.className = 'status-badge' + (post.status === 'draft' ? ' is-draft' : '');
      badge.textContent = post.status === 'draft' ? '草稿' : '已发布';
      var date = document.createElement('time');
      date.className = 'post-date';
      date.textContent = formatDate(post.date).slice(0, 10);
      row.append(content, badge, date);
      row.addEventListener('click', function () { openPost(post.file); });
      row.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openPost(post.file);
        }
      });
      list.appendChild(row);
    });
  }

  async function refreshPosts() {
    var payload = await api('/api/posts');
    state.posts = payload.posts;
    renderPostList();
  }

  function localDateTime() {
    var now = new Date();
    var offset = now.getTimezoneOffset() * 60000;
    return new Date(now.getTime() - offset).toISOString().slice(0, 16);
  }

  function slugFromTitle(title) {
    return String(title || '')
      .trim()
      .toLowerCase()
      .replace(/[\s_]+/g, '-')
      .replace(/[^\p{L}\p{N}-]+/gu, '')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 100);
  }

  function setPostForm(post) {
    var form = element('#post-form');
    var fields = form.elements;
    fields.status.value = post.status || 'draft';
    fields.date.value = post.date || localDateTime();
    fields.title.value = post.title || '';
    fields.subtitle.value = post.subtitle || '';
    fields.slug.value = post.slug || '';
    fields.author.value = post.author || state.config.title || 'Melting_Pot';
    fields.tags.value = (post.tags || []).join(', ');
    fields.headerImage.value = post.headerImage || 'img/bg-little-universe.jpg';
    fields.headerMask.value = String(post.headerMask == null ? 0.45 : post.headerMask);
    fields.mathjax.checked = Boolean(post.mathjax);
    fields.content.value = post.content || '';
    element('#mask-output').textContent = fields.headerMask.value;
    element('#trash-post').hidden = !post.file;
    renderPreview();
    setDirty(false);
  }

  function newPost() {
    state.currentPost = {
      file: '',
      status: 'draft',
      title: '',
      subtitle: '',
      date: localDateTime(),
      author: state.config.title || 'Melting_Pot',
      headerImage: 'img/bg-little-universe.jpg',
      headerMask: 0.45,
      tags: [],
      mathjax: false,
      slug: '',
      content: '## 从这里开始\n\n写下问题、背景和你的思考。\n',
      frontMatter: ''
    };
    setPostForm(state.currentPost);
    delete element('[name="slug"]', element('#post-form')).dataset.manuallyEdited;
    showView('editor');
    element('#view-title').textContent = '新建文章';
    element('[name="title"]', element('#post-form')).focus();
  }

  async function openPost(file) {
    try {
      var post = await api('/api/post?file=' + encodeURIComponent(file));
      state.currentPost = post;
      setPostForm(post);
      showView('editor');
      element('#view-title').textContent = post.title || '文章编辑器';
    } catch (error) {
      showToast(error.message, true);
    }
  }

  function formPostPayload() {
    var fields = element('#post-form').elements;
    return {
      originalFile: state.currentPost ? state.currentPost.file : '',
      frontMatter: state.currentPost ? state.currentPost.frontMatter : '',
      status: fields.status.value,
      date: fields.date.value,
      title: fields.title.value,
      subtitle: fields.subtitle.value,
      slug: fields.slug.value,
      author: fields.author.value,
      tags: fields.tags.value.split(/[,，]/).map(function (tag) { return tag.trim(); }).filter(Boolean),
      headerImage: fields.headerImage.value,
      headerMask: Number(fields.headerMask.value),
      mathjax: fields.mathjax.checked,
      content: fields.content.value
    };
  }

  async function savePost(event) {
    event.preventDefault();
    var button = event.submitter || element('#post-form .primary-button');
    setBusy(button, true, '保存中…');
    try {
      var payload = await api('/api/posts/save', { method: 'POST', body: JSON.stringify(formPostPayload()) });
      state.currentPost = payload.post;
      setPostForm(payload.post);
      await refreshPosts();
      element('#view-title').textContent = payload.post.title;
      showToast(payload.message);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      setBusy(button, false);
    }
  }

  async function trashCurrentPost() {
    if (!state.currentPost || !state.currentPost.file) return;
    if (!window.confirm('文章会被移入 .blog-admin-trash，本地仍可恢复。确定继续吗？')) return;
    var button = element('#trash-post');
    setBusy(button, true, '移动中…');
    try {
      var payload = await api('/api/posts/trash', {
        method: 'POST',
        body: JSON.stringify({ file: state.currentPost.file })
      });
      state.currentPost = null;
      await refreshPosts();
      showView('posts');
      showToast(payload.message);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      setBusy(button, false);
    }
  }

  function renderPreview() {
    var preview = element('#markdown-preview');
    var fields = element('#post-form').elements;
    var markdown = fields.content.value || '';
    var rendered;
    if (window.marked && window.DOMPurify) {
      window.marked.setOptions({ gfm: true, breaks: false });
      rendered = window.marked.parse(markdown);
      rendered = window.DOMPurify.sanitize(rendered);
    } else {
      rendered = '<pre>' + escapeHtml(markdown) + '</pre>';
    }
    preview.innerHTML = '<h1 class="preview-title">' + escapeHtml(fields.title.value || '未命名文章') + '</h1>' +
      '<p class="preview-subtitle">' + escapeHtml(fields.subtitle.value || '') + '</p><hr class="preview-rule">' + rendered;
    if (fields.mathjax.checked && preview.classList.contains('is-active') && window.MathJax && window.MathJax.typesetPromise) {
      if (window.MathJax.typesetClear) window.MathJax.typesetClear([preview]);
      window.MathJax.typesetPromise([preview]).catch(function () {});
    }
  }

  function schedulePreview() {
    clearTimeout(state.previewTimer);
    state.previewTimer = setTimeout(renderPreview, 180);
  }

  function fillSettings() {
    var form = element('#settings-form');
    Object.keys(state.config).forEach(function (key) {
      var field = form.elements[key];
      if (!field) return;
      field.value = Array.isArray(state.config[key]) ? state.config[key].join('\n') : state.config[key];
    });
  }

  async function saveSettings(event) {
    event.preventDefault();
    var button = event.submitter;
    var form = event.currentTarget;
    var payload = {};
    ['title', 'SEOTitle', 'description', 'keyword', 'home-tagline', 'home-status', 'footer-signature', 'github_username', 'sidebar-about-description'].forEach(function (key) {
      payload[key] = form.elements[key].value;
    });
    payload['home-principles'] = form.elements['home-principles'].value.split(/\r?\n/).map(function (line) { return line.trim(); }).filter(Boolean);
    setBusy(button, true, '保存中…');
    try {
      var result = await api('/api/config/save', { method: 'POST', body: JSON.stringify(payload) });
      state.config = result.config;
      fillSettings();
      setDirty(false);
      showToast(result.message);
    } catch (error) {
      showToast(error.message, true);
    } finally {
      setBusy(button, false);
    }
  }

  function renderGitStatus() {
    if (!state.git) return;
    element('#git-branch').textContent = state.git.branch || 'main';
    var container = element('#git-state');
    container.innerHTML = '';
    if (state.git.clean) {
      container.innerHTML = '<div class="git-clean"><strong>工作区干净</strong><span>暂无需要提交的修改。</span></div>';
      return;
    }
    state.git.changes.forEach(function (line) {
      var row = document.createElement('div');
      row.className = 'git-change';
      var code = document.createElement('code');
      code.textContent = line.slice(0, 2).trim() || 'M';
      var path = document.createElement('span');
      path.textContent = line.slice(3);
      row.append(code, path);
      container.appendChild(row);
    });
  }

  async function refreshGitStatus() {
    try {
      state.git = await api('/api/git/status');
      renderGitStatus();
    } catch (error) {
      showToast(error.message, true);
    }
  }

  async function publish(event) {
    event.preventDefault();
    var button = event.submitter;
    var message = event.currentTarget.elements.message.value;
    setBusy(button, true, '正在推送…');
    try {
      var result = await api('/api/publish', { method: 'POST', body: JSON.stringify({ message: message }) });
      state.git = result.status;
      renderGitStatus();
      showToast(result.message);
    } catch (error) {
      showToast(error.message, true);
      await refreshGitStatus();
    } finally {
      setBusy(button, false);
    }
  }

  function setWritingTab(name) {
    elements('[data-writing-tab]').forEach(function (tab) { tab.classList.toggle('is-active', tab.dataset.writingTab === name); });
    elements('[data-writing-surface]').forEach(function (surface) { surface.classList.toggle('is-active', surface.dataset.writingSurface === name); });
    if (name === 'preview') renderPreview();
  }

  function setupEvents() {
    document.addEventListener('click', function (event) {
      var viewButton = event.target.closest('[data-view-target]');
      if (viewButton) {
        if (state.dirty && !window.confirm('存在未保存修改，确定离开当前页面吗？')) return;
        setDirty(false);
        showView(viewButton.dataset.viewTarget);
      }
      if (event.target.closest('[data-action="new-post"]')) {
        if (state.dirty && !window.confirm('存在未保存修改，确定新建文章吗？')) return;
        newPost();
      }
      var writingTab = event.target.closest('[data-writing-tab]');
      if (writingTab) setWritingTab(writingTab.dataset.writingTab);
    });

    element('#post-search').addEventListener('input', function (event) {
      state.query = event.target.value;
      renderPostList();
    });
    elements('[data-post-filter]').forEach(function (button) {
      button.addEventListener('click', function () {
        state.filter = button.dataset.postFilter;
        elements('[data-post-filter]').forEach(function (item) { item.classList.toggle('is-active', item === button); });
        renderPostList();
      });
    });

    element('#post-form').addEventListener('submit', savePost);
    element('#post-form').addEventListener('input', function (event) {
      setDirty(true);
      if (event.target.name === 'headerMask') element('#mask-output').textContent = event.target.value;
      if (event.target.name === 'title' && state.currentPost && !state.currentPost.file && !element('[name="slug"]', event.currentTarget).dataset.manuallyEdited) {
        element('[name="slug"]', event.currentTarget).value = slugFromTitle(event.target.value);
      }
      schedulePreview();
    });
    element('[name="slug"]', element('#post-form')).addEventListener('input', function (event) { event.target.dataset.manuallyEdited = 'true'; });
    element('#trash-post').addEventListener('click', trashCurrentPost);
    element('#settings-form').addEventListener('submit', saveSettings);
    element('#settings-form').addEventListener('input', function () { setDirty(true); });
    element('#publish-form').addEventListener('submit', publish);
    element('#refresh-button').addEventListener('click', async function () {
      try {
        await Promise.all([refreshPosts(), refreshGitStatus()]);
        showToast('数据已刷新。');
      } catch (error) {
        showToast(error.message, true);
      }
    });
    element('.mobile-menu').addEventListener('click', function () { document.body.classList.toggle('is-menu-open'); });
    element('#admin-theme-toggle').addEventListener('click', function () {
      var theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      document.documentElement.style.colorScheme = theme;
      localStorage.setItem('melting-pot-admin-theme', theme);
      updateThemeLabel();
    });
    window.addEventListener('beforeunload', function (event) {
      if (!state.dirty) return;
      event.preventDefault();
      event.returnValue = '';
    });
  }

  function updateThemeLabel() {
    element('#admin-theme-toggle').textContent = document.documentElement.dataset.theme === 'dark' ? '切换日间模式' : '切换夜间模式';
  }

  async function initialize() {
    setupEvents();
    updateThemeLabel();
    try {
      var session = await api('/api/session');
      state.token = session.token;
      var results = await Promise.all([api('/api/posts'), api('/api/config'), api('/api/git/status')]);
      state.posts = results[0].posts;
      state.config = results[1];
      state.git = results[2];
      renderPostList();
      fillSettings();
      renderGitStatus();
      element('#loading-screen').classList.add('is-hidden');
    } catch (error) {
      element('#loading-screen p').textContent = error.message;
      showToast(error.message, true);
    }
  }

  initialize();
}());
