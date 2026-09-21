#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把所有年份的q12.html从单层参考答案改为三档tab结构"""
import re, os

BASE = "/Users/zhaoguowei/Documents/personal/教资学习-ai/生成资料/动态/404_高中数学学科/真题分卷"

# 三档tab结构的CSS和JS模板（和q15-q17一致）
TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{year} · 简答题 12-13（主观题部分）</title>
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
       padding:12px 16px;color:#555;font-size:15px;margin:12px 0;white-space:pre-line}}
  .block{{border-radius:12px;padding:14px 18px;margin:14px 0}}
  .block h3{{margin:0 0 8px;font-size:15px}}
  .k-gold{{background:var(--gold-bg);border:1px solid #f3d9a0}}
  .k-gold h3{{color:var(--gold)}}
  a{{color:#1971c2;text-decoration:underline;text-underline-offset:3px}}
  .pk{{color:var(--pink);font-weight:700}}
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
<section class="card" id="q12">
  <div class="qhead">
    <span class="badge b-jie">简答题</span>
    <h2>第 12-13 题 · 简答题（各7分）</h2>
    <span class="score">共14分</span>
  </div>
  <div class="origin">{origin}</div>
  <div class="tabs">
    <button class="tab-btn active-t" data-tab="t-full" onclick="switchTab('t-full')">🏆 满分版 <small style="font-size:11px;color:#888">完整答案·7分</small></button>
    <button class="tab-btn" data-tab="t-exam" onclick="switchTab('t-exam')">🎯 考场版 <small style="font-size:11px;color:#888">精简版·5-6分</small></button>
    <button class="tab-btn" data-tab="t-life" onclick="switchTab('t-life')">🛟 救急版 <small style="font-size:11px;color:#888">关键词·3-4分</small></button>
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

# 各年份的数据：题干、满分版答案、考场版（精简）、救急版（关键词）、得分技巧
YEARS_DATA = {
    "2025上": {
        "origin": "12. 说明二项分布的两个实例（不用计算）。\n13. 简述普通高中数学课程目标。",
        "full": """<p><b>第12题（二项分布实例）：</b>二项分布描述的是n次独立重复试验中某事件恰好发生k次的概率分布。两个实例：</p>
<ol>
<li>抛硬币：连续抛掷一枚均匀硬币n次，每次正面向上的概率为0.5，正面向上的次数服从二项分布B(n,0.5)。</li>
<li>产品检验：从一批产品中有放回地抽取n件，每件为次品的概率为p，抽到的次品数服从二项分布B(n,p)。</li>
</ol>
<p><b>第13题（课程目标）：</b>普通高中数学课程目标包括：</p>
<ol>
<li>获得必要的数学基础知识和基本技能，理解基本的数学概念和数学结论的本质。</li>
<li>体会和运用数学思想方法，发展数学学科核心素养（数学抽象、逻辑推理、数学建模、直观想象、数学运算、数据分析）。</li>
<li>提高空间想象能力、抽象概括能力、推理论证能力、运算求解能力和数据处理能力。</li>
<li>发展数学应用意识和创新意识，提高学习数学的兴趣，形成科学态度和理性精神。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①抛硬币n次，正面向上次数服从B(n,0.5)；②有放回抽取产品n件，次品数服从B(n,p)。</p>
<p><b>第13题：</b>①获得基础知识与基本技能，理解概念本质；②体会数学思想方法，发展六大核心素养；③提高空间想象、抽象概括、推理论证、运算求解、数据处理能力；④发展应用意识和创新意识，形成科学态度。</p>""",
        "life": """<p>12：抛硬币B(n,0.5)、产品检验B(n,p)。</p>
<p>13：<span class="pk">基础知识技能</span>→<span class="pk">思想方法+六大素养</span>→<span class="pk">五大能力</span>→<span class="pk">应用意识+科学态度</span>。</p>""",
        "tips": """<li>简答题分点作答，编号清晰（①②③），阅卷按点给分；</li>
<li>第12题只需举实例不用计算，答出"独立重复试验+概率固定"即可；</li>
<li>第13题课程目标是背记题，四条全写=满分，时间紧写前两条保底。</li>""",
    },
    "2024下": {
        "origin": "12. 以二次函数和一元二次方程为例，说明函数与方程的联系。\n13. 设a,b为两实数，列举出坐标(a,b)可表示的三个数学对象。",
        "full": """<p><b>第12题（函数与方程的联系）：</b></p>
<ol>
<li><b>方程的根＝函数的零点。</b>一元二次方程ax²+bx+c=0的实数根就是二次函数y=ax²+bx+c与x轴交点的横坐标。</li>
<li><b>判别式决定交点个数。</b>Δ>0两个交点两根；Δ=0一个交点等根；Δ<0无交点无实根。</li>
<li><b>函数值符号与不等式。</b>y>0对应的x范围就是ax²+bx+c>0的解集，体现"函数—方程—不等式"三位一体。</li>
</ol>
<p><b>第13题（坐标(a,b)表示的数学对象）：</b></p>
<ol>
<li><b>平面直角坐标系中的点。</b>表示平面上横坐标为a、纵坐标为b的点P(a,b)。</li>
<li><b>二维向量。</b>表示向量v=(a,b)，a为横分量，b为纵分量。</li>
<li><b>复数。</b>表示复数z=a+bi，a为实部，b为虚部。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①方程的根＝函数零点（图象与x轴交点）；②判别式Δ决定根的个数；③函数值符号对应不等式解集。</p>
<p><b>第13题：</b>①点P(a,b)；②向量(a,b)；③复数a+bi。</p>""",
        "life": """<p>12：<span class="pk">根=零点</span>、<span class="pk">Δ定根数</span>、<span class="pk">符号=不等式</span>。</p>
<p>13：<span class="pk">点</span>P(a,b)、<span class="pk">向量</span>(a,b)、<span class="pk">复数</span>a+bi。</p>""",
        "tips": """<li>第12题以二次函数为例说明，三步：零点→判别式→不等式；</li>
<li>第13题只需列举三个对象，每个一句话即可；</li>
<li>坐标的三重含义（点、向量、复数）是高频考点。</li>""",
    },
    "2024上": {
        "origin": "12. 简要说明过程评价应关注哪几个方面。\n13. 以等比数列概念教学为例，简述数学概念教学的主要环节。",
        "full": """<p><b>第12题（过程评价应关注的方面）：</b></p>
<ol>
<li><b>学生的参与度。</b>课堂参与、小组讨论、探究活动等。</li>
<li><b>学生的思维过程。</b>思考问题的方式、策略和推理过程。</li>
<li><b>学生的合作交流。</b>表达观点、倾听他人、协作解决。</li>
<li><b>学生的反思与改进。</b>发现不足并改进。</li>
<li><b>学生的情感态度。</b>兴趣、信心、毅力等。</li>
</ol>
<p><b>第13题（概念教学的主要环节）：</b>以等比数列为例：</p>
<ol>
<li><b>概念的引入。</b>从实例引入（细胞分裂1,2,4,8,…），观察共同特征。</li>
<li><b>概念的形成。</b>从实例中抽象本质属性，归纳概括出定义。</li>
<li><b>概念的明确。</b>给出严格定义，明确内涵和外延（公比q≠0）。</li>
<li><b>概念的巩固与应用。</b>通过练习判断是否为等比数列等。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①参与度；②思维过程；③合作交流；④反思改进；⑤情感态度。</p>
<p><b>第13题：</b>①引入（实例引入）；②形成（归纳概括）；③明确（严格定义）；④巩固（练习应用）。</p>""",
        "life": """<p>12：<span class="pk">参与、思维、合作、反思、情感</span>。</p>
<p>13：<span class="pk">引入→形成→明确→巩固</span>。</p>""",
        "tips": """<li>过程评价五方面可用口诀"参与思维合作反思情感"；</li>
<li>概念教学四环节是固定框架：引入→形成→明确→巩固；</li>
<li>以等比数列为例时，提到细胞分裂等具体实例更得分。</li>""",
    },
    "2023下": {
        "origin": "12. 简述逻辑推理的含义及主要推理形式。\n13. 写出复数代数运算的加法、减法、乘法、除法运算法则，并简述复数加法运算的几何意义。",
        "full": """<p><b>第12题（逻辑推理）：</b></p>
<p><b>含义：</b>从已有事实或命题出发，依据规则推出其他命题的思维过程，是数学核心素养之一。</p>
<p><b>主要推理形式：</b></p>
<ol>
<li><b>演绎推理：</b>从一般到特殊，结论必然成立（三段论）。</li>
<li><b>归纳推理：</b>从特殊到一般，包括完全归纳和不完全归纳。</li>
<li><b>类比推理：</b>根据两对象某些属性相同推断其他属性也相同，结论或然成立。</li>
</ol>
<p><b>第13题（复数运算法则）：</b>设z₁=a+bi, z₂=c+di：</p>
<ol>
<li><b>加法：</b>z₁+z₂=(a+c)+(b+d)i</li>
<li><b>减法：</b>z₁-z₂=(a-c)+(b-d)i</li>
<li><b>乘法：</b>z₁·z₂=(ac-bd)+(ad+bc)i</li>
<li><b>除法：</b>z₁/z₂=[(ac+bd)+(bc-ad)i]/(c²+d²)</li>
</ol>
<p><b>加法几何意义：</b>对应平面向量加法的<b>平行四边形法则</b>。</p>""",
        "exam": """<p><b>第12题：</b>逻辑推理＝从已有命题推出新命题。形式：①演绎（一般→特殊，必然）；②归纳（特殊→一般）；③类比（或然）。</p>
<p><b>第13题：</b>加(a+c)+(b+d)i；减(a-c)+(b-d)i；乘(ac-bd)+(ad+bc)i；除[(ac+bd)+(bc-ad)i]/(c²+d²)。加法几何意义＝<b>平行四边形法则</b>。</p>""",
        "life": """<p>12：<span class="pk">演绎（必然）、归纳、类比（或然）</span>。</p>
<p>13：加减乘除四公式；加法＝<span class="pk">平行四边形法则</span>。</p>""",
        "tips": """<li>三种推理形式的核心区别：演绎必然、归纳或然、类比或然；</li>
<li>复数四则运算法则要写全公式，不能只写文字描述；</li>
<li>加法几何意义就是向量加法的平行四边形法则，一句话搞定。</li>""",
    },
    "2023上": {
        "origin": '12. 简述长方体模型在学习直线与直线、直线与平面、平面与平面的平行和垂直位置关系中的作用。（答出两条即可）\n13. 写出高中数学中与"函数单调性"密切相关的具体知识。（答出5条即可）',
        "full": """<p><b>第12题（长方体模型的作用）：</b></p>
<ol>
<li><b>直观感知空间位置关系。</b>长方体提供丰富的线线、线面、面面位置关系实例。例：上下底面对应棱平行，侧棱与底面垂直，对立面平行。</li>
<li><b>辅助证明和推理。</b>作为验证和推理的载体，在证明空间位置关系时可借助长方体找思路、验证结论。</li>
</ol>
<p><b>第13题（与函数单调性相关的知识）：</b></p>
<ol>
<li><b>函数的图象。</b>单调性通过图象上升/下降直观体现。</li>
<li><b>导数。</b>f'(x)>0则增，f'(x)<0则减，是研究单调性的重要工具。</li>
<li><b>不等式。</b>利用单调性可比较函数值大小。</li>
<li><b>极值与最值。</b>极值点两侧单调性改变，最值依赖于单调性分析。</li>
<li><b>反函数。</b>单调函数必定存在反函数。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①直观感知（提供线线/线面/面面实例）；②辅助证明（找思路、验证结论）。</p>
<p><b>第13题：</b>①函数图象；②导数（f'>0增）；③不等式（比较函数值）；④极值最值；⑤反函数（单调↔存在反函数）。</p>""",
        "life": """<p>12：<span class="pk">直观感知</span>、<span class="pk">辅助证明</span>。</p>
<p>13：<span class="pk">图象、导数、不等式、极值、反函数</span>。</p>""",
        "tips": """<li>第12题答出两条即可，每条带例子；</li>
<li>第13题答出5条，每条一句话说明关联；</li>
<li>导数与单调性的关系是最高频考点。</li>""",
    },
    "2022下": {
        "origin": "12. 简述分类的原则和学习分类的意义。\n13. 结合抛掷硬币的试验，简述概率和频率的区别与联系。",
        "full": """<p><b>第12题（分类的原则和意义）：</b></p>
<p><b>分类原则：</b></p>
<ol>
<li><b>不重不漏。</b>各类不重叠、覆盖所有情况。</li>
<li><b>标准统一。</b>每次分类按同一标准。</li>
<li><b>层次分明。</b>多级分类逐级进行。</li>
</ol>
<p><b>学习分类的意义：</b></p>
<ol>
<li><b>培养逻辑思维能力。</b>分类需要严密逻辑。</li>
<li><b>化繁为简。</b>复杂问题分类后逐一解决。</li>
<li><b>培养全面思考习惯。</b>不遗漏任何情况。</li>
</ol>
<p><b>第13题（概率与频率）：</b></p>
<p><b>区别：</b>频率是经验值（随试验变化），概率是理论值（固有属性、唯一确定）。</p>
<p><b>联系：</b></p>
<ol>
<li>频率是概率的估计，大量试验中频率趋于稳定，稳定值即为概率。</li>
<li>概率是频率的理论极限（大数定律）。</li>
<li>频率为概率提供经验支持。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>原则：不重不漏、标准统一、层次分明。意义：培养逻辑、化繁为简、全面思考。</p>
<p><b>第13题：</b>区别：频率经验值（变），概率理论值（不变）。联系：频率→估计概率，大量试验频率趋近概率。</p>""",
        "life": """<p>12：原则<span class="pk">不重不漏、标准统一</span>；意义<span class="pk">逻辑、化繁、全面</span>。</p>
<p>13：频率<span class="pk">变的</span>，概率<span class="pk">不变的</span>；大量试验频率<span class="pk">趋近</span>概率。</p>""",
        "tips": """<li>分类原则口诀"不重不漏、标准统一、层次分明"；</li>
<li>概率vs频率核心区别：经验值vs理论值、变化vs确定；</li>
<li>抛硬币是经典例子，频率越来越接近0.5。</li>""",
    },
    "2022上": {
        "origin": "12. 简述研究椭圆几何性质的两种方法。\n13. 简述教材习题的设计意图（答出两条即可）。",
        "full": """<p><b>第12题（研究椭圆几何性质的两种方法）：</b></p>
<ol>
<li><b>代数方法（利用标准方程）。</b>通过标准方程x²/a²+y²/b²=1，用代数手段研究：范围、对称性、顶点、离心率。优点是精确可计算。</li>
<li><b>几何方法（利用定义和图象）。</b>利用椭圆定义和几何直观研究：到焦点距离范围、焦点弦性质、光学性质等。优点是直观。</li>
</ol>
<p><b>第13题（习题设计意图）：</b></p>
<ol>
<li><b>巩固基本不等式的应用。</b>训练代数变形能力，灵活运用不等式工具。</li>
<li><b>培养逻辑推理能力。</b>证明题训练严谨推理——从已知出发步步有据推出结论。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①代数法（标准方程→范围/对称性/顶点/离心率）；②几何法（定义和图象→距离/光学性质）。</p>
<p><b>第13题：</b>①巩固知识应用；②培养逻辑推理能力。</p>""",
        "life": """<p>12：<span class="pk">代数法</span>（方程算性质）、<span class="pk">几何法</span>（定义看直观）。</p>
<p>13：<span class="pk">巩固知识</span>、<span class="pk">培养推理</span>。</p>""",
        "tips": """<li>两种方法的核心区别：代数法精确可算、几何法直观易懂；</li>
<li>第13题答两条设计意图即可，每条一句话+目的。</li>""",
    },
    "2021下": {
        "origin": '12. 回答"四基"和"四能"分别是什么。\n13. 结合实例，简述什么是简单随机抽样和分层随机抽样。',
        "full": """<p><b>第12题（四基和四能）：</b></p>
<p><b>四基：</b>①基础知识（概念、定理、公式）；②基本技能（运算、作图、推理）；③基本思想（抽象、推理、建模等）；④基本活动经验（探究、应用、合作经验）。</p>
<p><b>四能：</b>①发现和提出问题的能力；②分析和解决问题的能力。</p>
<p><b>第13题（简单随机抽样和分层随机抽样）：</b></p>
<p><b>简单随机抽样：</b>从总体N个个体中逐个不放回抽取n个，每个个体被抽到的概率相等。例：从50名学生中抽签抽取5名。</p>
<p><b>分层随机抽样：</b>当总体由差异明显的层组成时，按各层个体数占比从各层独立简单随机抽样。例：全校1000名学生按年级比例抽取40+35+25人。</p>""",
        "exam": """<p><b>第12题：</b>四基＝基础知识、基本技能、基本思想、基本活动经验。四能＝发现提出问题、分析解决问题。</p>
<p><b>第13题：</b>简单随机＝每个个体等概率抽取（抽签法）。分层随机＝按层比例分别抽取（各层有代表性）。</p>""",
        "life": """<p>12：四基<span class="pk">知识、技能、思想、经验</span>；四能<span class="pk">发现提出、分析解决</span>。</p>
<p>13：简单随机<span class="pk">等概率</span>；分层<span class="pk">按比例</span>。</p>""",
        "tips": """<li>四基四能是课标核心术语，必须背准；</li>
<li>两种抽样的核心区别：简单随机＝等概率，分层＝按比例保证代表性；</li>
<li>每种抽样都要举一个具体例子。</li>""",
    },
    "2021上": {
        "origin": "12. 请谈谈课堂留白的必要性及其意义。\n13. 给出指数函数模型的两个实际背景，并简述指数函数模型的特点。",
        "full": """<p><b>第12题（课堂留白）：</b></p>
<p><b>必要性：</b></p>
<ol>
<li><b>思维需要时间。</b>理解和形成解题思路需要加工过程。</li>
<li><b>避免灌输式教学。</b>立即讲解会形成被动接受的依赖。</li>
</ol>
<p><b>意义：</b></p>
<ol>
<li><b>促进深度理解。</b>经历"困惑—探索—顿悟"的思维过程。</li>
<li><b>培养思维能力。</b>独立思考是发展逻辑推理的前提。</li>
<li><b>激发主动性。</b>从被动听讲转为主动探究。</li>
<li><b>暴露思维障碍。</b>为学生调整教学提供反馈。</li>
</ol>
<p><b>第13题（指数函数模型）：</b></p>
<p><b>背景1：</b>种群增长，N(t)=N₀·2ᵗ（细菌分裂）。</p>
<p><b>背景2：</b>放射物衰减，m(t)=m₀·(1/2)ᵗ（半衰期）。</p>
<p><b>特点：</b>①变化率与当前值成正比（dy/dt=ky）；②增长/衰减速度快；③适合描述自然现象。</p>""",
        "exam": """<p><b>第12题：</b>必要性：思维需时间、避免灌输。意义：深度理解、培养思维、激发主动、暴露问题。</p>
<p><b>第13题：</b>背景：①种群增长N₀·2ᵗ；②放射衰减m₀·(1/2)ᵗ。特点：变化率与当前值成正比、增长快、适用广。</p>""",
        "life": """<p>12：必要<span class="pk">思维需时间</span>；意义<span class="pk">深度理解、培养思维、激发主动</span>。</p>
<p>13：背景<span class="pk">种群增长、放射衰减</span>；特点<span class="pk">变化率与当前值成正比</span>。</p>""",
        "tips": """<li>课堂留白从必要性和意义两方面作答，各写2-3点；</li>
<li>指数函数模型两个背景要写出函数解析式；</li>
<li>核心特点：变化率与当前值成正比（dy/dt=ky）。</li>""",
    },
    "2020下": {
        "origin": "12. 简述为什么函数是普通高中数学课程的主线之一。\n13. 简述数学运算的基本内涵。",
        "full": """<p><b>第12题（函数是课程主线的原因）：</b></p>
<ol>
<li><b>贯穿各模块。</b>函数与方程、不等式、数列、三角、导数等都有联系，是连接各知识板块的纽带。</li>
<li><b>数学建模的核心工具。</b>现实变化规律可用函数描述，是建模活动的基础工具。</li>
<li><b>体现数学本质。</b>函数揭示变量依赖关系，是数学抽象的重要载体。</li>
<li><b>贯穿认知发展全过程。</b>从初中变量函数到高中集合映射函数再到大学微积分，概念不断深化。</li>
</ol>
<p><b>第13题（数学运算的基本内涵）：</b></p>
<ol>
<li><b>理解运算对象。</b>明确运算涉及的对象（数、式、向量等）。</li>
<li><b>掌握运算法则。</b>熟练掌握法则、公式和定律。</li>
<li><b>选择运算方法。</b>根据特点选择恰当简洁的运算路径。</li>
<li><b>实施运算过程。</b>准确有序执行每一步骤。</li>
<li><b>反思运算结果。</b>检验结果合理性，优化运算过程。</li>
</ol>""",
        "exam": """<p><b>第12题：</b>①贯穿各模块（方程/数列/导数）；②建模核心工具；③体现数学本质（变量依赖）；④贯穿认知发展。</p>
<p><b>第13题：</b>①理解对象→②掌握法则→③选择方法→④实施运算→⑤反思结果。</p>""",
        "life": """<p>12：<span class="pk">贯穿各模块、建模工具、体现本质、认知发展</span>。</p>
<p>13：<span class="pk">理解→法则→方法→实施→反思</span>。</p>""",
        "tips": """<li>函数主线四条理由，每条一句话即可；</li>
<li>数学运算五步是固定框架，按顺序写不可打乱；</li>
<li>运算五步口诀："理解法则选择实施反思"。</li>""",
    },
}

if __name__ == "__main__":
    for year_short, data in YEARS_DATA.items():
        filepath = os.path.join(BASE, year_short, "q12.html")
        html = TEMPLATE.format(
            year=year_short,
            origin=data["origin"],
            full_answer=data["full"],
            exam_answer=data["exam"],
            life_answer=data["life"],
            tips=data["tips"],
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  {year_short}/q12.html 已更新")

    print(f"\n全部 {len(YEARS_DATA)} 个年份的 q12.html 已改为三档格式")
