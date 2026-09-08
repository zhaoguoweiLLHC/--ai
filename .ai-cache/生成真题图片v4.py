#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教资真题答案图片生成器 v4（Chrome截图版）
直接从原始HTML页面提取DOM节点，用Chrome headless渲染截图
"""
import subprocess, os, re, html, tempfile, time

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
OUTPUT_DIR = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/答案图片合集"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# CSS模板——手机友好
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:750px;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f2f3f7;color:#2b2b33;line-height:2;font-size:18px;padding:20px}
.header{background:linear-gradient(135deg,#e5487c,#8a4bd8);color:#fff;border-radius:14px;padding:16px;text-align:center;font-size:22px;font-weight:700;margin-bottom:16px}
.section-title{font-size:20px;font-weight:700;margin:14px 0 8px}
.q-card{background:#fff;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 6px rgba(0,0,0,.06)}
.q-card .badge{display:inline-block;color:#fff;border-radius:6px;padding:2px 10px;font-size:13px;font-weight:600}
.q-card .qtitle{font-size:17px;font-weight:700;margin:8px 0 4px}
.q-card .origin{font-size:15px;color:#666;white-space:pre-line;line-height:1.8}
.tier{border-radius:10px;padding:14px;margin:8px 0;border:1px solid}
.tier .tlabel{font-size:15px;font-weight:700;margin-bottom:8px}
.tier .tmeta{font-size:12px;color:#888;font-weight:400;float:right;margin-top:3px}
.tier .tbody{font-size:18px;white-space:pre-line;line-height:2.1}
.tier .tbody b{font-weight:700}
.t-full{background:#eef6ff;border-color:#b6d6f7}.t-full .tlabel{color:#1971c2}
.t-exam{background:#e9f9ef;border-color:#b2e2c5}.t-exam .tlabel{color:#2b8a3e}
.t-life{background:#ffecec;border-color:#ffc9c9}.t-life .tlabel{color:#c92a2a}
.tips{background:#fff7e0;border:1px solid #f3d9a0;border-radius:10px;padding:14px;margin:8px 0}
.tips .tips-title{font-size:16px;font-weight:700;color:#b26a00;margin-bottom:8px}
.tips .tips-body{font-size:16px;color:#5a5032;white-space:pre-line;line-height:1.9}
"""

def strip_tags_keep_b(text):
    """去所有HTML标签，输出纯文本（已转义）"""
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</?(p|div|li|ul|ol|h[1-6]|details|summary|span|a|mark)[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)  # 去所有剩余标签
    text = html.unescape(text)  # 解码实体
    # 再转义，防止文本中的 < > & 被HTML解析
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    lines = [l.strip() for l in text.split('\n')]
    out = []
    for l in lines:
        if l == '':
            if not out or out[-1] != '': out.append('')
            continue
        if l.startswith('📐') or l.startswith('🧭'): continue
        out.append(l)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()

def find_block_content(content, class_name):
    """用div计数法精确提取block内容（保留内部HTML标签）"""
    start_m = re.search(r'<div class="block ' + class_name + r'"[^>]*>', content)
    if not start_m: return ''
    pos = start_m.end(); depth = 1
    while depth > 0 and pos < len(content):
        no = content.find('<div', pos); nc = content.find('</div>', pos)
        if nc == -1: break
        if no != -1 and no < nc: depth += 1; pos = no + 4
        else:
            depth -= 1
            if depth == 0: return content[start_m.end():nc]
            pos = nc + 6
    return content[start_m.end():pos]

def extract_question(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    q = {'section':'', 'section_color':'', 'badge':'', 'badge_color':'', 'title':'', 'score':'', 'origin':'', 'tiers':[], 'tips':''}

    if 'b-lun' in content:
        q['section']='四、论述题'; q['section_color']='#e5487c'; q['badge']='论述题'; q['badge_color']='#e5487c'
    elif 'b-an' in content:
        q['section']='五、案例分析'; q['section_color']='#f08c00'; q['badge']='案例分析'; q['badge_color']='#f08c00'
    elif 'b-she' in content:
        q['section']='六、教学设计'; q['section_color']='#0ca678'; q['badge']='教学设计'; q['badge_color']='#0ca678'

    m = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.S)
    if m: q['title'] = strip_tags_keep_b(m.group(1))

    m = re.search(r'class="score"[^>]*>(.*?)</span>', content, re.S)
    if m: q['score'] = strip_tags_keep_b(m.group(1))

    m = re.search(r'class="origin"[^>]*>(.*?)</div>', content, re.S)
    if m: q['origin'] = strip_tags_keep_b(m.group(1))

    tier_configs = [
        ('t-full', '🏆 满分版', '#1971c2'),
        ('t-exam', '🎯 考场版', '#2b8a3e'),
        ('t-life', '🛟 救急版', '#c92a2a'),
    ]
    for tid, label, color in tier_configs:
        meta = ''
        m = re.search(r'data-tab="' + tid + r'"[^>]*>(.*?)</button>', content, re.S)
        if m: meta = strip_tags_keep_b(m.group(1)).replace(label, '').strip()

        block_html = find_block_content(content, tid)
        text = strip_tags_keep_b(block_html)
        if '待生成' in text: text = '（待生成）'
        q['tiers'].append({'label': label, 'color': color, 'meta': meta, 'text': text})

    tips_html = find_block_content(content, 'k-gold')
    if tips_html:
        tips_m = re.search(r'<ul class="tips"[^>]*>(.*?)</ul>', tips_html, re.S)
        if tips_m:
            q['tips'] = strip_tags_keep_b(tips_m.group(1))

    return q

def build_html(year_label, q_label, q):
    """构建截图用的HTML"""
    html_parts = [f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>{CSS}</style></head><body>']
    html_parts.append(f'<div class="header">{year_label} · {q_label}</div>')
    html_parts.append(f'<div class="section-title" style="color:{q["section_color"]}">{q["section"]}</div>')

    badge = q['badge']
    html_parts.append(f'<div class="q-card"><span class="badge" style="background:{q["badge_color"]}">{badge}</span>')
    html_parts.append(f'<div class="qtitle">{q["title"]}</div>')
    html_parts.append(f'<div class="origin">{q["origin"]}</div></div>')

    tier_classes = {'🏆 满分版':'t-full', '🎯 考场版':'t-exam', '🛟 救急版':'t-life'}
    for tier in q['tiers']:
        cls = tier_classes.get(tier['label'], 't-full')
        html_parts.append(f'<div class="tier {cls}"><div class="tlabel">{tier["label"]}')
        if tier['meta']:
            html_parts.append(f'<span class="tmeta">{tier["meta"]}</span>')
        html_parts.append(f'</div><div class="tbody">{tier["text"]}</div></div>')

    if q['tips']:
        html_parts.append(f'<div class="tips"><div class="tips-title">💡 得分技巧</div><div class="tips-body">{q["tips"]}</div></div>')

    html_parts.append('</body></html>')
    return '\n'.join(html_parts)

def screenshot(html_content, output_path):
    """用Chrome headless截图——先获取页面高度，再设window-size截图"""
    from PIL import Image

    # 在HTML中加JS计算高度
    html_with_js = html_content.replace('</body>', '''
<script>
document.title = document.body.scrollHeight;
</script>
</body>''')

    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(html_with_js)
        tmp_html = f.name

    # 用Chrome的--dump-dom获取计算后的高度
    # 先用一个大的window跑一次，然后裁剪
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
        for x in range(0, min(w, 200), 5):
            r, g, b = pixels[x, y][:3]
            if abs(r-bg[0])>8 or abs(g-bg[1])>8 or abs(b-bg[2])>8:
                found = True; break
        if found:
            last_content = min(y + 40, h)
            break

    img = img.crop((0, 0, w, last_content))
    # 缩小回750宽（scale factor=2所以实际是1500宽）
    if img.size[0] > 760:
        ratio = 750 / img.size[0]
        img = img.resize((750, int(img.size[1]*ratio)), Image.LANCZOS)
    img.save(output_path, "PNG")
    return img.size

def generate_one(year_label, year_dir, qfile, q_label):
    filepath = os.path.join(year_dir, qfile)
    if not os.path.exists(filepath): return None
    q = extract_question(filepath)
    if not q['title']: return None

    year_short = year_label.replace('年','').replace('上半','上').replace('下半','下').replace('期','')
    html_content = build_html(year_short, q_label, q)

    qnum = qfile.replace('.html','')
    outname = f"{year_short}_{qnum}.png"
    outpath = os.path.join(OUTPUT_DIR, outname)
    size = screenshot(html_content, outpath)
    print(f"  {outname} ({size[0]}x{size[1]})")
    return outpath

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 先只生成2025上q17
    generate_one("2025上半年", os.path.join(BASE, "2025上"), "q17.html", "第17题·教学设计")
