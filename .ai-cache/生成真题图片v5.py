#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教资真题答案图片生成器 v5（Chrome直接截图原始HTML）
方案：给原始HTML注入CSS，隐藏推导区/返回链接/脚本等，
      只显示题干+三档答案+得分技巧，然后Chrome截图
"""
import subprocess, os, re, tempfile
from PIL import Image

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
OUTPUT_DIR = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/答案图片合集"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 注入到原始HTML的CSS——隐藏不需要的元素 + 手机友好排版
INJECT_CSS = '<style>.back-link{display:none!important}details{display:none!important}footer{display:none!important}.k-gold{display:none!important}.k-bibei{display:none!important}.tab-content{display:block!important}.tabs{display:none!important}body{width:750px!important;max-width:750px!important;margin:0 auto!important;padding:20px!important;font-size:18px!important;line-height:2!important;background:#f2f3f7!important;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif!important}.wrap{max-width:none!important;padding:0!important}section.card{padding:16px!important;margin-bottom:12px!important}.origin{font-size:16px!important}.tab-content .block{padding:14px!important;margin:4px 0 12px!important;font-size:18px!important;line-height:2.1!important}.tab-content .block p,.tab-content .block ul,.tab-content .block ol,.tab-content .block li{font-size:18px!important;line-height:2.1!important}.tab-content .block li{margin:6px 0!important}header.top{display:none!important}.tier-label{display:block;padding:8px 14px;margin:8px 0 2px;font-size:16px;font-weight:700;border-radius:8px 8px 0 0}.tier-label-full{background:#eef6ff;color:#1971c2}.tier-label-exam{background:#e9f9ef;color:#2b8a3e}.tier-label-life{background:#ffecec;color:#c92a2a}</style>'

def screenshot_html(html_content, output_path):
    """用Chrome headless截图"""
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(html_content)
        tmp_html = f.name

    cmd = [
        CHROME,
        '--headless=new',
        '--disable-gpu',
        '--force-device-scale-factor=2',
        '--window-size=750,20000',
        f'--screenshot={output_path}',
        '--hide-scrollbars',
        '--virtual-time-budget=2000',
        f'file://{tmp_html}'
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    os.unlink(tmp_html)

    img = Image.open(output_path)
    w, h = img.size

    # 裁剪底部空白
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
    img.save(output_path, "PNG")
    return img.size

def process_file(filepath, year_short, q_label, output_dir):
    """处理单个HTML文件：注入CSS+档位标签 → 截图"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 在</head>前注入CSS
    if '</head>' in content:
        content = content.replace('</head>', INJECT_CSS + '\n</head>')
    else:
        content = INJECT_CSS + content

    # 在每个tab-content前插入档位标签
    tier_labels = {
        't-full': ('🏆 满分版', 'tier-label-full'),
        't-exam': ('🎯 考场版', 'tier-label-exam'),
        't-life': ('🛟 救急版', 'tier-label-life'),
    }
    for tid, (label_text, label_cls) in tier_labels.items():
        meta = ''
        m = re.search(r'data-tab="' + tid + r'"[^>]*>(.*?)</button>', content, re.S)
        if m:
            meta = re.sub(r'<[^>]+>', '', m.group(1)).replace(label_text, '').strip()

        label_html = f'<div class="tier-label {label_cls}">{label_text}'
        if meta:
            label_html += f' <small style="font-size:12px;color:#888;font-weight:400">{meta}</small>'
        label_html += '</div>\n'

        # 在 <div class="tab-content ... id="tid" ...> 前插入标签
        # 匹配 <div class="tab-content[^>]*id="tid"[^>]*>
        pattern = r'(<div class="tab-content[^>]*id="' + tid + r'"[^>]*>)'
        content = re.sub(pattern, label_html + r'\1', content, count=1)

    # 在<body>后插入标题栏
    header_html = f'<div style="background:linear-gradient(135deg,#e5487c,#8a4bd8);color:#fff;border-radius:14px;padding:16px;text-align:center;font-size:22px;font-weight:700;margin-bottom:16px">{year_short} · {q_label}</div>'
    if '<body>' in content:
        content = content.replace('<body>', '<body>' + header_html)
    elif '<body ' in content:
        content = re.sub(r'<body[^>]*>', lambda m: m.group(0) + header_html, content)

    # 输出
    qnum = os.path.basename(filepath).replace('.html', '')
    outname = f"{year_short}_{qnum}.png"
    outpath = os.path.join(output_dir, outname)
    size = screenshot_html(content, outpath)
    print(f"  {outname} ({size[0]}x{size[1]})")
    return outpath

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 先只生成2025上q17
    process_file(
        os.path.join(BASE, "2025上", "q17.html"),
        "2025上", "第17题·教学设计",
        OUTPUT_DIR
    )
