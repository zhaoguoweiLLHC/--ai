#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片生成v7：手机友好版，600px视口，scale=2，缩到1080宽"""
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import subprocess, os, tempfile

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
OUTPUT_DIR = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题解析-手机用"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def screenshot(filepath, outpath):
    with open(filepath, 'r') as f:
        content = f.read()
    # 只隐藏footer，back-link已在CSS里display:none
    css = 'footer{display:none!important}body{padding:8px!important}'
    inject = '<style>' + css + '</style>'
    if '</head>' in content:
        content = content.replace('</head>', inject + '</head>')
    else:
        content = inject + content

    tmp = tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w')
    tmp.write(content); tmp.close()
    subprocess.run([
        CHROME, '--headless=new', '--disable-gpu',
        '--force-device-scale-factor=2',
        '--window-size=600,20000',
        '--screenshot=' + outpath,
        '--hide-scrollbars', '--virtual-time-budget=2000',
        'file://' + tmp.name
    ], capture_output=True, timeout=30)
    os.unlink(tmp.name)

    img = Image.open(outpath)
    w, h = img.size
    # 裁底部空白
    bg = (242, 243, 247)
    px = img.load()
    last = h
    for y in range(h-1, -1, -1):
        found = False
        for x in range(0, min(w, 300), 3):
            r, g, b = px[x, y][:3]
            if abs(r-bg[0])>8 or abs(g-bg[1])>8 or abs(b-bg[2])>8:
                found = True; break
        if found:
            last = min(y + 16, h); break
    img = img.crop((0, 0, w, last))
    # 缩到1080宽
    ratio = 1080 / img.size[0]
    img = img.resize((1080, int(img.size[1]*ratio)), Image.LANCZOS)
    img.save(outpath, 'PNG')
    return img.size

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 清空旧图片
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith('.png'):
            os.remove(os.path.join(OUTPUT_DIR, f))

    years = [
        ("2025上", "2025上"), ("2024下", "2024下"), ("2024上", "2024上"),
        ("2023下", "2023下"), ("2023上", "2023上"), ("2022下", "2022下"),
        ("2022上", "2022上"), ("2021下", "2021下"), ("2021上", "2021上"),
        ("2020下", "2020下"),
    ]
    questions = [
        ("q12", "第12题"), ("q13", "第13题"),
        ("q15", "第15题"), ("q16", "第16题"), ("q17", "第17题"),
    ]

    total = 0
    for dirname, year_short in years:
        year_dir = os.path.join(BASE, dirname)
        print(f"=== {year_short} ===")
        for qnum, qlabel in questions:
            filepath = os.path.join(year_dir, f"{qnum}.html")
            if not os.path.exists(filepath):
                continue
            outname = f"{year_short}_{qnum}.png"
            outpath = os.path.join(OUTPUT_DIR, outname)
            size = screenshot(filepath, outpath)
            print(f"  {outname} ({size[0]}x{size[1]})")
            total += 1

    print(f"\n全部完成！共 {total} 张图片")
    print(f"输出目录: {OUTPUT_DIR}")
