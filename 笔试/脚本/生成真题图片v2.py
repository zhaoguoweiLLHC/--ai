#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教资真题答案图片生成器 v3（手机友好版）
750px宽、大字号、每题拆成单张图
"""
from PIL import Image, ImageDraw, ImageFont
import os, re, html

# ============ 配置（手机友好） ============
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_REG  = "/System/Library/Fonts/STHeiti Light.ttc"

W = 750        # 手机屏宽
PAD = 24       # 边距缩小
LINE_SPACING = 8  # 行间距加大

C_BG = (242, 243, 247)
C_HEADER_BG = (229, 72, 124)
C_WHITE = (255, 255, 255)
C_INK = (43, 43, 51)
C_GRAY = (138, 143, 152)
C_PINK = (229, 72, 124)
C_BLUE = (43, 125, 233)
C_GREEN = (43, 138, 62)
C_RED = (201, 42, 42)
C_GOLD = (178, 106, 0)

C_FULL_BG = (238, 246, 255); C_FULL_BD = (182, 214, 247)
C_EXAM_BG = (233, 249, 239); C_EXAM_BD = (178, 226, 197)
C_LIFE_BG = (255, 236, 236); C_LIFE_BD = (255, 201, 201)

C_LUN = (229, 72, 124); C_AN = (240, 140, 0); C_SHE = (12, 166, 120)

# 字号（全面加大）
FS_HEADER = 24    # 标题栏
FS_SECTION = 20   # 题型标题
FS_TITLE = 18     # 题目标题
FS_BADGE = 13     # 徽章
FS_SCORE = 14     # 分值
FS_ORIGIN = 16    # 原题
FS_TIER_LABEL = 15 # 档位标签
FS_META = 12      # 档位meta
FS_BODY = 18      # 正文（核心加大）
FS_TIPS = 16      # 技巧
FS_TIPS_TITLE = 17 # 技巧标题

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def text_size(draw, text, f):
    bbox = draw.textbbox((0,0), text, font=f)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]

def wrap_text(text, draw, f, max_w):
    lines = []
    cur = ""
    for ch in text:
        test = cur + ch
        w = text_size(draw, test, f)[0]
        if w > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines

# ============ HTML解析 ============
def strip_tags(text):
    """去除HTML标签，保留纯文本"""
    # 先处理<br>和<br/>
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    # 处理block级标签换行
    text = re.sub(r'</?(p|div|li|ul|ol|h[1-6]|details|summary)[^>]*>', '\n', text, flags=re.I)
    # 去除所有剩余标签
    text = re.sub(r'<[^>]+>', '', text)
    # HTML实体
    text = html.unescape(text)
    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 清理行首多余空白和孤立符号
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        # 去掉孤立的 > < 符号
        if line in ('>', '<', ''):
            if not cleaned or cleaned[-1] != '':
                cleaned.append('')
            continue
        # 去掉链接引导文字（📐查看...→ 这种）
        if line.startswith('📐') or line.startswith('🧭'):
            continue
        cleaned.append(line)
    text = '\n'.join(cleaned)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_from_html(filepath):
    """从HTML文件提取题目标题、原题、三档答案、得分技巧"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'title': '', 'origin': '', 'score': '',
        'badge': '', 'badge_color': C_LUN,
        'tiers': [], 'tips': '',
        'section': '', 'section_color': C_LUN
    }

    # 判断题型
    if 'b-lun' in content:
        result['badge'] = '论述题'; result['badge_color'] = C_LUN; result['section'] = '四、论述题'; result['section_color'] = C_LUN
    elif 'b-an' in content:
        result['badge'] = '案例分析'; result['badge_color'] = C_AN; result['section'] = '五、案例分析'; result['section_color'] = C_AN
    elif 'b-she' in content:
        result['badge'] = '教学设计'; result['badge_color'] = C_SHE; result['section'] = '六、教学设计'; result['section_color'] = C_SHE

    # 提取标题
    m = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.S)
    if m:
        result['title'] = strip_tags(m.group(1))

    # 提取分值
    m = re.search(r'class="score"[^>]*>(.*?)</span>', content, re.S)
    if m:
        result['score'] = strip_tags(m.group(1))

    # 提取原题
    m = re.search(r'class="origin"[^>]*>(.*?)</div>', content, re.S)
    if m:
        result['origin'] = strip_tags(m.group(1))

    # 提取三档答案
    tier_configs = [
        ('t-full', '🏆 满分版', C_BLUE, C_FULL_BG, C_FULL_BD),
        ('t-exam', '🎯 考场版', C_GREEN, C_EXAM_BG, C_EXAM_BD),
        ('t-life', '🛟 救急版', C_RED, C_LIFE_BG, C_LIFE_BD),
    ]
    for i, (tid, label, color, bg, bd) in enumerate(tier_configs):
        # 找tab按钮提取meta
        meta = ''
        pattern = r'data-tab="' + tid + r'"[^>]*>(.*?)</button>'
        m = re.search(pattern, content, re.S)
        if m:
            meta = strip_tags(m.group(1)).replace(label, '').strip()

        # 找content内容：定位 id="tid" 后面的内容
        start_m = re.search(r'id="' + tid + r'"', content)
        if not start_m:
            continue
        start_pos = start_m.end()
        remaining = content[start_pos:]
        # 找到下一个 tab-content div 或 k-gold block 或 </section>
        # 注意k-gold可能以 <div class="block k-gold"> 或 class="k-gold" 出现
        next_m = re.search(r'<div class="tab-content|<div class="block k-gold"|class="k-gold"|</section>', remaining)
        if next_m:
            block_text = remaining[:next_m.start()]
        else:
            block_text = remaining[:5000]  # 兜底

        text = strip_tags(block_text)
        if '待生成' in text:
            text = '（待生成）'
        result['tiers'].append({
            'label': label, 'color': color, 'bg': bg, 'bd': bd,
            'meta': meta, 'text': text
        })

    # 提取得分技巧
    pattern = r'class="k-gold"[^>]*>.*?<ul class="tips"[^>]*>(.*?)</ul>'
    m = re.search(pattern, content, re.S)
    if m:
        result['tips'] = strip_tags(m.group(1))
    else:
        # 尝试另一种结构
        pattern = r'class="k-gold"[^>]*>.*?<h3>.*?</h3>(.*?)</div>'
        m = re.search(pattern, content, re.S)
        if m:
            t = strip_tags(m.group(1))
            if '待生成' not in t:
                result['tips'] = t

    return result

# ============ 绘图 ============
class Canvas:
    def __init__(self):
        self.items = []
        self.h = 0
    def reserve(self, h):
        start = self.h
        self.h += h
        return start
    def finalize(self):
        self.img = Image.new("RGB", (W, self.h + PAD), C_BG)
        self.draw = ImageDraw.Draw(self.img)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_header(canvas, year_text, q_label=""):
    h = 80
    y = canvas.reserve(h)
    def _draw(d):
        draw_rounded_rect(d, [PAD, y+8, W-PAD, y+h-8], 14, C_HEADER_BG)
        f = font(FS_HEADER, True)
        text = year_text
        if q_label:
            text = f"{year_text} · {q_label}"
        tw, th = text_size(d, text, f)
        d.text(((W-tw)//2, y+8+(h-16-th)//2), text, fill=C_WHITE, font=f)
    canvas.items.append(_draw)

def draw_section_title(canvas, text, color):
    h = 44
    y = canvas.reserve(h)
    def _draw(d):
        f = font(FS_SECTION, True)
        d.text((PAD+8, y+10), text, fill=color, font=f)
    canvas.items.append(_draw)

def draw_question_card(canvas, badge_text, badge_color, title, score, origin_text):
    f_title = font(FS_TITLE, True); f_badge = font(FS_BADGE, True); f_score = font(FS_SCORE, True); f_origin = font(FS_ORIGIN, False)
    max_w = W - 2*PAD - 24
    tmp_d = ImageDraw.Draw(Image.new("RGB",(1,1)))
    origin_lines = []
    for line in origin_text.split('\n'):
        origin_lines.extend(wrap_text(line, tmp_d, f_origin, max_w))
    h = 16 + 28 + max(1,len(origin_lines)) * (FS_ORIGIN + 10 + LINE_SPACING) + 12
    y = canvas.reserve(h)
    def _draw(d):
        draw_rounded_rect(d, [PAD, y, W-PAD, y+h-4], 14, C_WHITE)
        bw, bh = text_size(d, badge_text, f_badge)
        draw_rounded_rect(d, [PAD+12, y+10, PAD+12+bw+20, y+10+bh+6], 7, badge_color)
        d.text((PAD+12+10, y+10+3), badge_text, fill=C_WHITE, font=f_badge)
        d.text((PAD+12+bw+20+8, y+10+3), title, fill=C_INK, font=f_title)
        sw, sh = text_size(d, score, f_score)
        d.text((W-PAD-12-sw, y+10+5), score, fill=C_PINK, font=f_score)
        oy = y + 10 + bh + 10
        for line in origin_lines:
            d.text((PAD+14, oy), line, fill=(85,85,85), font=f_origin)
            oy += FS_ORIGIN + 10 + LINE_SPACING
    canvas.items.append(_draw)

def draw_tier(canvas, tier_label, tier_color, tier_bg, tier_bd, tier_meta, answer_text):
    f_label = font(FS_TIER_LABEL, True); f_meta = font(FS_META, False); f_body = font(FS_BODY, False)
    max_w = W - 2*PAD - 28
    tmp_d = ImageDraw.Draw(Image.new("RGB",(1,1)))
    answer_lines = []
    for line in answer_text.split('\n'):
        if line.strip() == '':
            answer_lines.append('')
        else:
            answer_lines.extend(wrap_text(line, tmp_d, f_body, max_w))
    h = 10 + 22 + max(1,len(answer_lines)) * (FS_BODY + 10 + LINE_SPACING) + 10
    y = canvas.reserve(h)
    def _draw(d):
        draw_rounded_rect(d, [PAD+6, y, W-PAD-6, y+h-4], 10, tier_bg, tier_bd, 1)
        d.text((PAD+14, y+7), tier_label, fill=tier_color, font=f_label)
        if tier_meta:
            mw, mh = text_size(d, tier_meta, f_meta)
            d.text((W-PAD-14-mw, y+8), tier_meta, fill=C_GRAY, font=f_meta)
        oy = y + 7 + 22
        for line in answer_lines:
            if line:
                d.text((PAD+16, oy), line, fill=C_INK, font=f_body)
            oy += FS_BODY + 10 + LINE_SPACING
    canvas.items.append(_draw)

def draw_tips(canvas, tips_text):
    f = font(FS_TIPS, False); f_title = font(FS_TIPS_TITLE, True)
    max_w = W - 2*PAD - 28
    tmp_d = ImageDraw.Draw(Image.new("RGB",(1,1)))
    lines = []
    for line in tips_text.split('\n'):
        if line.strip() == '':
            lines.append('')
        else:
            lines.extend(wrap_text(line, tmp_d, f, max_w))
    h = 10 + 22 + max(1,len(lines))*(FS_TIPS+8+LINE_SPACING) + 10
    y = canvas.reserve(h)
    def _draw(d):
        draw_rounded_rect(d, [PAD+6, y, W-PAD-6, y+h-4], 10, (255,247,224), (243,217,160), 1)
        d.text((PAD+14, y+7), "得分技巧", fill=C_GOLD, font=f_title)
        oy = y + 7 + 24
        for line in lines:
            if line:
                d.text((PAD+14, oy), line, fill=(90,80,50), font=f)
            oy += FS_TIPS + 8 + LINE_SPACING
    canvas.items.append(_draw)

def draw_spacer(canvas, h=12):
    canvas.reserve(h)

def generate_year_images(year_label, year_dir, output_dir):
    """每题单独生成一张图"""
    qfiles = [
        ('q15.html', '第15题·论述题'),
        ('q16.html', '第16题·案例分析'),
        ('q17.html', '第17题·教学设计'),
    ]
    
    # 提取年份简称用于文件名
    year_short = year_label.replace('年', '').replace('上半', '上').replace('下半', '下').replace('期', '')
    
    generated = []
    for qfile, q_label in qfiles:
        filepath = os.path.join(year_dir, qfile)
        if not os.path.exists(filepath):
            continue
        q = extract_from_html(filepath)
        if not q['title']:
            continue

        canvas = Canvas()
        draw_header(canvas, year_short, q_label)
        draw_spacer(canvas, 6)

        draw_section_title(canvas, q['section'], q['section_color'])
        draw_question_card(canvas, q['badge'], q['badge_color'], q['title'], q['score'], q['origin'])
        draw_spacer(canvas, 4)

        for tier in q['tiers']:
            draw_tier(canvas, tier['label'], tier['color'], tier['bg'], tier['bd'], tier['meta'], tier['text'])
            draw_spacer(canvas, 3)

        if q['tips']:
            draw_tips(canvas, q['tips'])
        draw_spacer(canvas, 10)

        canvas.finalize()
        for item in canvas.items:
            item(canvas.draw)
        
        # 文件名：年份_题号.png
        qnum = qfile.replace('.html', '')
        outname = f"{year_short}_{qnum}.png"
        outpath = os.path.join(output_dir, outname)
        canvas.img.save(outpath, "PNG")
        generated.append(outpath)
        print(f"  {outname} ({canvas.img.size[0]}x{canvas.img.size[1]})")
    
    return generated

# ============ 主程序 ============
if __name__ == "__main__":
    base = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
    output_dir = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/答案图片合集"
    os.makedirs(output_dir, exist_ok=True)

    years = [
        ("2025上半年", "2025上"),
        ("2024下半年", "2024下"),
        ("2024上半年", "2024上"),
        ("2023下半年", "2023下"),
        ("2023上半年", "2023上"),
        ("2022下半年", "2022下"),
        ("2022上半年", "2022上"),
        ("2021下半年", "2021下"),
        ("2021上半年", "2021上"),
        ("2020下半年", "2020下"),
    ]

    for label, dirname in years:
        year_dir = os.path.join(base, dirname)
        print(f"=== {label} ===")
        generate_year_images(label, year_dir, output_dir)

    print("\n全部完成！")
    print(f"输出目录: {output_dir}")
    print(f"共 {len(os.listdir(output_dir))} 个文件")
