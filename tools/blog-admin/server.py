#!/usr/bin/env python3
"""Local-only management panel for the Melting_Pot Jekyll blog."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[1]
UI_DIR = APP_DIR / "ui"
POSTS_DIR = REPO_ROOT / "_posts"
DRAFTS_DIR = REPO_ROOT / "_drafts"
TRASH_DIR = REPO_ROOT / ".blog-admin-trash"
CONFIG_FILE = REPO_ROOT / "_config.yml"
SESSION_TOKEN = secrets.token_urlsafe(32)
CHINA_TZ = timezone(timedelta(hours=8))
MAX_BODY_BYTES = 2 * 1024 * 1024

MANAGED_CONFIG = {
    "title": "text",
    "SEOTitle": "text",
    "description": "text",
    "keyword": "text",
    "home-tagline": "text",
    "home-status": "text",
    "home-principles": "list",
    "footer-signature": "text",
    "github_username": "text",
    "sidebar-about-description": "text",
}

POST_FIELD_ORDER = [
    "layout",
    "title",
    "subtitle",
    "date",
    "author",
    "header-img",
    "header-mask",
    "tags",
    "mathjax",
]


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def run_git(*args: str, timeout: int = 45, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ApiError(500, "未找到 Git，请先安装 Git 并加入 PATH。") from exc
    except subprocess.TimeoutExpired as exc:
        raise ApiError(504, "Git 操作超时，请检查网络后重试。") from exc

    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "Git 操作失败").strip()
        raise ApiError(500, detail)
    return result


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def strip_inline_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote == '"':
            escaped = True
            continue
        if char in ("'", '"'):
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
        elif char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def parse_scalar(value: str) -> Any:
    value = strip_inline_comment(value.strip())
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [str(parse_scalar(part.strip())) for part in inner.split(",") if part.strip()]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def yaml_string(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=False)


def yaml_value(key: str, value: Any) -> str:
    if key == "tags":
        tags = value if isinstance(value, list) else []
        return "[" + ", ".join(yaml_string(tag) for tag in tags) + "]"
    if key == "mathjax":
        return "true" if bool(value) else "false"
    if key == "header-mask":
        try:
            return f"{min(max(float(value), 0), 1):g}"
        except (TypeError, ValueError):
            return "0.45"
    if key in {"layout", "date"}:
        return str(value)
    return yaml_string(value)


def split_front_matter(text: str) -> tuple[str, str]:
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---"):
        return "", normalized
    match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", normalized, re.S)
    if not match:
        return "", normalized
    return match.group(1), normalized[match.end():]


def parse_front_matter(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if not value and index + 1 < len(lines) and re.match(r"^\s+-\s+", lines[index + 1]):
            items: list[str] = []
            index += 1
            while index < len(lines):
                item = re.match(r"^\s+-\s+(.*)$", lines[index])
                if not item:
                    break
                items.append(str(parse_scalar(item.group(1))))
                index += 1
            data[key] = items
            continue
        data[key] = parse_scalar(value)
        index += 1
    return data


def update_front_matter(existing: str, values: dict[str, Any]) -> str:
    if not existing.strip():
        return "\n".join(f"{key}: {yaml_value(key, values[key])}" for key in POST_FIELD_ORDER if key in values)

    output: list[str] = []
    seen: set[str] = set()
    lines = existing.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if match and match.group(1) in values:
            key = match.group(1)
            output.append(f"{key}: {yaml_value(key, values[key])}")
            seen.add(key)
            index += 1
            while index < len(lines) and re.match(r"^\s+-\s+", lines[index]):
                index += 1
            continue
        output.append(lines[index])
        index += 1

    for key in POST_FIELD_ORDER:
        if key in values and key not in seen:
            output.append(f"{key}: {yaml_value(key, values[key])}")
    return "\n".join(output)


def normalize_slug(value: str) -> str:
    value = re.sub(r"[\s_]+", "-", value.strip().lower())
    value = "".join(char for char in value if char.isalnum() or char == "-")
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ApiError(400, "文章 slug 不能为空。")
    if len(value) > 100:
        raise ApiError(400, "文章 slug 不能超过 100 个字符。")
    return value


def safe_managed_path(relative: str) -> Path:
    relative = urllib.parse.unquote(relative or "").replace("\\", "/")
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise ApiError(400, "无效的文章路径。")
    candidate = (REPO_ROOT / relative).resolve()
    allowed = (POSTS_DIR.resolve(), DRAFTS_DIR.resolve())
    if not any(candidate.parent == directory for directory in allowed) or candidate.suffix.lower() not in {".md", ".markdown"}:
        raise ApiError(400, "文章路径不在允许的目录中。")
    return candidate


def date_for_input(value: Any, fallback: datetime | None = None) -> str:
    text = str(value or "")
    match = re.match(r"^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})", text)
    if match:
        return f"{match.group(1)}T{match.group(2)}"
    return (fallback or datetime.now(CHINA_TZ)).strftime("%Y-%m-%dT%H:%M")


def post_summary(path: Path, status: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    raw, content = split_front_matter(text)
    meta = parse_front_matter(raw)
    excerpt = re.sub(r"[`*_>#\[\]$|]", "", content)
    excerpt = re.sub(r"\s+", " ", excerpt).strip()[:150]
    relative = path.relative_to(REPO_ROOT).as_posix()
    return {
        "file": relative,
        "status": status,
        "title": str(meta.get("title") or path.stem),
        "subtitle": str(meta.get("subtitle") or ""),
        "date": str(meta.get("date") or ""),
        "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
        "mathjax": bool(meta.get("mathjax", False)),
        "excerpt": excerpt,
        "modified": datetime.fromtimestamp(path.stat().st_mtime, CHINA_TZ).isoformat(),
    }


def list_posts() -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    for directory, status in ((POSTS_DIR, "published"), (DRAFTS_DIR, "draft")):
        directory.mkdir(parents=True, exist_ok=True)
        for path in directory.glob("*.md"):
            posts.append(post_summary(path, status))
        for path in directory.glob("*.markdown"):
            posts.append(post_summary(path, status))
    return sorted(posts, key=lambda item: (item["date"], item["modified"]), reverse=True)


def load_post(relative: str) -> dict[str, Any]:
    path = safe_managed_path(relative)
    if not path.exists():
        raise ApiError(404, "文章不存在。")
    text = path.read_text(encoding="utf-8-sig")
    raw, content = split_front_matter(text)
    meta = parse_front_matter(raw)
    filename = path.stem
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename)
    try:
        header_mask = float(meta.get("header-mask") or 0.45)
    except (TypeError, ValueError):
        header_mask = 0.45
    return {
        "file": path.relative_to(REPO_ROOT).as_posix(),
        "status": "draft" if path.parent == DRAFTS_DIR.resolve() else "published",
        "title": str(meta.get("title") or ""),
        "subtitle": str(meta.get("subtitle") or ""),
        "date": date_for_input(meta.get("date"), datetime.fromtimestamp(path.stat().st_mtime, CHINA_TZ)),
        "author": str(meta.get("author") or "Melting_Pot"),
        "headerImage": str(meta.get("header-img") or "img/bg-little-universe.jpg"),
        "headerMask": header_mask,
        "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
        "mathjax": bool(meta.get("mathjax", False)),
        "slug": slug,
        "content": content.rstrip() + "\n",
        "frontMatter": raw,
    }


def save_post(payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title") or "").strip()
    if not title:
        raise ApiError(400, "文章标题不能为空。")
    content = str(payload.get("content") or "")
    slug = normalize_slug(str(payload.get("slug") or title))
    date_input = date_for_input(payload.get("date"))
    status = str(payload.get("status") or "draft")
    if status not in {"draft", "published"}:
        raise ApiError(400, "无效的文章状态。")

    date_part = date_input[:10]
    target_dir = POSTS_DIR if status == "published" else DRAFTS_DIR
    filename = f"{date_part}-{slug}.md" if status == "published" else f"{slug}.md"
    target = (target_dir / filename).resolve()
    if target.parent != target_dir.resolve():
        raise ApiError(400, "无效的目标文件名。")

    original_relative = str(payload.get("originalFile") or "")
    original = safe_managed_path(original_relative) if original_relative else None
    if target.exists() and (original is None or target != original):
        raise ApiError(409, f"目标文件已经存在：{target.name}")

    tags = payload.get("tags")
    if not isinstance(tags, list):
        tags = [item.strip() for item in str(tags or "").split(",") if item.strip()]
    tags = list(dict.fromkeys(str(tag).strip() for tag in tags if str(tag).strip()))
    values = {
        "layout": "post",
        "title": title,
        "subtitle": str(payload.get("subtitle") or "").strip(),
        "date": date_input.replace("T", " ") + ":00 +0800",
        "author": str(payload.get("author") or "Melting_Pot").strip(),
        "header-img": str(payload.get("headerImage") or "img/bg-little-universe.jpg").strip(),
        "header-mask": payload.get("headerMask", 0.45),
        "tags": tags,
        "mathjax": bool(payload.get("mathjax", False)),
    }
    front = update_front_matter(str(payload.get("frontMatter") or ""), values)
    document = f"---\n{front}\n---\n\n{content.lstrip(chr(13) + chr(10))}"
    if not document.endswith("\n"):
        document += "\n"

    atomic_write(target, document)
    if original and original != target and original.exists():
        original.unlink()
    return load_post(target.relative_to(REPO_ROOT).as_posix())


def trash_post(relative: str) -> dict[str, str]:
    source = safe_managed_path(relative)
    if not source.exists():
        raise ApiError(404, "文章不存在。")
    stamp = datetime.now(CHINA_TZ).strftime("%Y%m%d-%H%M%S-%f")
    destination = TRASH_DIR / stamp / source.parent.name / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    return {"message": "文章已移入本地回收目录。", "trash": str(destination.relative_to(REPO_ROOT))}


def read_config() -> dict[str, Any]:
    lines = CONFIG_FILE.read_text(encoding="utf-8-sig").splitlines()
    result: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if not match or match.group(1) not in MANAGED_CONFIG:
            index += 1
            continue
        key, value = match.groups()
        if MANAGED_CONFIG[key] == "list":
            items: list[str] = []
            index += 1
            while index < len(lines):
                item = re.match(r"^\s+-\s+(.*)$", lines[index])
                if not item:
                    break
                items.append(str(parse_scalar(item.group(1))))
                index += 1
            result[key] = items
            continue
        result[key] = str(parse_scalar(value))
        index += 1
    return result


def save_config(payload: dict[str, Any]) -> dict[str, Any]:
    lines = CONFIG_FILE.read_text(encoding="utf-8-sig").splitlines()
    output: list[str] = []
    seen: set[str] = set()
    index = 0
    while index < len(lines):
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if match and match.group(1) in MANAGED_CONFIG and match.group(1) in payload:
            key = match.group(1)
            seen.add(key)
            if MANAGED_CONFIG[key] == "list":
                output.append(f"{key}:")
                values = payload[key] if isinstance(payload[key], list) else []
                output.extend(f"  - {yaml_string(item)}" for item in values if str(item).strip())
                index += 1
                while index < len(lines) and re.match(r"^\s+-\s+", lines[index]):
                    index += 1
                continue
            output.append(f"{key}: {yaml_string(payload[key])}")
            index += 1
            continue
        output.append(lines[index])
        index += 1

    for key, kind in MANAGED_CONFIG.items():
        if key not in seen and key in payload:
            if kind == "list":
                output.append(f"{key}:")
                output.extend(f"  - {yaml_string(item)}" for item in payload[key] if str(item).strip())
            else:
                output.append(f"{key}: {yaml_string(payload[key])}")
    atomic_write(CONFIG_FILE, "\n".join(output) + "\n")
    return read_config()


def git_status() -> dict[str, Any]:
    branch = run_git("branch", "--show-current").stdout.strip() or "main"
    porcelain = run_git("status", "--short").stdout.splitlines()
    latest = run_git("log", "-1", "--pretty=format:%h%x09%s%x09%cr").stdout.strip().split("\t")
    remote = run_git("remote", "get-url", "origin", check=False).stdout.strip()
    return {
        "branch": branch,
        "changes": porcelain,
        "clean": not porcelain,
        "latest": {"hash": latest[0], "subject": latest[1], "when": latest[2]} if len(latest) >= 3 else None,
        "remote": remote,
    }


def publish_changes(message: str) -> dict[str, Any]:
    message = message.strip()
    if not message:
        raise ApiError(400, "请填写提交说明。")
    if len(message) > 120 or "\n" in message:
        raise ApiError(400, "提交说明应为不超过 120 个字符的单行文字。")

    staged = run_git("diff", "--cached", "--name-only").stdout.splitlines()
    unrelated = [
        path for path in staged
        if path != "_config.yml" and not path.startswith(("_posts/", "_drafts/"))
    ]
    if unrelated:
        raise ApiError(409, "检测到面板范围外的暂存文件，请先在终端处理：" + "、".join(unrelated))

    run_git("add", "-A", "--", "_posts", "_drafts", "_config.yml")
    changed = run_git("diff", "--cached", "--quiet", "--", "_posts", "_drafts", "_config.yml", check=False)
    branch = run_git("branch", "--show-current").stdout.strip() or "main"
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", branch):
        raise ApiError(400, "当前 Git 分支名称不安全，已停止推送。")
    if changed.returncode == 0:
        push_result = run_git("push", "origin", branch, timeout=120)
        output = (push_result.stdout + push_result.stderr).lower()
        synchronized = "everything up-to-date" not in output
        return {
            "message": "已推送之前未同步的提交。" if synchronized else "没有新修改，远程仓库已经同步。",
            "published": synchronized,
            "status": git_status(),
        }

    run_git("commit", "-m", message, timeout=60)
    run_git("push", "origin", branch, timeout=120)
    return {"message": "提交并推送成功，GitHub Pages 将自动更新。", "published": True, "status": git_status()}


class BlogAdminHandler(BaseHTTPRequestHandler):
    server_version = "MeltingPotAdmin/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            raise ApiError(404, "资源不存在。")
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def require_token(self) -> None:
        if not secrets.compare_digest(self.headers.get("X-Blog-Admin-Token", ""), SESSION_TOKEN):
            raise ApiError(403, "会话校验失败，请刷新管理面板。")
        origin = self.headers.get("Origin")
        if origin:
            expected = f"http://{self.headers.get('Host')}"
            if origin != expected:
                raise ApiError(403, "请求来源不受信任。")

    def require_local_host(self) -> None:
        host = self.headers.get("Host", "").split(":", 1)[0].strip().lower()
        if host not in {"127.0.0.1", "localhost"}:
            raise ApiError(403, "管理面板只接受本机地址访问。")

    def read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ApiError(400, "无效的请求长度。") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ApiError(413, "请求内容为空或过大。")
        try:
            value = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApiError(400, "无法解析请求内容。") from exc
        if not isinstance(value, dict):
            raise ApiError(400, "请求内容必须是对象。")
        return value

    def handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
        if path == "/api/session":
            self.send_json({"token": SESSION_TOKEN, "root": str(REPO_ROOT), "port": self.server.server_port})
        elif path == "/api/posts":
            self.send_json({"posts": list_posts()})
        elif path == "/api/post":
            self.send_json(load_post(query.get("file", [""])[0]))
        elif path == "/api/config":
            self.send_json(read_config())
        elif path == "/api/git/status":
            self.send_json(git_status())
        else:
            raise ApiError(404, "接口不存在。")

    def handle_api_post(self, path: str) -> None:
        self.require_token()
        payload = self.read_json()
        if path == "/api/posts/save":
            self.send_json({"post": save_post(payload), "message": "文章已保存到本地。"})
        elif path == "/api/posts/trash":
            self.send_json(trash_post(str(payload.get("file") or "")))
        elif path == "/api/config/save":
            self.send_json({"config": save_config(payload), "message": "站点配置已保存。"})
        elif path == "/api/publish":
            self.send_json(publish_changes(str(payload.get("message") or "")))
        else:
            raise ApiError(404, "接口不存在。")

    def do_GET(self) -> None:
        try:
            self.require_local_host()
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path.startswith("/api/"):
                self.handle_api_get(parsed.path, urllib.parse.parse_qs(parsed.query))
                return
            if parsed.path in {"/", "/index.html"}:
                self.send_file(UI_DIR / "index.html")
                return
            if parsed.path.startswith("/assets/"):
                name = parsed.path.removeprefix("/assets/")
                if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
                    raise ApiError(400, "无效的资源路径。")
                self.send_file(UI_DIR / name)
                return
            raise ApiError(404, "页面不存在。")
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception as exc:  # pragma: no cover - final safety net
            print(f"Unexpected error: {exc}", file=sys.stderr)
            self.send_json({"error": "服务器发生内部错误。"}, 500)

    def do_POST(self) -> None:
        try:
            self.require_local_host()
            self.handle_api_post(urllib.parse.urlparse(self.path).path)
        except ApiError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except Exception as exc:  # pragma: no cover - final safety net
            print(f"Unexpected error: {exc}", file=sys.stderr)
            self.send_json({"error": "服务器发生内部错误。"}, 500)


def main() -> None:
    parser = argparse.ArgumentParser(description="Melting_Pot 本地博客管理面板")
    parser.add_argument("--port", type=int, default=4173, help="本地监听端口，默认 4173")
    parser.add_argument("--no-browser", action="store_true", help="启动时不自动打开浏览器")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("端口必须位于 1024 到 65535 之间")

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), BlogAdminHandler)
    except OSError as exc:
        print(f"无法启动管理面板：端口 {args.port} 可能已被占用。", file=sys.stderr)
        raise SystemExit(1) from exc
    address = f"http://127.0.0.1:{args.port}"
    print("\nMelting_Pot Blog Admin")
    print(f"Repository: {REPO_ROOT}")
    print(f"Panel:      {address}")
    print("Local access only. Press Ctrl+C to stop.\n")
    if not args.no_browser:
        threading.Timer(0.7, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n管理面板已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
