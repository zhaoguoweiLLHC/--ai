#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地静态服务：解决 file:// 协议下语音插件不可用的问题。

用法：
    python3 serve.py                 # 默认打开 2020下/解析.html
    python3 serve.py 相对路径/文件.html  # 打开指定讲义，例如：
    python3 serve.py "404_高中数学学科/真题分卷/2024上/解析.html"

启动后浏览器自动打开，根目录是全部资料的索引页，可直接点进去。
停止服务：终端按 Ctrl+C（后台运行时用 lsof + kill 查端口）。
全程本地访问，不耗流量。
"""
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DEFAULT_TARGET = "404_高中数学学科/真题分卷/2020下/解析.html"

target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET
if not (ROOT / target).exists():
    print(f"文件不存在：{target}")
    sys.exit(1)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        pass  # 不打印访问日志，保持输出干净


# 避开 IDE 预览服务常用的 8000 端口，从 8890 起找空端口
server = None
for port in range(8890, 8900):
    try:
        server = HTTPServer(("127.0.0.1", port), Handler)
        break
    except OSError:
        continue

if server is None:
    print("8890-8899 端口都被占用了，请关掉一些服务再试")
    sys.exit(1)

url = f"http://localhost:{port}/" + quote(target)
print(f"服务已启动，本讲义地址：\n  {url}")
print("根目录是全部资料索引，可直接浏览其他卷子。")
print("看完后在终端按 Ctrl+C 停止服务。")

threading.Timer(1.0, lambda: webbrowser.open(url)).start()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n服务已停止")
