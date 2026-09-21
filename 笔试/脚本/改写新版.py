#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把所有年份的q12/q13/q15/q16/q17从旧版tab格式改为新版三列+推导格式
从现有HTML中提取三档答案内容，套用新模板
"""
import re, os, html as htmlmod

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"

# 新版CSS（电子书风格，与2025上q17一致）
NEW_CSS = """  :root{
    --pink:#e5487c; --pink-bg:#fdeef4; --blue:#2b7de9; --blue-bg:#eaf3fe;
    --gold:#b26a00; --gold-bg:#fff7e0; --ink:#2b2b33; --gray:#8a8f98; --line:#e8e8ee;
  }
  *{box-sizing:border-box;margin:0}
  body{background:#f2f3f7;color:var(--ink);
       font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
       line-height:1.9;font-size:22px;padding:16px}
  .wrap{max-width:none;margin:0;padding:0}
  section.card{background:none;box-shadow:none;border-radius:0;padding:0;margin:0}
  .qhead{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}
  .qhead h2{font-size:24px;margin:0}
  .badge{border-radius:6px;padding:4px 14px;font-size:16px;font-weight:600;white-space:nowrap}
  .b-she{background:#0ca678;color:#fff}
  .b-lun{background:#e5487c;color:#fff}
  .b-an{background:#f08c00;color:#fff}
  .b-jie{background:#5b8def;color:#fff}
  .score{color:var(--pink);font-weight:700;font-size:17px}
  .origin{background:#f7f7fa;border-left:3px solid #b9bdc9;border-radius:6px;
       padding:12px 16px;color:#555;font-size:20px;margin:10px 0}
  a{color:#1971c2;text-decoration:underline;text-underline-offset:2px}
  mark{background:#d0ebff;color:#1971c2;padding:0 2px;border-radius:3px}
  .pk{color:var(--pink);font-weight:700}
  .ex{background:#fff3bf;border-radius:4px;padding:1px 6px;color:#9a7b00}
  .points{list-style:none;padding-left:0}
  .points>li{margin:8px 0}
  .points .pt{font-weight:700;color:var(--pink)}
  ul.tips{margin:6px 0;padding-left:22px}
  ul.tips li{margin:6px 0;font-size:18px}
  footer{color:#9aa0aa;font-size:16px;text-align:center;margin-top:16px}
  .back-link{display:none}
  .tiers-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;align-items:start}
  @media(max-width:1100px){.tiers-row{grid-template-columns:1fr;gap:14px}}
  .tier-col{display:flex;flex-direction:column;gap:6px}
  .tier-header{border-radius:8px 8px 0 0;padding:8px 14px;font-size:20px;font-weight:700;text-align:center}
  .tier-full-h{background:#eef6ff;color:#1971c2;border:1px solid #b6d6f7;border-bottom:none}
  .tier-exam-h{background:#e9f9ef;color:#2b8a3e;border:1px solid #b2e2c5;border-bottom:none}
  .tier-life-h{background:#ffecec;color:#c92a2a;border:1px solid #ffc9c9;border-bottom:none}
  .tier-body{border-radius:0 0 8px 8px;padding:12px 16px;font-size:20px;line-height:1.9}
  .tier-full-b{background:#f7fbff;border:1px solid #b6d6f7;border-top:none}
  .tier-exam-b{background:#f5fcf8;border:1px solid #b2e2c5;border-top:none}
  .tier-life-b{background:#fff8f8;border:1px solid #ffc9c9;border-top:none}
  .tier-body p{margin:8px 0}
  .tier-body ul{padding-left:22px;margin:4px 0}
  .tier-body li{margin:5px 0}
  .derive-box{margin-top:8px;border-radius:8px;padding:10px 16px;font-size:17px;line-height:1.7}
  .derive-full{background:#f0f7ff;border:1px solid #c4dcf8}
  .derive-exam{background:#edf9f2;border:1px solid #c4e8d4}
  .derive-life{background:#fff0f0;border:1px solid #f6c3c3}
  .derive-box .derive-title{font-weight:700;font-size:17px;margin-bottom:4px}
  .derive-full .derive-title{color:#1971c2}
  .derive-exam .derive-title{color:#2b8a3e}
  .derive-life .derive-title{color:#c92a2a}
  .derive-box ul{padding-left:20px;margin:4px 0}
  .derive-box li{margin:4px 0}
  .k-gold{background:var(--gold-bg);border:1px solid #f3d9a0;border-radius:8px;padding:12px 16px;margin:10px 0}
  .k-gold h3{color:var(--gold);margin:0 0 6px;font-size:18px}
  @media print{body{background:#fff}.tiers-row{grid-template-columns:1fr 1fr 1fr}}"""

def find_block_content(content, class_name):
    """用div计数法提取block内容（保留内部HTML）"""
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

def find_tips(content):
    """提取得分技巧"""
    tips_html = find_block_content(content, 'k-gold')
    if tips_html:
        tips_m = re.search(r'<ul class="tips"[^>]*>(.*?)</ul>', tips_html, re.S)
        if tips_m:
            return tips_m.group(1).strip()
    return ''

def find_derive(content):
    """提取推导区内容（details内的ul部分）"""
    m = re.search(r'<details[^>]*>.*?<ul class="points"[^>]*>(.*?)</ul>', content, re.S)
    if m:
        return m.group(1).strip()
    return ''

def extract_question(filepath):
    """从旧版HTML提取所有信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    q = {'title':'', 'score':'', 'origin':'', 'badge':'', 'badge_class':'',
         'full':'', 'exam':'', 'life':'', 'derive':'', 'tips':''}

    # 题型
    if 'b-lun' in content:
        q['badge']='论述题'; q['badge_class']='b-lun'
    elif 'b-an' in content:
        q['badge']='案例分析'; q['badge_class']='b-an'
    elif 'b-she' in content:
        q['badge']='教学设计'; q['badge_class']='b-she'
    elif 'b-jie' in content:
        q['badge']='简答题'; q['badge_class']='b-jie'

    # 标题
    m = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.S)
    if m: q['title'] = re.sub(r'<[^>]+>', '', m.group(1)).strip()

    # 分值
    m = re.search(r'class="score"[^>]*>(.*?)</span>', content, re.S)
    if m: q['score'] = re.sub(r'<[^>]+>', '', m.group(1)).strip()

    # 原题
    m = re.search(r'class="origin"[^>]*>(.*?)</div>', content, re.S)
    if m: q['origin'] = m.group(1).strip()

    # 三档答案（保留内部HTML）
    q['full'] = find_block_content(content, 't-full').strip()
    q['exam'] = find_block_content(content, 't-exam').strip()
    q['life'] = find_block_content(content, 't-life').strip()

    # 推导
    q['derive'] = find_derive(content)

    # 得分技巧
    q['tips'] = find_tips(content)

    return q

def build_new_html(year, qnum, q):
    """构建新版HTML"""
    # 档位meta
    full_meta = ''
    exam_meta = ''
    life_meta = ''
    
    # 从原始tab按钮提取meta
    # 如果没有就给默认值
    
    # 构建推导区HTML
    derive_html = ''
    if q['derive']:
        derive_html = f'''      <div class="derive-box derive-full">
        <div class="derive-title">🧠 推导</div>
        <ul>{q['derive']}</ul>
      </div>'''

    # 简答题没有三档tab结构的情况
    if not q['full'] and not q['exam']:
        # 可能是旧版q12格式，只有k-gold参考答案
        tips_content = find_block_content(open(os.path.join(BASE, year, f'q{qnum}.html')).read(), 'k-gold')
        if tips_content:
            q['full'] = tips_content
            q['exam'] = '<p>（精简版见满分版关键点）</p>'
            q['life'] = '<p>（关键词见上）</p>'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{year} · 第{qnum}题</title>
<style>
{NEW_CSS}
</style>
</head>
<body>
<div class="wrap">
<section class="card" id="q{qnum}">
  <div class="qhead">
    <span class="badge {q['badge_class']}">{q['badge']}</span>
    <h2>{q['title']}</h2>
    <span class="score">{q['score']}</span>
  </div>
  <div class="origin">{q['origin']}</div>'''

    if q['full'] or q['exam']:
        html += f'''
  <div class="tiers-row">
    <div class="tier-col">
      <div class="tier-header tier-full-h">🏆 满分版</div>
      <div class="tier-body tier-full-b">{q['full']}</div>
      {derive_html}
    </div>
    <div class="tier-col">
      <div class="tier-header tier-exam-h">🎯 考场版</div>
      <div class="tier-body tier-exam-b">{q['exam']}</div>
      <div class="derive-box derive-exam">
        <div class="derive-title">🧠 考场版怎么来的</div>
        <ul><li>从满分版砍例子和展开说明，保留核心结论句。</li><li>砍掉黄色例子，黑色结论句一字不砍。</li></ul>
      </div>
    </div>
    <div class="tier-col">
      <div class="tier-header tier-life-h">🛟 救急版</div>
      <div class="tier-body tier-life-b">{q['life']}</div>
      <div class="derive-box derive-life">
        <div class="derive-title">🧠 救急版蹭分逻辑</div>
        <ul><li>不会时写通用框架+得分关键词，不依赖具体内容也能拿结构分。</li><li>分点作答、写环节名称、写课标术语——这三样不依赖具体知识。</li></ul>
      </div>
    </div>
  </div>'''
    else:
        # 没有三档的题目（如旧版q12）
        html += f'\n  <div class="tier-body tier-full-b">{q["tips"]}</div>'

    if q['tips']:
        html += f'''
  <div class="k-gold">
    <h3>💡 得分技巧</h3>
    <ul class="tips">{q['tips']}</ul>
  </div>'''

    html += f'''
</section>
<div style="text-align:center;margin:14px 0"><a href="../../../../固定/404_高中数学学科/三档说明.html" style="font-size:13px;color:#b26a00;text-decoration:none">🧭 三档制说明 →</a></div>
<footer><a href="解析.html">← 返回目录</a></footer>
</div>
</body>
</html>'''
    return html

if __name__ == "__main__":
    years = ['2025上','2024下','2024上','2023下','2023上','2022下','2022上','2021下','2021上','2020下']
    questions = ['q12','q13','q15','q16','q17']
    count = 0
    
    for year in years:
        year_dir = os.path.join(BASE, year)
        for qnum in questions:
            filepath = os.path.join(year_dir, f'{qnum}.html')
            if not os.path.exists(filepath):
                continue
            # 跳过已经是新版格式的（2025上q17）
            if year == '2025上' and qnum == 'q17':
                count += 1
                continue
            
            q = extract_question(filepath)
            if not q['title']:
                continue
            
            new_html = build_new_html(year, qnum, q)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            count += 1
            print(f"  {year}/{qnum} 已更新")
    
    print(f"\n共更新 {count} 个文件")
