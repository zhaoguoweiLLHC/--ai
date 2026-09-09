#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把所有年份的q12.html拆分为q12.html和q13.html，每题独立一页，带推导模块和三档答案"""
import os

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"

TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{year} · 第{qnum}题 · 简答题</title>
<style>
  :root{{
    --pink:#e5487c; --pink-bg:#fdeef4; --blue:#2b7de9; --blue-bg:#eaf3fe;
    --gold:#b26a00; --gold-bg:#fff7e0; --ink:#2b2b33; --gray:#8a8f98; --line:#e8e8ee;
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:#f2f3f7;color:var(--ink);
       font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
       line-height:1.85;font-size:16px}}
  .wrap{{max-width:860px;margin:0 auto;padding:28px 18px 60px}}
  section.card{{background:#fff;border-radius:16px;padding:24px 26px;margin-bottom:20px;
       box-shadow:0 2px 10px rgba(30,30,60,.07)}}
  .qhead{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}}
  .qhead h2{{font-size:19px;margin:0}}
  .badge{{border-radius:8px;padding:2px 12px;font-size:13px;font-weight:600;white-space:nowrap}}
  .b-jie{{background:#5b8def;color:#fff}}
  .score{{color:var(--pink);font-weight:700;font-size:14px}}
  .origin{{background:#f7f7fa;border-left:4px solid #b9bdc9;border-radius:8px;
       padding:12px 16px;color:#555;font-size:15px;margin:12px 0}}
  .block{{border-radius:12px;padding:14px 18px;margin:14px 0}}
  .block h3{{margin:0 0 8px;font-size:15px}}
  .k-bibei{{background:var(--pink-bg);border:1px solid #f6c3d6}}
  .k-bibei h3{{color:var(--pink)}}
  .k-gold{{background:var(--gold-bg);border:1px solid #f3d9a0}}
  .k-gold h3{{color:var(--gold)}}
  a{{color:#1971c2;text-decoration:underline;text-underline-offset:3px}}
  mark{{background:#d0ebff;color:#1971c2;padding:0 3px;border-radius:4px}}
  .pk{{color:var(--pink);font-weight:700}}
  .ex{{background:#fff3bf;border-radius:8px;padding:2px 8px;color:#9a7b00}}
  .points{{list-style:none;padding-left:4px}}
  .points>li{{margin:10px 0}}
  .points .pt{{font-weight:700;color:var(--pink)}}
  ul.tips{{margin:6px 0;padding-left:20px}}
  ul.tips li{{margin:6px 0}}
  .wait{{color:#9aa0aa;text-align:center;padding:10px 0;font-size:14px}}
  footer{{color:#9aa0aa;font-size:13px;text-align:center;margin-top:26px}}
  .back-link{{position:fixed;top:12px;left:12px;z-index:200;background:rgba(255,255,255,.9);
    border:1px solid #e8e8ee;border-radius:8px;padding:5px 14px;font-size:14px;
    text-decoration:none;color:#1971c2;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  .tabs{{display:flex;gap:0;margin:14px 0 0;border-radius:12px 12px 0 0;overflow:hidden}}
  .tab-btn{{flex:1;padding:10px 8px;border:none;background:#f2f3f7;font-size:14px;font-weight:600;
    cursor:pointer;text-align:center;color:#8a8f98;border-bottom:3px solid transparent;transition:.2s}}
  .tab-btn.active-t{{color:#fff}}
  .tab-btn[data-tab="t-full"].active-t{{background:#eef6ff;color:#1971c2;border-bottom-color:#1971c2}}
  .tab-btn[data-tab="t-exam"].active-t{{background:#e9f9ef;color:#2b8a3e;border-bottom-color:#2b8a3e}}
  .tab-btn[data-tab="t-life"].active-t{{background:#ffecec;color:#c92a2a;border-bottom-color:#c92a2a}}
  .tab-content{{display:none}}
  .tab-content.active-t{{display:block}}
  .t-full{{background:#eef6ff;border:1px solid #b6d6f7}}
  .t-exam{{background:#e9f9ef;border:1px solid #b2e2c5}}
  .t-life{{background:#ffecec;border:1px solid #ffc9c9}}
  details{{margin:14px 0;padding:14px 18px;border-radius:12px;border:1px solid #f6c3d6;background:#fdeef4}}
  details summary::-webkit-details-marker{{display:none}}
  details summary::before{{content:"▸ ";font-size:12px}}
  details[open] summary::before{{content:"▾ ";font-size:12px}}
  @media print{{body{{background:#fff}}.wrap{{max-width:none;padding:0}}section.card{{box-shadow:none;border:1px solid #eee;break-inside:avoid}}}}
</style>
</head>
<body>
<div class="wrap">
<a href="解析.html" class="back-link">← 返回目录</a>
<section class="card" id="q{qnum}">
  <div class="qhead">
    <span class="badge b-jie">简答题</span>
    <h2>第 {qnum} 题 · {title}</h2>
    <span class="score">7 分</span>
  </div>
  <div class="origin">{origin}</div>
  <details class="block k-bibei" open>
    <summary style="font-size:15px;font-weight:700;color:#e5487c;cursor:pointer;list-style:none">🧠 推导 · {derive_title}</summary>
    <ul class="points" style="list-style:none;padding-left:4px">
{derive_content}
    </ul>
  </details>
  <div class="tabs">
    <button class="tab-btn active-t" data-tab="t-full" onclick="switchTab('t-full')">🏆 满分版 <small style="font-size:11px;color:#888">{full_meta}</small></button>
    <button class="tab-btn" data-tab="t-exam" onclick="switchTab('t-exam')">🎯 考场版 <small style="font-size:11px;color:#888">{exam_meta}</small></button>
    <button class="tab-btn" data-tab="t-life" onclick="switchTab('t-life')">🛟 救急版 <small style="font-size:11px;color:#888">{life_meta}</small></button>
  </div>
  <div class="tab-content active-t" id="t-full">
    <div class="block t-full">
{full_answer}
    </div>
  </div>
  <div class="tab-content" id="t-exam">
    <div class="block t-exam">
{exam_answer}
    </div>
  </div>
  <div class="tab-content" id="t-life">
    <div class="block t-life">
{life_answer}
    </div>
  </div>
  <div class="block k-gold">
    <h3>💡 得分技巧</h3>
    <ul class="tips">
{tips}
    </ul>
  </div>
</section>
<div style="text-align:center;margin:14px 0"><a href="../../../../固定/404_高中数学学科/三档说明.html" style="font-size:13px;color:#b26a00;text-decoration:none">🧭 三档制说明（分工/过渡/颜色图例）→</a></div>
<footer><a href="解析.html">← 返回目录</a></footer>
<script>
function switchTab(id){{
  document.querySelectorAll('.tab-btn').forEach(function(b){{b.classList.toggle('active-t',b.dataset.tab===id)}});
  document.querySelectorAll('.tab-content').forEach(function(c){{c.classList.toggle('active-t',c.id===id)}});
}}
</script>
</div>
</body>
</html>'''

# 各年份各题数据
DATA = {
    "2025上": {
        "q12": {
            "title": "二项分布实例",
            "origin": "说明二项分布的两个实例（不用计算）。",
            "derive_title": "二项分布的特征",
            "derive": """<li><span class="pt">① 审题：</span>举两个二项分布的实例，不用计算。关键是找到"独立重复试验+每次概率固定+计数"的场景。</li>
<li><span class="pt">② 找特征：</span>二项分布B(n,p)的三个要素：n次<b>独立</b>重复试验、每次成功概率<b>固定</b>为p、随机变量是成功<b>次数</b>k。</li>
<li><span class="pt">③ 选实例：</span>抛硬币（最经典，p=0.5）、产品检验（有放回抽取，p=次品率）。</li>""",
            "full": """<p>二项分布描述的是n次独立重复试验中某事件恰好发生k次的概率分布。两个实例：</p>
<ol>
<li>抛硬币：连续抛掷一枚均匀硬币n次，每次正面向上的概率为0.5，正面向上的次数服从二项分布B(n,0.5)。</li>
<li>产品检验：从一批产品中有放回地抽取n件，每件为次品的概率为p，抽到的次品数服从二项分布B(n,p)。</li>
</ol>""",
            "exam": """<p>①抛硬币n次，正面向上次数服从B(n,0.5)；②有放回抽取产品n件，次品数服从B(n,p)。</p>""",
            "life": """<p>抛硬币<span class="pk">B(n,0.5)</span>、产品检验<span class="pk">B(n,p)</span>。关键：独立重复+概率固定+计次数。</p>""",
            "tips": """<li>只需举实例不用计算，答出"独立重复试验+概率固定"即可；</li>
<li>抛硬币和产品检验是最经典两个例子。</li>""",
        },
        "q13": {
            "title": "普通高中数学课程目标",
            "origin": "简述普通高中数学课程目标。",
            "derive_title": "课程目标四条怎么记",
            "derive": """<li><span class="pt">① 审题：</span>简述课程目标，背记题，写出课标中的四条目标即可。</li>
<li><span class="pt">② 记忆框架：</span>四条目标递进关系：<b>知识技能</b>（基础）→<b>思想方法+素养</b>（核心）→<b>能力</b>（应用）→<b>态度价值观</b>（情感）。</li>
<li><span class="pt">③ 关键词：</span>六大核心素养名称要写全：数学抽象、逻辑推理、数学建模、直观想象、数学运算、数据分析。</li>""",
            "full": """<p>普通高中数学课程目标包括：</p>
<ol>
<li>获得必要的数学基础知识和基本技能，理解基本的数学概念和数学结论的本质。</li>
<li>体会和运用数学思想方法，发展数学学科核心素养（数学抽象、逻辑推理、数学建模、直观想象、数学运算、数据分析）。</li>
<li>提高空间想象能力、抽象概括能力、推理论证能力、运算求解能力和数据处理能力。</li>
<li>发展数学应用意识和创新意识，提高学习数学的兴趣，形成科学态度和理性精神。</li>
</ol>""",
            "exam": """<p>①获得基础知识与基本技能，理解概念本质；②体会数学思想方法，发展六大核心素养；③提高空间想象、抽象概括、推理论证、运算求解、数据处理能力；④发展应用意识和创新意识，形成科学态度。</p>""",
            "life": """<p><span class="pk">基础知识技能</span>→<span class="pk">思想方法+六大素养</span>→<span class="pk">五大能力</span>→<span class="pk">应用意识+科学态度</span>。</p>""",
            "tips": """<li>课程目标是背记题，四条全写=满分；</li>
<li>六大核心素养名称必须写全；</li>
<li>时间紧写前两条保底。</li>""",
        },
    },
    "2024下": {
        "q12": {
            "title": "函数与方程的联系",
            "origin": "以二次函数和一元二次方程为例，说明函数与方程的联系。",
            "derive_title": "函数与方程的三层联系",
            "derive": """<li><span class="pt">① 审题：</span>以二次函数y=ax²+bx+c和一元二次方程ax²+bx+c=0为例，说明联系。</li>
<li><span class="pt">② 找联系：</span>三层联系：<b>零点=根</b>（方程的根就是函数图象与x轴交点）→<b>判别式=交点个数</b>（Δ决定根的个数）→<b>函数值符号=不等式解集</b>（y>0对应ax²+bx+c>0）。</li>
<li><span class="pt">③ 组织：</span>按"零点→判别式→不等式"三层递进论述。</li>""",
            "full": """<p>以二次函数y=ax²+bx+c和一元二次方程ax²+bx+c=0为例：</p>
<ol>
<li><b>方程的根＝函数的零点。</b>方程的实数根就是函数图象与x轴交点的横坐标。求方程的根等价于求函数的零点。</li>
<li><b>判别式决定交点个数。</b>Δ>0两个交点两不等实根；Δ=0一个交点等根；Δ<0无交点无实根。</li>
<li><b>函数值符号与不等式。</b>y>0对应的x范围就是ax²+bx+c>0的解集，体现"函数—方程—不等式"三位一体。</li>
</ol>""",
            "exam": """<p>①方程的根＝函数零点（图象与x轴交点）；②判别式Δ决定根的个数；③函数值符号对应不等式解集。三者构成"函数—方程—不等式"三位一体。</p>""",
            "life": """<p><span class="pk">根=零点</span>、<span class="pk">Δ定根数</span>、<span class="pk">符号=不等式</span>。</p>""",
            "tips": """<li>以二次函数为例，三步递进：零点→判别式→不等式；</li>
<li>金句"三位一体"写出即被识别。</li>""",
        },
        "q13": {
            "title": "坐标(a,b)表示的数学对象",
            "origin": "设a,b为两实数，列举出坐标(a,b)可表示的三个数学对象。",
            "derive_title": "坐标的多重含义",
            "derive": """<li><span class="pt">① 审题：</span>列举坐标(a,b)可表示的三个数学对象，纯背记题。</li>
<li><span class="pt">② 回忆：</span>坐标(a,b)在高中数学中可表示：<b>点</b>（解析几何）、<b>向量</b>（向量部分）、<b>复数</b>（复数部分）。</li>
<li><span class="pt">③ 组织：</span>每个对象一句话说明即可。</li>""",
            "full": """<p>坐标(a,b)可以表示以下三个数学对象：</p>
<ol>
<li><b>平面直角坐标系中的点。</b>表示平面上横坐标为a、纵坐标为b的点P(a,b)。</li>
<li><b>二维向量。</b>表示向量v=(a,b)，a为横分量，b为纵分量。</li>
<li><b>复数。</b>表示复数z=a+bi，a为实部，b为虚部，对应复平面上的点。</li>
</ol>""",
            "exam": """<p>①点P(a,b)；②向量(a,b)；③复数a+bi。</p>""",
            "life": """<p><span class="pk">点</span>P(a,b)、<span class="pk">向量</span>(a,b)、<span class="pk">复数</span>a+bi。</p>""",
            "tips": """<li>只需列举三个对象，每个一句话即可；</li>
<li>坐标三重含义（点、向量、复数）是高频考点。</li>""",
        },
    },
    "2024上": {
        "q12": {
            "title": "过程评价应关注的方面",
            "origin": "简要说明过程评价应关注哪几个方面。",
            "derive_title": "过程评价五方面",
            "derive": """<li><span class="pt">① 审题：</span>过程评价关注哪些方面，背记题，列举即可。</li>
<li><span class="pt">② 记忆框架：</span>五个方面围绕学生：<b>参与</b>（是否积极）→<b>思维</b>（怎么想）→<b>合作</b>（是否交流）→<b>反思</b>（能否改进）→<b>情感</b>（兴趣态度）。</li>""",
            "full": """<p>过程评价应关注以下几个方面：</p>
<ol>
<li><b>学生的参与度。</b>课堂参与、小组讨论、探究活动等。</li>
<li><b>学生的思维过程。</b>思考问题的方式、策略和推理过程。</li>
<li><b>学生的合作交流。</b>表达观点、倾听他人、协作解决。</li>
<li><b>学生的反思与改进。</b>发现不足并改进。</li>
<li><b>学生的情感态度。</b>兴趣、信心、毅力等。</li>
</ol>""",
            "exam": """<p>①参与度；②思维过程；③合作交流；④反思改进；⑤情感态度。</p>""",
            "life": """<p><span class="pk">参与、思维、合作、反思、情感</span>。</p>""",
            "tips": """<li>五方面口诀"参与思维合作反思情感"；</li>
<li>每方面一句话解释即可。</li>""",
        },
        "q13": {
            "title": "数学概念教学的主要环节",
            "origin": "以等比数列概念教学为例，简述数学概念教学的主要环节。",
            "derive_title": "概念教学四环节",
            "derive": """<li><span class="pt">① 审题：</span>以等比数列为例，简述概念教学环节，背框架+套例子。</li>
<li><span class="pt">② 记忆框架：</span>四环节固定：<b>引入</b>（实例引入）→<b>形成</b>（归纳概括）→<b>明确</b>（严格定义）→<b>巩固</b>（练习应用）。</li>
<li><span class="pt">③ 套例子：</span>等比数列——引入用细胞分裂(1,2,4,8…)，形成时观察"后项/前项=常数"，明确时强调q≠0。</li>""",
            "full": """<p>以等比数列概念教学为例，数学概念教学一般包括以下环节：</p>
<ol>
<li><b>概念的引入。</b>从实例引入：展示细胞分裂(1,2,4,8,…)和折纸等实例，观察共同特征——后一项与前一项的比为常数。</li>
<li><b>概念的形成。</b>从实例中抽象本质属性，归纳概括出定义：从第二项起每项与前一项的比等于同一常数。</li>
<li><b>概念的明确。</b>给出严格定义，强调"公比q≠0"和"首项a₁≠0"的条件。</li>
<li><b>概念的巩固与应用。</b>通过练习判断给定数列是否为等比数列、已知前几项求公比等。</li>
</ol>""",
            "exam": """<p>①引入（细胞分裂实例）；②形成（归纳"比=常数"）；③明确（严格定义，q≠0）；④巩固（判断练习）。</p>""",
            "life": """<p><span class="pk">引入→形成→明确→巩固</span>。等比数列：细胞分裂引入→比=常数→q≠0→判断练习。</p>""",
            "tips": """<li>概念教学四环节是固定框架不能变；</li>
<li>以等比数列为例时要提到具体实例。</li>""",
        },
    },
    "2023下": {
        "q12": {
            "title": "逻辑推理的含义及主要推理形式",
            "origin": "简述逻辑推理的含义及主要推理形式。",
            "derive_title": "三种推理形式的区别",
            "derive": """<li><span class="pt">① 审题：</span>简述含义+列举主要推理形式，背记题。</li>
<li><span class="pt">② 含义：</span>从已有命题出发依据规则推出新命题的思维过程。</li>
<li><span class="pt">③ 三种形式：</span>演绎（一般→特殊，<b>必然</b>成立）、归纳（特殊→一般，或然）、类比（A似B，或然）。核心区别在结论的<b>确定性</b>。</li>""",
            "full": """<p><b>含义：</b>逻辑推理是指从已有的事实或命题出发，依据规则推出其他命题的思维过程。它是数学核心素养之一。</p>
<p><b>主要推理形式：</b></p>
<ol>
<li><b>演绎推理（必然性推理）：</b>从一般到特殊，结论必然成立。如三段论。</li>
<li><b>归纳推理（或然性推理）：</b>从特殊到一般。包括完全归纳（必然）和不完全归纳（或然）。</li>
<li><b>类比推理：</b>根据两对象某些属性相同推断其他属性也相同，结论或然成立。</li>
</ol>""",
            "exam": """<p>逻辑推理＝从已有命题推出新命题。形式：①演绎（一般→特殊，必然）；②归纳（特殊→一般）；③类比（或然）。</p>""",
            "life": """<p><span class="pk">演绎（必然）、归纳、类比（或然）</span>。</p>""",
            "tips": """<li>三种推理核心区别：演绎必然、归纳和类比或然；</li>
<li>完全归纳是例外，结论也必然成立。</li>""",
        },
        "q13": {
            "title": "复数运算法则及加法几何意义",
            "origin": "写出复数代数运算的加法、减法、乘法、除法运算法则，并简述复数加法运算的几何意义。",
            "derive_title": "复数运算公式+几何意义",
            "derive": """<li><span class="pt">① 审题：</span>写出四则运算法则（背公式）+加法几何意义（一句话）。</li>
<li><span class="pt">② 设z₁=a+bi, z₂=c+di：</span>加法实虚部分别相加，减法分别相减，乘法用分配律展开（ac-bd)+(ad+bc)i，除法乘以共轭复数实数化。</li>
<li><span class="pt">③ 几何意义：</span>复数↔向量一一对应，加法对应向量加法的<b>平行四边形法则</b>。</li>""",
            "full": """<p>设z₁=a+bi, z₂=c+di（a,b,c,d∈R）：</p>
<ol>
<li><b>加法：</b>z₁+z₂=(a+c)+(b+d)i</li>
<li><b>减法：</b>z₁-z₂=(a-c)+(b-d)i</li>
<li><b>乘法：</b>z₁·z₂=(ac-bd)+(ad+bc)i</li>
<li><b>除法：</b>z₁/z₂=[(ac+bd)+(bc-ad)i]/(c²+d²)</li>
</ol>
<p><b>加法几何意义：</b>复数加法对应平面向量加法，遵循<b>平行四边形法则</b>。复数z₁对应向量(a,b)，z₂对应向量(c,d)，和对应以两向量为邻边的平行四边形对角线。</p>""",
            "exam": """<p>加(a+c)+(b+d)i；减(a-c)+(b-d)i；乘(ac-bd)+(ad+bc)i；除[(ac+bd)+(bc-ad)i]/(c²+d²)。加法几何意义＝平行四边形法则。</p>""",
            "life": """<p>加减乘除四公式；加法＝<span class="pk">平行四边形法则</span>。</p>""",
            "tips": """<li>四则运算要写全公式，不能只写文字；</li>
<li>加法几何意义就是向量加法的平行四边形法则。</li>""",
        },
    },
    "2023上": {
        "q12": {
            "title": "长方体模型的作用",
            "origin": "简述长方体模型在学习直线与直线、直线与平面、平面与平面的平行和垂直位置关系中的作用。（答出两条即可）",
            "derive_title": "长方体作为立体几何模型的价值",
            "derive": """<li><span class="pt">① 审题：</span>答出两条作用即可，每条带例子。</li>
<li><span class="pt">② 作用1：</span><b>直观感知</b>——长方体有丰富的线线/线面/面面关系实例（侧棱⊥底面、对立面∥）。</li>
<li><span class="pt">③ 作用2：</span><b>辅助证明</b>——在证明空间位置关系时借助长方体找思路、验证结论。</li>""",
            "full": """<ol>
<li><b>直观感知空间位置关系。</b>长方体提供丰富的线线、线面、面面位置关系实例。例：上下底面对应棱互相平行，侧棱与底面垂直，对立面互相平行。学生通过观察即可直观理解平行和垂直的概念。</li>
<li><b>辅助证明和推理。</b>长方体模型可作为验证和推理的载体。例：证明"若一条直线与两个平行平面中的一个垂直，则与另一个也垂直"时，可在长方体中直观验证。</li>
</ol>""",
            "exam": """<p>①直观感知（提供线线/线面/面面实例）；②辅助证明（找思路、验证结论）。</p>""",
            "life": """<p><span class="pk">直观感知</span>、<span class="pk">辅助证明</span>。</p>""",
            "tips": """<li>答两条即可，每条带具体例子；</li>
<li>长方体是最常用的立体几何模型。</li>""",
        },
        "q13": {
            "title": "与函数单调性相关的知识",
            "origin": '写出高中数学中与"函数单调性"密切相关的具体知识。（答出5条即可）',
            "derive_title": "单调性的知识网络",
            "derive": """<li><span class="pt">① 审题：</span>答出5条相关知识，每条一句话说明关联。</li>
<li><span class="pt">② 知识网络：</span>单调性连接了<b>图象</b>（上升下降）→<b>导数</b>（f'>0增）→<b>不等式</b>（比较大小）→<b>极值最值</b>（单调性改变处）→<b>反函数</b>（单调↔存在反函数）。</li>""",
            "full": """<ol>
<li><b>函数的图象。</b>单调性通过图象的上升/下降直观体现，作图需利用单调性确定变化趋势。</li>
<li><b>导数。</b>f'(x)>0则f(x)单调递增，f'(x)<0则递减。导数是研究单调性的重要工具。</li>
<li><b>不等式。</b>利用单调性可比较函数值大小（同一单调区间内自变量大小关系传递到函数值）。</li>
<li><b>极值与最值。</b>极值点两侧单调性改变，最值依赖于单调性分析。</li>
<li><b>反函数。</b>单调函数必定存在反函数（一一对应），单调性是函数存在反函数的充分条件。</li>
</ol>""",
            "exam": """<p>①函数图象；②导数（f'>0增）；③不等式（比较函数值）；④极值最值；⑤反函数（单调↔存在反函数）。</p>""",
            "life": """<p><span class="pk">图象、导数、不等式、极值、反函数</span>。</p>""",
            "tips": """<li>答5条，每条一句话说明关联；</li>
<li>导数与单调性的关系是最高频考点。</li>""",
        },
    },
    "2022下": {
        "q12": {
            "title": "分类的原则和意义",
            "origin": "简述分类的原则和学习分类的意义。",
            "derive_title": "分类原则+意义",
            "derive": """<li><span class="pt">① 审题：</span>两部分：分类原则+学习分类的意义。</li>
<li><span class="pt">② 原则：</span>三条——<b>不重不漏</b>（不重叠不遗漏）、<b>标准统一</b>（同一标准）、<b>层次分明</b>（逐级分类）。</li>
<li><span class="pt">③ 意义：</span>三条——培养<b>逻辑思维</b>、<b>化繁为简</b>（复杂问题分而治之）、<b>全面思考</b>。</li>""",
            "full": """<p><b>分类的原则：</b></p>
<ol>
<li><b>不重不漏。</b>各类之间不重叠，所有情况被覆盖。</li>
<li><b>标准统一。</b>每次分类按同一标准进行。</li>
<li><b>层次分明。</b>多级分类逐级进行，不跨级混分。</li>
</ol>
<p><b>学习分类的意义：</b></p>
<ol>
<li><b>培养逻辑思维能力。</b>分类需要严密逻辑，有助于培养条理性。</li>
<li><b>化繁为简解决问题。</b>复杂问题分类后逐一解决。例：含参数不等式需分类讨论。</li>
<li><b>培养全面思考习惯。</b>分类要求不遗漏，养成全面严谨的思维品质。</li>
</ol>""",
            "exam": """<p>原则：不重不漏、标准统一、层次分明。意义：培养逻辑、化繁为简、全面思考。</p>""",
            "life": """<p>原则<span class="pk">不重不漏、标准统一</span>；意义<span class="pk">逻辑、化繁、全面</span>。</p>""",
            "tips": """<li>原则口诀"不重不漏标准统一层次分明"；</li>
<li>意义每条带一个例子更得分。</li>""",
        },
        "q13": {
            "title": "概率和频率的区别与联系",
            "origin": "结合抛掷硬币的试验，简述概率和频率的区别与联系。",
            "derive_title": "频率vs概率",
            "derive": """<li><span class="pt">① 审题：</span>结合抛掷硬币说明区别和联系。</li>
<li><span class="pt">② 区别：</span>频率是<b>经验值</b>（每次试验可能不同），概率是<b>理论值</b>（固有属性、唯一确定）。</li>
<li><span class="pt">③ 联系：</span>大量试验中频率<b>趋于稳定</b>，稳定值≈概率。抛硬币次数越多频率越接近0.5。</li>""",
            "full": """<p><b>区别：</b></p>
<ol>
<li>频率是经验值，通过实际试验统计得到，随试验不同而变化；概率是理论值，是事件发生的固有属性，唯一确定。</li>
<li>频率具有随机性，同样次数的重复试验频率可能不同；概率具有确定性。</li>
</ol>
<p><b>联系：</b></p>
<ol>
<li>频率是概率的估计。大量试验中频率趋于稳定，稳定值即为概率。如抛掷硬币次数增加，"正面向上"频率越来越接近0.5。</li>
<li>概率是频率的理论极限（大数定律）。</li>
<li>频率为概率提供经验支持，通过试验可验证理论概率。</li>
</ol>""",
            "exam": """<p>区别：频率经验值（变），概率理论值（不变）。联系：大量试验频率趋近概率（抛硬币频率→0.5）。</p>""",
            "life": """<p>频率<span class="pk">变的</span>，概率<span class="pk">不变的</span>；大量试验频率<span class="pk">趋近</span>概率。</p>""",
            "tips": """<li>核心区别：经验值vs理论值、变化vs确定；</li>
<li>抛硬币是经典例子，频率越来越接近0.5。</li>""",
        },
    },
    "2022上": {
        "q12": {
            "title": "研究椭圆几何性质的两种方法",
            "origin": "简述研究椭圆几何性质的两种方法。",
            "derive_title": "代数法vs几何法",
            "derive": """<li><span class="pt">① 审题：</span>两种方法，每种说明怎么做+研究什么。</li>
<li><span class="pt">② 代数法：</span>利用标准方程x²/a²+y²/b²=1，通过代数运算研究范围、对称性、顶点、离心率。优点是<b>精确可算</b>。</li>
<li><span class="pt">③ 几何法：</span>利用定义和图象，研究到焦点距离范围、焦点弦性质、光学性质等。优点是<b>直观</b>。</li>""",
            "full": """<ol>
<li><b>代数方法（利用标准方程）。</b>通过标准方程x²/a²+y²/b²=1，用代数手段研究：范围（|x|≤a,|y|≤b）、对称性（关于坐标轴和原点对称）、顶点、离心率（e=c/a）。优点是精确、可计算。</li>
<li><b>几何方法（利用定义和图象）。</b>利用椭圆定义和几何直观研究：椭圆上点到焦点距离的范围、焦点弦性质、光学性质（从一焦点发出的光经椭圆反射后过另一焦点）。优点是直观、有助于理解本质。</li>
</ol>""",
            "exam": """<p>①代数法（标准方程→范围/对称性/顶点/离心率）；②几何法（定义和图象→距离/光学性质）。</p>""",
            "life": """<p><span class="pk">代数法</span>（方程算性质）、<span class="pk">几何法</span>（定义看直观）。</p>""",
            "tips": """<li>两种方法核心区别：代数法精确可算、几何法直观易懂；</li>
<li>每种方法举出具体研究的性质。</li>""",
        },
        "q13": {
            "title": "习题设计意图",
            "origin": "简述在教材的教学设计内容中设置习题的设计意图（答出两条即可）。",
            "derive_title": "习题设计意图",
            "derive": """<li><span class="pt">① 审题：</span>答出两条设计意图即可，每条一句话+目的。</li>
<li><span class="pt">② 意图1：</span><b>巩固知识应用</b>——通过练习巩固基本不等式，训练代数变形能力。</li>
<li><span class="pt">③ 意图2：</span><b>培养逻辑推理</b>——证明题训练严谨推理，从已知步步有据推出结论。</li>""",
            "full": """<ol>
<li><b>巩固基本不等式的应用。</b>通过练习运用基本不等式证明不等式，巩固不等式证明的基本方法，训练代数变形能力，让学生灵活运用不等式工具。</li>
<li><b>培养逻辑推理能力。</b>通过证明题训练严谨的逻辑推理——从已知条件出发，步步有据地推出结论，发展演绎推理素养，养成规范的数学书写习惯。</li>
</ol>""",
            "exam": """<p>①巩固知识应用（训练代数变形）；②培养逻辑推理（严谨推理习惯）。</p>""",
            "life": """<p><span class="pk">巩固知识</span>、<span class="pk">培养推理</span>。</p>""",
            "tips": """<li>答两条即可，每条一句话+目的说明。</li>""",
        },
    },
    "2021下": {
        "q12": {
            "title": "四基和四能",
            "origin": '回答"四基"和"四能"分别是什么。',
            "derive_title": "四基四能背记",
            "derive": """<li><span class="pt">① 审题：</span>背记题，分别写出"四基"和"四能"。</li>
<li><span class="pt">② 四基：</span>基础<b>知识</b>（概念定理）、基本<b>技能</b>（运算作图）、基本<b>思想</b>（抽象推理建模）、基本<b>活动经验</b>（探究应用合作）。</li>
<li><span class="pt">③ 四能：</span>发现和<b>提出</b>问题的能力、分析和<b>解决</b>问题的能力。（注意：四能实际是"两能两步"，但习惯称四能）</li>""",
            "full": """<p><b>"四基"是指：</b></p>
<ol>
<li><b>基础知识</b>——数学中的概念、定理、公式、法则等。</li>
<li><b>基本技能</b>——运算、作图、推理、数据处理等操作技能。</li>
<li><b>基本思想</b>——数学抽象、逻辑推理、数学建模、直观想象等思想方法。</li>
<li><b>基本活动经验</b>——学生在数学活动中积累的探究、应用、合作经验。</li>
</ol>
<p><b>"四能"是指：</b></p>
<ol>
<li><b>发现和提出问题的能力</b>——从情境中发现并提出数学问题。</li>
<li><b>分析和解决问题的能力</b>——运用数学知识和方法分析解决问题。</li>
</ol>""",
            "exam": """<p>四基＝基础知识、基本技能、基本思想、基本活动经验。四能＝发现提出问题、分析解决问题。</p>""",
            "life": """<p>四基<span class="pk">知识、技能、思想、经验</span>；四能<span class="pk">发现提出、分析解决</span>。</p>""",
            "tips": """<li>四基四能是课标核心术语，必须背准；</li>
<li>四基=知识技能思想经验，四能=发现提出+分析解决。</li>""",
        },
        "q13": {
            "title": "简单随机抽样和分层随机抽样",
            "origin": "结合实例，简述什么是简单随机抽样和分层随机抽样。",
            "derive_title": "两种抽样方法对比",
            "derive": """<li><span class="pt">① 审题：</span>分别简述两种抽样方法+各举一个实例。</li>
<li><span class="pt">② 简单随机：</span>每个个体被抽到的概率<b>相等</b>，例：抽签法。</li>
<li><span class="pt">③ 分层随机：</span>总体分层后<b>按比例</b>从各层抽取，保证各层有代表性，例：按年级比例抽样。</li>""",
            "full": """<p><b>简单随机抽样：</b>从总体N个个体中，逐个不放回地抽取n个个体，每个个体被抽到的概率相等（均为n/N）。例：从50名学生中用抽签法抽取5名参加座谈会，每名学生被抽到的概率均为5/50=1/10。</p>
<p><b>分层随机抽样：</b>当总体由差异明显的若干层组成时，按各层个体数占总体的比例，从各层中独立地进行简单随机抽样。例：调查全校1000名学生（高一400人、高二350人、高三250人），按比例分别抽取40、35、25人，保证各年级都有代表性。</p>""",
            "exam": """<p>简单随机＝每个个体等概率抽取（抽签法）。分层随机＝按层比例分别抽取（各层有代表性）。</p>""",
            "life": """<p>简单随机<span class="pk">等概率</span>；分层<span class="pk">按比例</span>。</p>""",
            "tips": """<li>核心区别：简单随机=等概率，分层=按比例保证代表性；</li>
<li>每种抽样都要举一个具体例子。</li>""",
        },
    },
    "2021上": {
        "q12": {
            "title": "课堂留白的必要性及意义",
            "origin": '请谈谈课堂留白的必要性及其意义。',
            "derive_title": "必要性+意义两部分",
            "derive": """<li><span class="pt">① 审题：</span>两部分——必要性（为什么需要留白）+意义（留白有什么价值）。</li>
<li><span class="pt">② 必要性：</span>思维需要时间加工、避免灌输式教学形成依赖。</li>
<li><span class="pt">③ 意义：</span>促进深度理解、培养思维能力、激发主动性、暴露思维障碍。</li>""",
            "full": """<p><b>必要性：</b></p>
<ol>
<li><b>思维需要时间。</b>数学问题的理解和解题思路的形成需要时间，没有足够思考时间就无法真正参与。</li>
<li><b>避免灌输式教学。</b>立即讲解学生来不及独立思考，容易形成被动接受的依赖心理。</li>
</ol>
<p><b>意义：</b></p>
<ol>
<li><b>促进深度理解。</b>学生经历"困惑—探索—顿悟"的思维过程，加深对知识的理解。</li>
<li><b>培养思维能力。</b>独立思考是发展逻辑推理和创新思维的前提。</li>
<li><b>激发学习主动性。</b>从被动听讲转为主动探究，提高课堂参与度。</li>
<li><b>暴露思维障碍。</b>学生在思考中暴露的错误和困惑为教师调整教学提供反馈。</li>
</ol>""",
            "exam": """<p>必要：思维需时间、避免灌输。意义：深度理解、培养思维、激发主动、暴露问题。</p>""",
            "life": """<p>必要<span class="pk">思维需时间</span>；意义<span class="pk">深度理解、培养思维、激发主动</span>。</p>""",
            "tips": """<li>从必要性和意义两方面作答，各写2-4点；</li>
<li>每点一句话即可，不需要展开太多。</li>""",
        },
        "q13": {
            "title": "指数函数模型",
            "origin": "给出指数函数模型的两个实际背景，分别写出其对应的函数解析式，并简述指数函数模型的特点。",
            "derive_title": "两个背景+特点",
            "derive": """<li><span class="pt">① 审题：</span>三部分——两个背景（带解析式）+特点。</li>
<li><span class="pt">② 背景：</span>种群增长（N₀·2ᵗ，细菌分裂）、放射衰减（m₀·(1/2)ᵗ，半衰期）。</li>
<li><span class="pt">③ 特点：</span>变化率与当前值成正比（dy/dt=ky）、增长/衰减快、适用广。</li>""",
            "full": """<p><b>实际背景1：</b>种群增长问题。某种细菌每小时分裂一次（数量翻倍），初始数量为N₀，t小时后数量为N(t)=N₀·2ᵗ。</p>
<p><b>实际背景2：</b>放射物衰减问题。某放射性物质每经过一个半衰期质量减半，初始质量为m₀，经过t个半衰期后剩余质量为m(t)=m₀·(1/2)ᵗ。</p>
<p><b>指数函数模型的特点：</b></p>
<ol>
<li><b>变化率与当前值成正比。</b>即dy/dt=ky，这是指数增长/衰减的核心特征。</li>
<li><b>增长/衰减速度快。</b>指数增长比任何多项式增长都快。</li>
<li><b>适合描述自然现象。</b>广泛适用于种群增长、放射性衰变、复利计算、传染病传播等。</li>
</ol>""",
            "exam": """<p>背景：①种群增长N₀·2ᵗ；②放射衰减m₀·(1/2)ᵗ。特点：变化率与当前值成正比、增长快、适用广。</p>""",
            "life": """<p>背景<span class="pk">种群增长、放射衰减</span>；特点<span class="pk">变化率与当前值成正比</span>。</p>""",
            "tips": """<li>两个背景要写出函数解析式；</li>
<li>核心特点：变化率与当前值成正比（dy/dt=ky）。</li>""",
        },
    },
    "2020下": {
        "q12": {
            "title": "函数是课程主线之一的原因",
            "origin": "简述为什么函数是普通高中数学课程的主线之一。",
            "derive_title": "函数主线四条理由",
            "derive": """<li><span class="pt">① 审题：</span>简述函数是主线的原因，列举理由。</li>
<li><span class="pt">② 四条理由：</span><b>贯穿各模块</b>（方程/数列/导数都离不开函数）→<b>建模核心工具</b>（描述变化规律）→<b>体现数学本质</b>（变量依赖关系）→<b>贯穿认知发展</b>（初中到大学不断深化）。</li>""",
            "full": """<ol>
<li><b>贯穿高中数学各模块。</b>函数与方程、不等式、数列、三角、导数、概率统计等都有密切联系，是连接各知识板块的纽带。</li>
<li><b>函数是数学建模的核心工具。</b>现实世界中的变化规律大量可用函数描述，是数学建模活动的基础工具。</li>
<li><b>函数思想体现数学本质。</b>函数揭示了变量之间的依赖关系，是数学抽象的重要载体。</li>
<li><b>函数学习贯穿认知发展全过程。</b>从初中变量函数到高中集合映射函数再到大学微积分，概念不断深化。</li>
</ol>""",
            "exam": """<p>①贯穿各模块（方程/数列/导数）；②建模核心工具；③体现数学本质（变量依赖）；④贯穿认知发展。</p>""",
            "life": """<p><span class="pk">贯穿各模块、建模工具、体现本质、认知发展</span>。</p>""",
            "tips": """<li>四条理由每条一句话即可；</li>
<li>提到具体模块（方程/数列/导数）更得分。</li>""",
        },
        "q13": {
            "title": "数学运算的基本内涵",
            "origin": "简述数学运算的基本内涵。",
            "derive_title": "运算五步框架",
            "derive": """<li><span class="pt">① 审题：</span>简述数学运算的基本内涵，背记题。</li>
<li><span class="pt">② 五步框架：</span><b>理解</b>运算对象→<b>掌握</b>运算法则→<b>选择</b>运算方法→<b>实施</b>运算过程→<b>反思</b>运算结果。五步递进，不可打乱。</li>""",
            "full": """<p>数学运算是指在明晰运算对象的基础上，依据运算法则解决数学问题的过程。其基本内涵包括：</p>
<ol>
<li><b>理解运算对象。</b>明确运算涉及的对象是什么（数、式、向量、矩阵等），理解其概念和性质。</li>
<li><b>掌握运算法则。</b>熟练掌握各种运算的法则、公式和定律。</li>
<li><b>选择运算方法。</b>根据问题特点选择恰当、简洁的运算路径。</li>
<li><b>实施运算过程。</b>准确、有序地执行运算的每一步骤。</li>
<li><b>反思运算结果。</b>对运算结果进行检验，判断合理性，优化运算过程。</li>
</ol>""",
            "exam": """<p>①理解对象→②掌握法则→③选择方法→④实施运算→⑤反思结果。</p>""",
            "life": """<p><span class="pk">理解→法则→方法→实施→反思</span>。</p>""",
            "tips": """<li>五步是固定框架，按顺序写不可打乱；</li>
<li>口诀"理解法则选择实施反思"。</li>""",
        },
    },
}

if __name__ == "__main__":
    count = 0
    for year_short, year_data in DATA.items():
        year_dir = os.path.join(BASE, year_short)
        for qnum in ["12", "13"]:
            qdata = year_data.get(f"q{qnum}")
            if not qdata:
                continue
            html = TEMPLATE.format(
                year=year_short,
                qnum=qnum,
                title=qdata["title"],
                origin=qdata["origin"],
                derive_title=qdata["derive_title"],
                derive_content=qdata["derive"],
                full_meta="完整答案·7分",
                exam_meta="精简版·5-6分",
                life_meta="关键词·3-4分",
                full_answer=qdata["full"],
                exam_answer=qdata["exam"],
                life_answer=qdata["life"],
                tips=qdata["tips"],
            )
            filepath = os.path.join(year_dir, f"q{qnum}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            count += 1
            print(f"  {year_short}/q{qnum}.html 已生成")

    print(f"\n全部 {count} 个文件已生成")
