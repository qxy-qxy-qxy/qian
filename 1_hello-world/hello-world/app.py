"""A dependency-free web demo for the course 从 localhost 到全世界.

Windows: python app.py (or py app.py)
macOS / Linux: python3 app.py
Cloud demo: python3 app.py --host 0.0.0.0 --port 8000
"""

import argparse
import html
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

# 课堂发布新版时，只需修改下面两行，然后重启应用。
MESSAGE = "Hello World，欢迎来到我的第一个网站！"
VERSION = "v1"

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hello World · 从 localhost 到全世界</title>
  <style>
    :root { color-scheme: light; font-family: -apple-system, BlinkMacSystemFont,
      "Segoe UI", "Microsoft YaHei", sans-serif; color: #153151; background: #f7f9fc; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 36px 24px; }
    main { width: min(100%, 900px); }
    .course { font-size: 17px; color: #63758b; margin: 0 0 56px; }
    .version { color: #235dd9; font-weight: 700; font-size: 18px; }
    h1 { font-size: clamp(48px, 8vw, 84px); line-height: 1.1; letter-spacing: -3px;
      margin: 14px 0 24px; }
    .greeting { font-size: clamp(21px, 3vw, 28px); line-height: 1.6; margin: 0 0 36px; }
    button { background: #235dd9; border: 0; border-radius: 8px; color: white;
      padding: 15px 24px; font: inherit; font-weight: 650; cursor: pointer; }
    button:hover { background: #1948b3; }
    button:focus-visible { outline: 3px solid #de752f; outline-offset: 4px; }
    button:disabled { opacity: .65; cursor: wait; }
    .response { min-height: 78px; margin-top: 20px; max-width: 840px;
      font-size: 18px; line-height: 1.6; color: #63758b; }
    .response.ok { color: #17623c; }
    .response.error { color: #b33924; }
    footer { border-top: 1px solid #d8e2f0; padding-top: 22px; margin-top: 40px;
      display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;
      color: #63758b; font-size: 15px; }
    code { color: #de752f; overflow-wrap: anywhere; }
    a { color: #235dd9; text-underline-offset: 3px; }
    @media (max-width: 600px) { .course { margin-bottom: 36px; } footer { margin-top: 24px; } }
  </style>
</head>
<body>
  <main>
    <p class="course">从 localhost 到全世界 · 课堂示例</p>
    <span class="version" id="version">__VERSION__</span>
    <h1>Hello World.</h1>
    <p class="greeting" id="greeting">__MESSAGE__</p>
    <button id="hello" type="button">向服务器打个招呼</button>
    <p id="response" class="response" role="status" aria-live="polite">点击按钮，检查页面能否收到服务器的回应。</p>
    <footer>
      <span>当前访问地址：<code id="address"></code></span>
      <a href="/health" target="_blank" rel="noopener">查看服务状态</a>
    </footer>
  </main>
  <script>
    const button = document.querySelector('#hello');
    const response = document.querySelector('#response');
    document.querySelector('#address').textContent = location.origin;
    button.addEventListener('click', async () => {
      button.disabled = true;
      response.className = 'response';
      response.textContent = '正在等待服务器回应…';
      try {
        const reply = await fetch('/api/hello', { cache: 'no-store', signal: AbortSignal.timeout(8000) });
        if (!reply.ok) throw new Error(`HTTP ${reply.status}`);
        const data = await reply.json();
        response.className = 'response ok';
        response.textContent = `服务器已回应：${data.message}（${data.version}）`;
      } catch (error) {
        response.className = 'response error';
        response.textContent = '暂时联系不上服务器。请检查启动终端、访问地址和网络。';
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    """Only expose the demo page and two JSON endpoints, never the project files."""

    def do_GET(self):
        self.respond(send_body=True)

    def do_HEAD(self):
        self.respond(send_body=False)

    def respond(self, send_body):
        path = urlsplit(self.path).path
        if path == "/":
            body = PAGE.replace("__VERSION__", html.escape(VERSION)).replace(
                "__MESSAGE__", html.escape(MESSAGE)
            ).encode("utf-8")
            content_type = "text/html; charset=utf-8"
            status = 200
        elif path in ("/api/hello", "/health"):
            data = {"status": "ok", "version": VERSION}
            if path == "/api/hello":
                data.update(message=MESSAGE, time=datetime.now(timezone.utc).isoformat())
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            content_type = "application/json; charset=utf-8"
            status = 200
        elif path == "/favicon.ico":
            body, content_type, status = b"", "image/x-icon", 204
        else:
            body = b"Not Found\n"
            content_type, status = "text/plain; charset=utf-8", 404
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if send_body:
            self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Hello World classroom web demo")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="TCP port (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    try:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Cannot start server: {error}\nTry another free port with --port.\n")
    with server:
        address = "127.0.0.1" if args.host == "0.0.0.0" else args.host
        print(f"Hello World {VERSION}: http://{address}:{args.port}", flush=True)
        print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", flush=True)


if __name__ == "__main__":
    main()
