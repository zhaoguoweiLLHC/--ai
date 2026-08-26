#!/usr/bin/env python3
"""把讲义 html / 文本 md/txt 转成手机长图 PNG（绕过 zip/pdf/html/txt/音频传输限制）。
用法：python3 make_longimg.py <源文件(html|md|txt)> <输出png> [宽度css px,默认820]
原理：Chrome headless 先量页面真实高度再截图，1.5倍清晰度。"""
import sys, subprocess, shutil, os, html, tempfile
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src,out=sys.argv[1],sys.argv[2]
W=int(sys.argv[3]) if len(sys.argv)>3 else 820

if src.endswith(".html"):
    page_src=src
    tmp_page=None
else:
    lines=open(src,encoding="utf-8").read().split("\n")
    body=[]
    for ln in lines:
        e=html.escape(ln)
        if e.startswith("="*8):
            body.append('<h2 style="border-bottom:2px solid #ff7ab8;margin:26px 0 10px;font-size:19px">'+e.strip("=")+'</h2>')
        elif e.startswith("【") and e.endswith("】"):
            body.append('<h3 style="background:#fdeef4;color:#e5487c;border-radius:8px;padding:6px 10px;margin:18px 0 8px;font-size:16px">'+e+'</h3>')
        elif e.startswith("# "):
            body.append('<h1 style="font-size:22px">'+e[2:]+'</h1>')
        elif e.startswith("## "):
            body.append('<h2 style="font-size:18px;border-left:5px solid #ff7ab8;padding-left:8px;margin:20px 0 8px">'+e[3:]+'</h2>')
        elif e.strip()=="":
            continue
        else:
            body.append('<p style="margin:6px 0">'+e+'</p>')
    tmp=tempfile.NamedTemporaryFile("w",suffix=".html",delete=False,encoding="utf-8")
    tmp.write('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>body{font-family:-apple-system,"PingFang SC",sans-serif;max-width:%dpx;margin:0 auto;padding:24px 18px 60px;line-height:1.8;color:#222;font-size:15px;}</style></head><body>%s</body></html>'%(W-40,"\n".join(body)))
    tmp.close(); tmp_page=tmp.name; page_src=tmp.name

# 1) 量真实高度：临时副本注入 title 脚本
probe=tempfile.NamedTemporaryFile("w",suffix=".html",delete=False,encoding="utf-8")
content=open(page_src,encoding="utf-8").read().replace("</body>","<script>document.title='H'+document.documentElement.scrollHeight</script></body>")
probe.write(content); probe.close()
dom=subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--dump-dom","file://"+probe.name],capture_output=True,text=True).stdout
H=800
import re
m=re.search(r"<title>H(\d+)</title>",dom)
if m: H=int(m.group(1))+20
os.unlink(probe.name)
# 2) 按真实高度截图（1.5x 清晰）
subprocess.run([CHROME,"--headless=new","--disable-gpu","--no-sandbox","--hide-scrollbars",
  "--screenshot="+out,"--window-size=%d,%d"%(W,H),"--force-device-scale-factor=1.5",
  "file://"+page_src],capture_output=True)
if tmp_page: os.unlink(tmp_page)
print(out,"高:",H)
