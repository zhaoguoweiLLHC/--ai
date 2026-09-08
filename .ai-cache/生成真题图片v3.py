#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教资真题答案图片生成器 v3（手机友好·精确提取版）
750px宽、大字号、每题拆成单张图
"""
from PIL import Image, ImageDraw, ImageFont
import os, re, html

# ============ 配置 ============
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_REG  = "/System/Library/Fonts/STHeiti Light.ttc"

W = 750; PAD = 24; LINE_SPACING = 8

C_BG=(242,243,247); C_HEADER_BG=(229,72,124); C_WHITE=(255,255,255)
C_INK=(43,43,51); C_GRAY=(138,143,152); C_PINK=(229,72,124)
C_BLUE=(43,125,233); C_GREEN=(43,138,62); C_RED=(201,42,42); C_GOLD=(178,106,0)
C_FULL_BG=(238,246,255); C_FULL_BD=(182,214,247)
C_EXAM_BG=(233,249,239); C_EXAM_BD=(178,226,197)
C_LIFE_BG=(255,236,236); C_LIFE_BD=(255,201,201)
C_LUN=(229,72,124); C_AN=(240,140,0); C_SHE=(12,166,120)

FS_HEADER=24; FS_SECTION=20; FS_TITLE=18; FS_BADGE=13; FS_SCORE=14
FS_ORIGIN=16; FS_TIER_LABEL=15; FS_META=12; FS_BODY=18; FS_TIPS=16; FS_TIPS_TITLE=17

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def text_size(draw, text, f):
    bbox = draw.textbbox((0,0), text, font=f)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]

def wrap_text(text, draw, f, max_w):
    lines = []; cur = ""
    for ch in text:
        test = cur + ch
        if text_size(draw, test, f)[0] > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

# ============ HTML解析 ============
def strip_tags(text):
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</?(p|div|li|ul|ol|h[1-6]|details|summary)[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    lines = [l.strip() for l in text.split('\n')]
    out = []
    for l in lines:
        if l in ('>', '<', ''):
            if not out or out[-1] != '': out.append('')
            continue
        if l.startswith('📐') or l.startswith('🧭'): continue
        out.append(l)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()

def find_block_content(content, class_name):
    """用div计数法精确提取 <div class="block xxx"> 到对应 </div> 的内容"""
    start_m = re.search(r'<div class="block ' + class_name + r'"[^>]*>', content)
    if not start_m:
        return ''
    pos = start_m.end()
    depth = 1  # 已经进入了一个div
    while depth > 0 and pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return content[start_m.end():next_close]
            pos = next_close + 6
    return content[start_m.end():pos]

def extract_from_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {'title':'', 'origin':'', 'score':'', 'badge':'', 'badge_color':C_LUN,
              'tiers':[], 'tips':'', 'section':'', 'section_color':C_LUN}

    # 题型
    if 'b-lun' in content:
        result['badge']='论述题'; result['badge_color']=C_LUN; result['section']='四、论述题'; result['section_color']=C_LUN
    elif 'b-an' in content:
        result['badge']='案例分析'; result['badge_color']=C_AN; result['section']='五、案例分析'; result['section_color']=C_AN
    elif 'b-she' in content:
        result['badge']='教学设计'; result['badge_color']=C_SHE; result['section']='六、教学设计'; result['section_color']=C_SHE

    # 标题
    m = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.S)
    if m: result['title'] = strip_tags(m.group(1))

    # 分值
    m = re.search(r'class="score"[^>]*>(.*?)</span>', content, re.S)
    if m: result['score'] = strip_tags(m.group(1))

    # 原题
    m = re.search(r'class="origin"[^>]*>(.*?)</div>', content, re.S)
    if m: result['origin'] = strip_tags(m.group(1))

    # 三档答案：用div计数法精确提取
    tier_configs = [
        ('t-full', '🏆 满分版', C_BLUE, C_FULL_BG, C_FULL_BD),
        ('t-exam', '🎯 考场版', C_GREEN, C_EXAM_BG, C_EXAM_BD),
        ('t-life', '🛟 救急版', C_RED, C_LIFE_BG, C_LIFE_BD),
    ]
    for tid, label, color, bg, bd in tier_configs:
        # meta
        meta = ''
        m = re.search(r'data-tab="' + tid + r'"[^>]*>(.*?)</button>', content, re.S)
        if m: meta = strip_tags(m.group(1)).replace(label, '').strip()

        # 用div计数法提取block内容
        block_html = find_block_content(content, tid)
        text = strip_tags(block_html)
        if '待生成' in text:
            text = '（待生成）'
        result['tiers'].append({
            'label': label, 'color': color, 'bg': bg, 'bd': bd,
            'meta': meta, 'text': text
        })

    # 得分技巧：同样用div计数法
    tips_html = find_block_content(content, 'k-gold')
    if tips_html:
        # 提取<ul class="tips">内容
        tips_m = re.search(r'<ul class="tips"[^>]*>(.*?)</ul>', tips_html, re.S)
        if tips_m:
            result['tips'] = strip_tags(tips_m.group(1))
        else:
            t = strip_tags(tips_html)
            if '待生成' not in t and t:
                result['tips'] = t

    return result

# ============ 绘图 ============
class Canvas:
    def __init__(self):
        self.items = []; self.h = 0
    def reserve(self, h):
        s = self.h; self.h += h; return s
    def finalize(self):
        self.img = Image.new("RGB", (W, self.h + PAD), C_BG)
        self.draw = ImageDraw.Draw(self.img)

def rrect(d, xy, r, fill, outline=None, w=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)

def draw_header(canvas, year_text, q_label=""):
    h = 80; y = canvas.reserve(h)
    def _d(d):
        rrect(d, [PAD, y+8, W-PAD, y+h-8], 14, C_HEADER_BG)
        f = font(FS_HEADER, True)
        text = f"{year_text} · {q_label}" if q_label else year_text
        tw, th = text_size(d, text, f)
        d.text(((W-tw)//2, y+8+(h-16-th)//2), text, fill=C_WHITE, font=f)
    canvas.items.append(_d)

def draw_section_title(canvas, text, color):
    h = 44; y = canvas.reserve(h)
    def _d(d):
        d.text((PAD+8, y+10), text, fill=color, font=font(FS_SECTION, True))
    canvas.items.append(_d)

def draw_question_card(canvas, badge, badge_color, title, score, origin):
    f_t=font(FS_TITLE,True); f_b=font(FS_BADGE,True); f_s=font(FS_SCORE,True); f_o=font(FS_ORIGIN,False)
    max_w = W-2*PAD-24; tmp=ImageDraw.Draw(Image.new("RGB",(1,1)))
    ol=[]
    for line in origin.split('\n'): ol.extend(wrap_text(line, tmp, f_o, max_w))
    h=16+28+max(1,len(ol))*(FS_ORIGIN+10+LINE_SPACING)+12; y=canvas.reserve(h)
    def _d(d):
        rrect(d,[PAD,y,W-PAD,y+h-4],14,C_WHITE)
        bw,bh=text_size(d,badge,f_b)
        rrect(d,[PAD+12,y+10,PAD+12+bw+20,y+10+bh+6],7,badge_color)
        d.text((PAD+22,y+13),badge,fill=C_WHITE,font=f_b)
        d.text((PAD+12+bw+20+8,y+13),title,fill=C_INK,font=f_t)
        sw,_=text_size(d,score,f_s)
        d.text((W-PAD-12-sw,y+15),score,fill=C_PINK,font=f_s)
        oy=y+10+bh+10
        for line in ol:
            d.text((PAD+14,oy),line,fill=(85,85,85),font=f_o)
            oy+=FS_ORIGIN+10+LINE_SPACING
    canvas.items.append(_d)

def draw_tier(canvas, label, color, bg, bd, meta, text):
    f_l=font(FS_TIER_LABEL,True); f_m=font(FS_META,False); f_b=font(FS_BODY,False)
    max_w=W-2*PAD-28; tmp=ImageDraw.Draw(Image.new("RGB",(1,1)))
    al=[]
    for line in text.split('\n'):
        if line.strip()=='': al.append('')
        else: al.extend(wrap_text(line, tmp, f_b, max_w))
    h=10+22+max(1,len(al))*(FS_BODY+10+LINE_SPACING)+10; y=canvas.reserve(h)
    def _d(d):
        rrect(d,[PAD+6,y,W-PAD-6,y+h-4],10,bg,bd,1)
        d.text((PAD+14,y+7),label,fill=color,font=f_l)
        if meta:
            mw,_=text_size(d,meta,f_m)
            d.text((W-PAD-14-mw,y+8),meta,fill=C_GRAY,font=f_m)
        oy=y+7+22
        for line in al:
            if line: d.text((PAD+16,oy),line,fill=C_INK,font=f_b)
            oy+=FS_BODY+10+LINE_SPACING
    canvas.items.append(_d)

def draw_tips(canvas, text):
    f=font(FS_TIPS,False); f_t=font(FS_TIPS_TITLE,True)
    max_w=W-2*PAD-28; tmp=ImageDraw.Draw(Image.new("RGB",(1,1)))
    lines=[]
    for line in text.split('\n'):
        if line.strip()=='': lines.append('')
        else: lines.extend(wrap_text(line, tmp, f, max_w))
    h=10+22+max(1,len(lines))*(FS_TIPS+8+LINE_SPACING)+10; y=canvas.reserve(h)
    def _d(d):
        rrect(d,[PAD+6,y,W-PAD-6,y+h-4],10,(255,247,224),(243,217,160),1)
        d.text((PAD+14,y+7),"得分技巧",fill=C_GOLD,font=f_t)
        oy=y+7+24
        for line in lines:
            if line: d.text((PAD+14,oy),line,fill=(90,80,50),font=f)
            oy+=FS_TIPS+8+LINE_SPACING
    canvas.items.append(_d)

def spacer(c, h=12): c.reserve(h)

def generate_one(year_label, year_dir, output_dir, qfile, q_label):
    filepath = os.path.join(year_dir, qfile)
    if not os.path.exists(filepath): return None
    q = extract_from_html(filepath)
    if not q['title']: return None

    year_short = year_label.replace('年','').replace('上半','上').replace('下半','下').replace('期','')
    canvas = Canvas()
    draw_header(canvas, year_short, q_label); spacer(canvas, 6)
    draw_section_title(canvas, q['section'], q['section_color'])
    draw_question_card(canvas, q['badge'], q['badge_color'], q['title'], q['score'], q['origin'])
    spacer(canvas, 4)
    for tier in q['tiers']:
        draw_tier(canvas, tier['label'], tier['color'], tier['bg'], tier['bd'], tier['meta'], tier['text'])
        spacer(canvas, 3)
    if q['tips']:
        draw_tips(canvas, q['tips'])
    spacer(canvas, 10)

    canvas.finalize()
    for item in canvas.items: item(canvas.draw)
    qnum = qfile.replace('.html','')
    outname = f"{year_short}_{qnum}.png"
    outpath = os.path.join(output_dir, outname)
    canvas.img.save(outpath, "PNG")
    print(f"  {outname} ({canvas.img.size[0]}x{canvas.img.size[1]})")
    return outpath

# ============ 主程序 ============
if __name__ == "__main__":
    base = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"
    output_dir = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/答案图片合集"
    os.makedirs(output_dir, exist_ok=True)

    # 先只生成 2025上 q17
    generate_one("2025上半年", os.path.join(base, "2025上"), output_dir, "q17.html", "第17题·教学设计")
