#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教资真题答案图片生成器
把每年三道主观题的三档答案绘制为一张PNG长图
"""
from PIL import Image, ImageDraw, ImageFont
import json, os, textwrap

# ============ 配置 ============
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_REG  = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"

W = 1080  # 图片宽度
PAD = 40  # 左右边距
LINE_SPACING = 6  # 行间距

# 颜色
C_BG = (242, 243, 247)
C_HEADER_BG = (229, 72, 124)
C_HEADER_BG2 = (138, 75, 216)
C_WHITE = (255, 255, 255)
C_INK = (43, 43, 51)
C_GRAY = (138, 143, 152)
C_PINK = (229, 72, 124)
C_BLUE = (43, 125, 233)
C_GREEN = (43, 138, 62)
C_RED = (201, 42, 42)
C_GOLD = (178, 106, 0)

# 档色
C_FULL_BG = (238, 246, 255)
C_FULL_BD = (182, 214, 247)
C_EXAM_BG = (233, 249, 239)
C_EXAM_BD = (178, 226, 197)
C_LIFE_BG = (255, 236, 236)
C_LIFE_BD = (255, 201, 201)

# 题型色
C_LUN = (229, 72, 124)
C_AN  = (240, 140, 0)
C_SHE = (12, 166, 120)

def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)

def text_size(draw, text, f):
    bbox = draw.textbbox((0,0), text, font=f)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]

def wrap_text(text, draw, f, max_w):
    """中文逐字换行"""
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

class Canvas:
    def __init__(self):
        self.items = []
        self.h = 0
    def add(self, h):
        self.h += h
    def reserve(self, h):
        start = self.h
        self.h += h
        return start
    def finalize(self):
        self.img = Image.new("RGB", (W, self.h + PAD), C_BG)
        self.draw = ImageDraw.Draw(self.img)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_header(canvas, year_text):
    """绘制顶部标题栏"""
    h = 100
    y = canvas.reserve(h)
    def _draw(img_draw):
        draw_rounded_rect(img_draw, [PAD, y+10, W-PAD, y+h-10], 16, None)
        # 渐变模拟：用纯色
        draw_rounded_rect(img_draw, [PAD, y+10, W-PAD, y+h-10], 16, C_HEADER_BG)
        f = font(28, True)
        tw, th = text_size(img_draw, year_text, f)
        img_draw.text(((W-tw)//2, y+10+(h-20-th)//2), year_text, fill=C_WHITE, font=f)
    canvas.items.append(_draw)

def draw_section_title(canvas, text, color):
    """绘制题型标题条"""
    h = 50
    y = canvas.reserve(h)
    def _draw(img_draw):
        f = font(22, True)
        img_draw.text((PAD+10, y+12), text, fill=color, font=f)
    canvas.items.append(_draw)

def draw_question_card(canvas, badge_text, badge_color, title, score, origin_text):
    """绘制题目卡片（题干+原题）"""
    f_title = font(19, True)
    f_badge = font(13, True)
    f_score = font(14, True)
    f_origin = font(15, False)
    max_w = W - 2*PAD - 32

    # 计算原题高度
    origin_lines = []
    for line in origin_text.split('\n'):
        origin_lines.extend(wrap_text(line, ImageDraw.Draw(Image.new("RGB",(1,1))), f_origin, max_w))
    
    h = 20 + 30 + len(origin_lines) * (22 + LINE_SPACING) + 16
    y = canvas.reserve(h)
    def _draw(img_draw):
        draw_rounded_rect(img_draw, [PAD, y, W-PAD, y+h-6], 16, C_WHITE)
        # badge
        bw, bh = text_size(img_draw, badge_text, f_badge)
        draw_rounded_rect(img_draw, [PAD+16, y+14, PAD+16+bw+24, y+14+bh+8], 8, badge_color)
        img_draw.text((PAD+16+12, y+14+4), badge_text, fill=C_WHITE, font=f_badge)
        # title
        img_draw.text((PAD+16+bw+24+10, y+14+4), title, fill=C_INK, font=f_title)
        # score
        sw, sh = text_size(img_draw, score, f_score)
        img_draw.text((W-PAD-16-sw, y+14+6), score, fill=C_PINK, font=f_score)
        # origin
        oy = y + 14 + bh + 14
        for line in origin_lines:
            img_draw.text((PAD+20, oy), line, fill=(85,85,85), font=f_origin)
            oy += 22 + LINE_SPACING
    canvas.items.append(_draw)

def draw_tier(canvas, tier_label, tier_color, tier_bg, tier_bd, tier_meta, answer_text):
    """绘制一档答案"""
    f_label = font(14, True)
    f_meta = font(11, False)
    f_body = font(15, False)
    max_w = W - 2*PAD - 40

    # 计算答案行数
    answer_lines = []
    for line in answer_text.split('\n'):
        if line.strip() == '':
            answer_lines.append('')
        else:
            answer_lines.extend(wrap_text(line, ImageDraw.Draw(Image.new("RGB",(1,1))), f_body, max_w))
    
    h = 12 + 24 + len(answer_lines) * (23 + LINE_SPACING) + 12
    y = canvas.reserve(h)
    def _draw(img_draw):
        draw_rounded_rect(img_draw, [PAD+8, y, W-PAD-8, y+h-4], 12, tier_bg, tier_bd, 1)
        # 标签
        img_draw.text((PAD+20, y+8), tier_label, fill=tier_color, font=f_label)
        # meta
        mw, mh = text_size(img_draw, tier_meta, f_meta)
        img_draw.text((W-PAD-20-mw, y+10), tier_meta, fill=C_GRAY, font=f_meta)
        # body
        oy = y + 8 + 24
        for line in answer_lines:
            if line:
                img_draw.text((PAD+22, oy), line, fill=C_INK, font=f_body)
            oy += 23 + LINE_SPACING
    canvas.items.append(_draw)

def draw_tips(canvas, tips_text):
    """绘制得分技巧"""
    f = font(14, False)
    f_title = font(15, True)
    max_w = W - 2*PAD - 40
    lines = []
    for line in tips_text.split('\n'):
        if line.strip() == '':
            lines.append('')
        else:
            lines.extend(wrap_text(line, ImageDraw.Draw(Image.new("RGB",(1,1))), f, max_w))
    
    h = 12 + 24 + len(lines)*(21+LINE_SPACING) + 12
    y = canvas.reserve(h)
    def _draw(img_draw):
        draw_rounded_rect(img_draw, [PAD+8, y, W-PAD-8, y+h-4], 12, (255,247,224), (243,217,160), 1)
        img_draw.text((PAD+22, y+8), "得分技巧", fill=C_GOLD, font=f_title)
        oy = y + 8 + 26
        for line in lines:
            if line:
                img_draw.text((PAD+22, oy), line, fill=(90,80,50), font=f)
            oy += 21 + LINE_SPACING
    canvas.items.append(_draw)

def draw_spacer(canvas, h=12):
    canvas.reserve(h)

def generate_year_image(year, questions, output_path):
    canvas = Canvas()
    draw_header(canvas, f"{year} · 高中数学教资 · 主观题三档答案")
    draw_spacer(canvas, 8)
    
    for q in questions:
        draw_section_title(canvas, q['section'], q['section_color'])
        draw_question_card(canvas, q['badge'], q['badge_color'], q['title'], q['score'], q['origin'])
        draw_spacer(canvas, 6)
        
        for tier in q['tiers']:
            draw_tier(canvas, tier['label'], tier['color'], tier['bg'], tier['bd'], tier['meta'], tier['text'])
            draw_spacer(canvas, 4)
        
        if q.get('tips'):
            draw_tips(canvas, q['tips'])
        draw_spacer(canvas, 16)
    
    canvas.finalize()
    for item in canvas.items:
        item(canvas.draw)
    
    canvas.img.save(output_path, "PNG")
    print(f"已生成: {output_path} ({canvas.img.size[0]}x{canvas.img.size[1]})")

# ============ 2025上 数据 ============
year_2025上 = [
    {
        "section": "四、论述题",
        "section_color": C_LUN,
        "badge": "论述题",
        "badge_color": C_LUN,
        "title": "第15题 · 论述提高教师教学专业能力",
        "score": "10分",
        "origin": "结合普通高中数学学科内容，试论述为了更好落实高中数学课程标准，应如何进一步提高教师教学专业能力。",
        "tiers": [
            {
                "label": "🏆 满分版",
                "color": C_BLUE,
                "bg": C_FULL_BG, "bd": C_FULL_BD,
                "meta": "700字≈25min · 得分：9-10",
                "text": """落实高中数学课程标准，关键在于教师。教师是课程实施的主力军，其专业能力直接影响课程标准的落地效果。为更好落实课标，应从以下五方面提高教师教学专业能力。

一、以教师专业标准理念为指导，提升专业水平。以"育人本、师德为先、能力为重、终身学习"为理念，从专业理念与师德、专业知识、专业能力三个维度系统提升。例：参加新课标专题培训，将立德树人融入日常教学。

二、努力提升通识素养。教师应具备广博的知识视野，不断提升科学素养、人文素养和信息技术素养。例：学习GeoGebra等信息技术工具辅助教学。

三、努力提升数学专业素养。深化对数学知识体系、思想方法和应用的理解。例：研读数学前沿著作，教学中渗透数学建模、逻辑推理等思想方法。

四、努力提升数学教育理论素养。主动学习数学教育理论、学习理论和课程理论。例：研读建构主义学习理论，据此设计符合认知水平的教学活动。

五、努力提升教学实践能力。在教学设计、课堂实施、教学评价与反思等环节不断提升。例：每节课后撰写教学反思，通过集体备课持续优化教学设计。

综上，提高教师教学专业能力是落实课标的关键，教师应提升通识素养、数学专业素养、教育理论素养和教学实践能力，同时学校应加强教研团队建设。""",
            },
            {
                "label": "🎯 考场版",
                "color": C_GREEN,
                "bg": C_EXAM_BG, "bd": C_EXAM_BD,
                "meta": "450字≈10min · 得分：8-9",
                "text": """落实高中数学课程标准，关键在于教师。应从以下方面提高教师教学专业能力。

一、以教师专业标准理念为指导，提升专业水平。以"育人本、师德为先、能力为重、终身学习"为理念，从专业理念与师德、专业知识、专业能力三个维度系统提升。例：参加新课标专题培训。

二、努力提升数学专业素养。深化对数学知识体系、思想方法和应用的理解。例：教学中渗透数学建模、逻辑推理等思想方法。

三、努力提升教学实践能力。在教学设计、课堂实施、教学评价与反思等环节不断提升。例：每节课后撰写教学反思，通过集体备课优化教学设计。

综上，教师应以专业标准理念为指导，提升数学专业素养和教学实践能力，学校应加强教研团队建设，才能将课标真正落到实处。""",
            },
            {
                "label": "🛟 救急版",
                "color": C_RED,
                "bg": C_LIFE_BG, "bd": C_LIFE_BD,
                "meta": "100字≈3min · 得分：5-6",
                "text": """为更好落实高中数学课程标准，教师应从五方面提高专业能力：一是以教师专业标准理念为指导提升专业水平；二是提升通识素养（科学、人文、信息技术）；三是提升数学专业素养；四是提升数学教育理论素养；五是提升教学实践能力（教学设计、课堂实施、评价反思）。（课标P104-105）""",
            },
        ],
        "tips": """分点作答（一、二、三…），阅卷按点给分；10分论述题写3-4个分点即可拿满
首尾各1-2句点题，呼应"落实课程标准"与"教师专业能力"，拿结构分
课标原话是得分关键词：专业理念与师德、专业知识、专业能力
本题是课标有原文清单的类型，五个方面直接照搬课标P104-105
考场时间紧时优先写"专业标准理念""数学专业素养""教学实践能力"三点""",
    },
    {
        "section": "五、案例分析",
        "section_color": C_AN,
        "badge": "案例分析",
        "badge_color": C_AN,
        "title": "第16题 · 杨辉三角性质与应用 · 过程性评价",
        "score": "20分",
        "origin": "(1) 除材料中提到的性质之外，杨辉三角形还有哪些性质？（6分）\n(2) 结合评价量表从教师和学生的角度分析过程性评价的作用。（8分）\n(3) 可以从哪些维度评价研究报告。（6分）",
        "tiers": [
            {
                "label": "🏆 满分版",
                "color": C_BLUE,
                "bg": C_FULL_BG, "bd": C_FULL_BD,
                "meta": "612字≈20min · 得分：18-20",
                "text": """(1) 杨辉三角形的其他性质：
①对称性：C(n,k)=C(n,n-k)，每行二项式系数关于中间项对称
②二项式系数和：第n行各系数之和为2^n
③递推关系：C(n,k)=C(n-1,k-1)+C(n-1,k)
④斜行求和：第k条斜行各数之和等于第k个斐波那契数

(2) 从教师角度：
①及时反馈：通过量表及时了解学生探究过程中的表现和困难，调整教学策略
②了解学情：量表从多维度记录学习过程，帮助教师全面掌握学情，因材施教
③调整教学：依据过程性数据反思教学设计的有效性，优化后续教学安排
从学生角度：
①自我反思：学生借助量表明确自身优势与不足，促进自我反思与元认知发展
②激发动力：过程性评价关注学习过程而非仅看结果，让学生获得持续成就感
③明确方向：量表提供具体评价指标，帮助学生明确后续努力方向

(3) 评价研究报告的维度：
①科学性：研究方法是否正确，数据是否准确，结论是否合理
②规范性：报告结构是否完整，格式是否规范，语言表达是否清晰
③创新性：是否有独特的视角或方法，是否提出新的发现或见解
④实用性：研究成果是否有实际应用价值，能否解决实际问题""",
            },
            {
                "label": "🎯 考场版",
                "color": C_GREEN,
                "bg": C_EXAM_BG, "bd": C_EXAM_BD,
                "meta": "398字≈15min · 得分：15-17",
                "text": """(1) 杨辉三角性质：①对称性：C(n,k)=C(n,n-k)；②系数和：第n行系数之和为2^n；③递推关系：C(n,k)=C(n-1,k-1)+C(n-1,k)；④斜行求和：斜行各数之和构成斐波那契数列。

(2) 教师角度：①通过量表及时反馈学生学习状况，调整教学策略；②全面了解学情，因材施教；③依据过程数据反思教学设计，优化教学。
学生角度：①借助量表自我反思，发现优缺点；②关注过程而非仅结果，激发学习动力；③量表提供明确指标，指明努力方向。

(3) 评价维度：①科学性（方法正确、数据准确、结论合理）；②规范性（结构完整、格式规范、语言清晰）；③创新性（独特视角或新发现）；④实用性（有应用价值、能解决实际问题）。""",
            },
            {
                "label": "🛟 救急版",
                "color": C_RED,
                "bg": C_LIFE_BG, "bd": C_LIFE_BD,
                "meta": "102字≈4min · 得分：9-11",
                "text": """(1) 杨辉三角性质：对称性（C(n,k)=C(n,n-k)）、系数和为2^n、递推关系、斜行和为斐波那契数。
(2) 教师：及时反馈、了解学情、调整教学；学生：自我反思、激发动力、明确方向。
(3) 评价维度：科学性、规范性、创新性、实用性。""",
            },
        ],
        "tips": """问①是纯背记题，至少写出3条杨辉三角性质，每条带名称+一句话解释
问②必须分教师和学生两个角度作答，各写2-3点，务必提到"评价量表"
问③背评价维度框架：科学性、规范性、创新性、实用性
三问时间分配：问①3min、问②8min、问③4min""",
    },
    {
        "section": "六、教学设计",
        "section_color": C_SHE,
        "badge": "教学设计",
        "badge_color": C_SHE,
        "title": "第17题 · 平面向量基本定理 · 教学设计",
        "score": "30分",
        "origin": '(1) 阐述平面向量的基本定理。（5分）\n(2) 说明平面向量的基本定理的作用。（5分）\n(3) 围绕"平面向量的基本定理"设计教案。（20分）',
        "tiers": [
            {
                "label": "🏆 满分版",
                "color": C_BLUE,
                "bg": C_FULL_BG, "bd": C_FULL_BD,
                "meta": "920字≈31min · 得分：27-30",
                "text": """(1) 平面向量基本定理：如果 e₁、e₂ 是同一平面内两个不共线的向量，那么该平面内的任一向量 a 可以表示为 a = λ₁e₁ + λ₂e₂，其中 λ₁、λ₂ 是唯一确定的实数。不共线的向量 e₁、e₂ 叫做表示这一平面内所有向量的一组基底。

(2) 作用：①代数化——将向量的几何表示转化为代数形式，使向量运算可借助实数运算完成；②坐标化——为建立向量坐标奠定理论基础，使向量可用坐标(x,y)表示，实现几何问题代数化；③统一基底——平面内所有向量均可由一组基底表示，为向量运算提供统一框架。

(3) 教案设计：
教学目标：①知道平面向量基本定理的内容，理解基底概念，应用定理解决向量分解问题；②通过独立思考、小组讨论，经历定理探究过程，提升合作交流能力；③感受数学与物理的密切联系，激发学习兴趣。
教学重难点：重点——平面向量基本定理的内容及基底的概念；难点——定理的探究过程及唯一性的理解。
情境引入：教师展示物理中力的分解实例——一个力F可分解为两个不共线的分力F₁、F₂，提出问题：平面内任一向量能否也分解为两个不共线向量的组合？学生观察思考、小组讨论。设计意图：以物理实例激发兴趣，感受学科间联系，体现数学化过程。
定理解释：教师提出目标问题，组织学生四人一组探究。学生在方格纸上画图，发现 a=λ₁e₁+λ₂e₂ 总能成立且 λ₁、λ₂ 唯一。教师引导总结定理内容和基底概念。设计意图：学生经历"探究→验证→归纳"过程，发展逻辑推理与直观想象素养。
定理巩固：练习1——用基底e₁、e₂表示给定向量（求λ₁、λ₂）；练习2——判断向量组能否作为基底（需不共线）。设计意图：变式练习巩固定理，分层达标。
小结作业：小结——学生畅谈收获，教师评价总结；作业——完成课后练习或设计生活实际问题。设计意图：小结检验重点认识情况，作业再巩固。""",
            },
            {
                "label": "🎯 考场版",
                "color": C_GREEN,
                "bg": C_EXAM_BG, "bd": C_EXAM_BD,
                "meta": "550字≈18min · 得分：24-27",
                "text": """(1) 平面向量基本定理：如果 e₁、e₂ 是同一平面内两个不共线的向量，那么该平面内的任一向量 a 可以表示为 a = λ₁e₁ + λ₂e₂，其中 λ₁、λ₂ 唯一确定。e₁、e₂ 叫做表示这一平面内所有向量的一组基底。

(2) 作用：①将向量代数化，使向量运算转化为实数运算；②为向量坐标化奠定理论基础，实现几何问题代数化；③提供统一基底，为向量运算建立框架。

(3) 教案设计：
教学目标：①知道平面向量基本定理内容及基底概念，应用定理解决向量分解问题；②通过独立思考、小组讨论，经历探究过程，提升合作交流能力；③感受数学与物理的联系，激发兴趣。
教学重难点：重点——平面向量基本定理内容及基底概念；难点——定理的探究过程及唯一性的理解。
情境引入：教师展示物理中力的分解实例，提出问题：平面内任一向量能否分解为两个不共线向量的组合？学生观察思考、小组讨论。设计意图：以物理实例激发兴趣，感受学科间联系，体现数学化过程。
定理解释：教师提出目标问题，组织学生四人一组探究。学生在方格纸上画图，发现 a=λ₁e₁+λ₂e₂ 总能成立且 λ₁、λ₂ 唯一。教师引导总结定理内容和基底概念。设计意图：学生经历"探究→验证→归纳"过程，发展逻辑推理与直观想象素养，体现教师主导、学生主体。
定理巩固：练习1——用基底e₁、e₂表示给定向量（求λ₁、λ₂）；练习2——判断向量组能否作为基底（需不共线）。设计意图：变式练习巩固定理，分层达标，及时反馈。
小结作业：小结——学生畅谈收获，教师评价总结；作业——完成课后练习或设计生活实际问题。设计意图：小结检验重点认识情况，增强信心；作业再巩固再认识。""",
            },
            {
                "label": "🛟 救急版",
                "color": C_RED,
                "bg": C_LIFE_BG, "bd": C_LIFE_BD,
                "meta": "125字≈5min · 得分：12-15",
                "text": """(1) e₁、e₂ 不共线，则任一向量 a=λ₁e₁+λ₂e₂（λ₁、λ₂唯一），e₁、e₂为基底。
(2) 作用：将向量代数化、坐标化，为向量运算提供统一框架。
(3) 目标：知道定理内容，理解探究过程，应用解决分解问题。重难点：重点定理内容及基底，难点唯一性理解。
情境引入：力的分解，提问能否分解为两个不共线向量。激发兴趣，感受学科联系。
定理解释：画图探究→发现a=λ₁e₁+λ₂e₂→归纳定理。意图：探究发现，发展逻辑推理。
定理巩固：用基底表示向量、判断基底。意图：巩固步骤。
小结作业：畅谈收获，完成课后练习。意图：再巩固。""",
            },
        ],
        "tips": """环节名称必须用题目给的六个：教学目标、教学重难点、情境引入、定理解释、定理巩固、小结作业
第(1)问阐述定理要写全三个要素：不共线基底 + a=λ₁e₁+λ₂e₂ + 唯一性
第(2)问作用至少答三点：代数化、坐标化、统一基底
第(3)问每个环节都要写"设计意图"，这是阅卷按点给分的关键
导入用力的分解（物理情境），贴合课标要求""",
    },
]

# ============ 生成 ============
if __name__ == "__main__":
    output_dir = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷/2025上"
    generate_year_image("2025年上半年", year_2025上, os.path.join(output_dir, "答案总览.png"))
