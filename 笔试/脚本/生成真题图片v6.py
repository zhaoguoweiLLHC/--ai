#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v6: 直接用文件操作注入CSS，避免字符串转义问题"""
import subprocess, os, re, tempfile
from PIL import Image

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
OUTPUT_DIR = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/答案图片合集"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# CSS文件——单独文件避免转义问题
CSS_FILE = "/tmp/inject_style.css"

def write_css():
    css = '.back-link{display:none!important}details{display:none!important}footer{display:none!important}.k-gold{display:none!important}.k-bibei{display:none!important}.tab-content{display:block!important}.tabs{display:none!important}body{width:750px!important;max-width:750px!important;margin:0 auto!important;padding:20px!important;font-size:18px!important;line-height:2!important;background:#f2f3f7!important;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif!important}.wrap{max-width:none!important;padding:0!important}section.card{padding:16px!important;margin-bottom:12px!important}.origin{font-size:16px!important}.tab-content .block{padding:14px!important;margin:4px 0 12px!important;font-size:18px!important;line-height:2.1!important}.tab-content .block p,.tab-content .block ul,.tab-content .block ol,.tab-content .block li{font-size:18px!important;line-height:2.1!important}.tab-content .block li{margin:6px 0!important}header.top{display:none!important}.tier-label{display:block;padding:8px 14px;margin:8px 0 2px;font-size:16px;font-weight:700;border-radius:8px 8px 0 0}.tier-label-full{background:#eef6ff;color:#1971c2}.tier-label-exam{background:#e9f9ef;color:#2b8a3e}.tier-label-life{background:#ffecec;color:#c92a2a}'
    with open(CSS_FILE, 'w') as f:
        f.write(css)

def process_file(filepath, year_short, q_label, output_dir):
    with open(filepath, 'r') as f:
        content = f.read()

    # 直接用硬编码CSS（不经过文件读写），用::before伪元素生成档位标签
    css = '.back-link{display:none!important}details{display:none!important}footer{display:none!important}.k-bibei{display:none!important}.tab-content{display:block!important}.tabs{display:none!important}body{width:750px!important;max-width:750px!important;margin:0 auto!important;padding:20px!important;font-size:18px!important;line-height:2!important;background:#f2f3f7!important;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif!important}.wrap{max-width:none!important;padding:0!important}section.card{padding:16px!important;margin-bottom:12px!important}.origin{font-size:16px!important}.tab-content .block{padding:14px!important;margin:4px 0 12px!important;font-size:18px!important;line-height:2.1!important}.tab-content .block p,.tab-content .block ul,.tab-content .block ol,.tab-content .block li{font-size:18px!important;line-height:2.1!important}.tab-content .block li{margin:6px 0!important}header.top{display:none!important}#t-full::before{content:"🏆 满分版";display:block;padding:8px 14px;margin:0 0 4px;font-size:16px;font-weight:700;background:#eef6ff;color:#1971c2;border-radius:8px 8px 0 0}#t-exam::before{content:"🎯 考场版";display:block;padding:8px 14px;margin:0 0 4px;font-size:16px;font-weight:700;background:#e9f9ef;color:#2b8a3e;border-radius:8px 8px 0 0}#t-life::before{content:"🛟 救急版";display:block;padding:8px 14px;margin:0 0 4px;font-size:16px;font-weight:700;background:#ffecec;color:#c92a2a;border-radius:8px 8px 0 0}.k-gold{font-size:18px!important;line-height:2.1!important}.k-gold p,.k-gold ol,.k-gold li{font-size:18px!important;line-height:2.1!important}'
    inject = '<style>' + css + '</style>'
    content = content.replace('</head>', inject + '</head>')

    # 插入标题栏
    header_html = '<div style="background:linear-gradient(135deg,#e5487c,#8a4bd8);color:#fff;border-radius:14px;padding:16px;text-align:center;font-size:22px;font-weight:700;margin-bottom:16px">' + year_short + ' · ' + q_label + '</div>'
    content = content.replace('<body>', '<body>' + header_html)

    # 写临时文件
    tmp = tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w')
    tmp.write(content)
    tmp.close()

    # Chrome截图
    qnum = os.path.basename(filepath).replace('.html', '')
    outname = year_short + '_' + qnum + '.png'
    outpath = os.path.join(output_dir, outname)

    subprocess.run([
        CHROME, '--headless=new', '--disable-gpu',
        '--force-device-scale-factor=2', '--window-size=750,20000',
        '--screenshot=' + outpath, '--hide-scrollbars',
        '--virtual-time-budget=2000', 'file://' + tmp.name
    ], capture_output=True, timeout=30)
    os.unlink(tmp.name)

    # 裁剪空白
    img = Image.open(outpath)
    w, h = img.size
    bg = (242, 243, 247)
    pixels = img.load()
    last_content = h
    for y in range(h-1, -1, -1):
        found = False
        for x in range(0, min(w, 300), 5):
            r, g, b = pixels[x, y][:3]
            if abs(r-bg[0])>8 or abs(g-bg[1])>8 or abs(b-bg[2])>8:
                found = True; break
        if found:
            last_content = min(y + 40, h)
            break
    img = img.crop((0, 0, w, last_content))
    if img.size[0] > 760:
        ratio = 750 / img.size[0]
        img = img.resize((750, int(img.size[1]*ratio)), Image.LANCZOS)
    img.save(outpath, "PNG")
    print(f"  {outname} ({img.size[0]}x{img.size[1]})")
    return outpath

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    write_css()

    years = [
        ("2025上", "2025上"),
        ("2024下", "2024下"),
        ("2024上", "2024上"),
        ("2023下", "2023下"),
        ("2023上", "2023上"),
        ("2022下", "2022下"),
        ("2022上", "2022上"),
        ("2021下", "2021下"),
        ("2021上", "2021上"),
        ("2020下", "2020下"),
    ]

    questions = [
        ("q12.html", "第12题·简答题"),
        ("q13.html", "第13题·简答题"),
        ("q15.html", "第15题·论述题"),
        ("q16.html", "第16题·案例分析"),
        ("q17.html", "第17题·教学设计"),
    ]

    for dirname, year_short in years:
        year_dir = os.path.join(BASE, dirname)
        if not os.path.exists(year_dir):
            continue
        print(f"=== {year_short} ===")
        for qfile, q_label in questions:
            filepath = os.path.join(year_dir, qfile)
            if os.path.exists(filepath):
                process_file(filepath, year_short, q_label, OUTPUT_DIR)

    print(f"\n全部完成！共 {len(os.listdir(OUTPUT_DIR))} 个文件")
    print(f"输出目录: {OUTPUT_DIR}")
