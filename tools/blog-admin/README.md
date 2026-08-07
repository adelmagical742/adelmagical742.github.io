# Melting_Pot 本地博客管理面板

这是一个只监听 `127.0.0.1` 的本地管理工具，不会被部署到 GitHub Pages，也不需要数据库或第三方 Python 包。

## 启动

在博客根目录双击 `manage-blog.cmd`，或在 PowerShell 中运行：

```powershell
.\manage-blog.ps1
```

浏览器会自动打开 `http://127.0.0.1:4173`。关闭启动窗口或按 `Ctrl+C` 即可停止服务。

如果端口被占用，可以手动指定：

```powershell
python tools/blog-admin/server.py --port 4180
```

## 第一版功能

- 浏览、搜索、新建和编辑 Markdown 文章；
- 在草稿与已发布状态之间切换；
- 预览 Markdown 与 MathJax 公式；
- 修改首页文字、站点介绍和 GitHub 用户名；
- 查看 Git 工作区状态；
- 提交并推送文章、草稿和 `_config.yml`；
- 删除文章时先移入 `.blog-admin-trash`，避免直接丢失。

## 安全边界

- 服务固定绑定 `127.0.0.1`，局域网中的其他设备无法访问；
- 写入路径限制在 `_posts`、`_drafts` 和 `_config.yml`；
- 发布接口只调用预先定义的 Git 参数，不接受终端命令；
- 每次启动都会生成新的本地会话令牌；
- 如果 Git 暂存区中存在面板范围外的文件，面板会拒绝一键发布。

Markdown 预览通过固定版本的 Marked、DOMPurify 和 MathJax CDN 加载；网络不可用时仍可编辑和保存，只是富文本预览会退化为纯文本。
