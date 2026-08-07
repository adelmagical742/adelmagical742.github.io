# Melting_Pot · 个人技术博客

这是一个基于 Jekyll 的个人技术博客，用 Markdown 写文章，由 GitHub Pages 自动构建和托管。

## 本地预览

需要 Ruby、Bundler 和 Jekyll：

```bash
bundle install
bundle exec jekyll serve
```

浏览器打开 `http://localhost:4000`。

## 发布到 GitHub Pages

1. 创建自己的 GitHub 仓库。
2. 将远程地址写入本地仓库：

   ```bash
   git remote add origin 你的仓库地址
   ```

3. 提交并推送：

   ```bash
   git add .
   git commit -m "Initial Melting_Pot blog"
   git push -u origin main
   ```

4. 在仓库的 `Settings → Pages` 中选择 `Deploy from a branch`，分支选择 `main`，目录选择 `/ (root)`。

## 个性化入口

- `_config.yml`：站点名称、地址、头像、简介和社交账号；
- `_includes/about/zh.md`：关于页；
- `_posts/`：新建文章的位置；
- `css/custom.css`：独立视觉样式；
- `img/avatar-lab.svg`：默认头像。

## 新建文章

文章文件名建议使用：

```text
2026-08-07-my-first-post.md
```

文件顶部添加 Front Matter：

```yaml
---
layout: post
title: 我的第一篇文章
subtitle: 从这里开始记录
date: 2026-08-07
tags: [随笔, 技术]
---
```

主题依赖文件中的历史命名暂时保留，因为它们仍被构建脚本引用，不会影响站点标题、网页内容或网址。
