#!/usr/bin/env python3
"""学习计划表生成器：md 为唯一权威底，整张渲染 学习计划表.html（倒计时/今日卡/框勾选/图例）。
用法：python3 gen_plan.py   之后跑 make_longimg.py 重渲 01 长图。
表结构：| 日期 | 当天计划（🌅早 / 🏢公司404·301 / 🌙晚） | 完成情况（纯勾选，例外才备注） |"""
import re, html, os
D=os.path.dirname(os.path.abspath(__file__))
md=open(os.path.join(D,"学习计划表.md"),encoding="utf-8").read()
def fmt(t):  # escape 后把 **xx** 变粗体
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(t))

rows=[]
for line in md.split("\n"):
    m=re.match(r"^\| (\d+/\d+) (.+?) \|(.+?)\|(.+?)\|\s*$", line)
    if not m: continue
    date,ctype,plan,act=[x.strip() for x in m.groups()]
    wk="周末" in ctype
    # 把"还债日"等额外标注拆出来，放到日期下方换行显示
    extra=''
    me=re.match(r'^(.+?)\s+(\*\*(.+?)\*\*)$', ctype)
    if me:
        ctype=me.group(1)
        extra='<br><b>%s</b>'%me.group(3)
    # 从完成列提取备注（注:xxx）
    note_m=re.search(r'(注:.+)', act)
    note=fmt(note_m.group(1)) if note_m else ''
    if note_m: act=act[:note_m.start()].strip()
    # 按时段符号拆成 <ul><li> 列表（计划列用）
    def link_for(seg):
        """根据计划项内容匹配对应资料文件路径"""
        s=re.sub(r'^[🌅🏢🌙☀️]\s*','',seg).strip()
        R='..'   # 相对路径：html 在 00_考试总览/ 下，项目根是 ../
        L='.'    # 同目录(00_考试总览/)
        AU=os.path.join(L,'通勤音频')
        T301=os.path.join(R,'301_综合素质/301.05答题模板升级版/答题模板升级版.html')
        T404CARD=os.path.join(R,'404_高中数学学科/404.05速记卡/404速记卡.html')
        T404FRAME=os.path.join(R,'404_高中数学学科/404.05速记卡/404主观题框架.html')
        audio_map={'01':'01_三观师德框架_朗读原文.html','02':'02_2020下解析_朗读原文.html',
                   '03':'03_作文升级版_朗读原文.html','04':'04_301立意清单_朗读原文.html',
                   '05':'05_404速记卡_朗读原文.html','06':'06_主观题框架_朗读原文.html'}
        audio_dir={'01':AU,'02':AU,'03':AU,'04':AU,
                   '05':os.path.join(R,'404_高中数学学科/404.05速记卡'),
                   '06':os.path.join(R,'404_高中数学学科/404.05速记卡')}
        # 通勤音频编号 01-06（含组合如 01+03、03+04）
        am=re.match(r'^(0[1-6])(\+0[1-6])*$', s)
        if am:
            n=s[:2]
            return os.path.join(audio_dir.get(n,AU), audio_map.get(n,''))
        # 01框架 / 06框架 = 音频01/06 + 框架
        if re.match(r'^0[1-6]框架', s):
            n=s[:2]
            return os.path.join(audio_dir.get(n,AU), audio_map.get(n,''))
        # 02朗读 / 02 朗读（无前导0）
        am2=re.match(r'^0?([1-6])\s*(朗读|朗读\()', s)
        if am2:
            n='0'+am2.group(1)
            return os.path.join(audio_dir.get(n,AU), audio_map.get(n,''))
        # 立意
        if '立意' in s:
            return os.path.join(AU,'04_301立意清单_朗读原文.html')
        # 301 内容（含 301 — 免维护）
        if '301' in s:
            if '框架' in s or '模板' in s or '默写' in s or '成文' in s or '材料' in s or '偏题' in s or '单选' in s or '整卷' in s or '—' in s:
                return T301
        # 301 三观/师德/教师观/学生观/教育观
        if '三观' in s or '师德' in s or '教师观' in s or '学生观' in s or '教育观' in s:
            return T301
        # 404 速记卡（含卡背、卡·簇、卡复习、错题上卡）
        if '卡' in s and ('簇' in s or '背' in s or '速记' in s or '复习' in s or '错题' in s):
            return T404CARD
        # 404 主观题框架（含 06框架、01框架）
        if '框架' in s and ('404' in s or '案例' in s or '设计' in s or '五类' in s or '终背' in s or '听框架' in s):
            return T404FRAME
        # 404 真题分卷（4位或2位年份，如 2020下/20下/21上/25上）
        vm=re.search(r'(?:(20)?(\d{2}))\s*([上下])', s)
        if vm:
            y=('20'+vm.group(2)) if not vm.group(1) else vm.group(1)
            d=vm.group(3)
            fp=os.path.join(R,'404_高中数学学科/真题分卷/%s%s'%(y,d))
            if '解析' in s:
                return os.path.join(fp,'解析.html')
            elif '文本' in s:
                return os.path.join(fp,'真题文本.html')
            else:
                return os.path.join(fp,'真题文本.html')
        # 03 作文
        if '作文' in s:
            return os.path.join(AU,'03_作文升级版_朗读原文.html')
        # 论述354字
        if '论述' in s or '354' in s:
            return os.path.join(fp if vm else R,'真题文本.txt') if vm else T404FRAME
        # 考场时间分配
        if '时间' in s:
            return os.path.join(L,'考场时间分配.html')
        # 备考/放松/文具 = 无资料
        if '放松' in s or '文具' in s or '准考证' in s:
            return ''
        return ''
    def to_list(s):
        segs=re.split(r' (?=🌅|🏢|🌙|☀️)', s.strip())
        items=[]
        for x in segs:
            if not x.strip(): continue
            link=link_for(x)
            txt=re.sub(r'^([🌅🏢🌙☀️])\s*',r'\1&nbsp;&nbsp;',fmt(x)) if re.match(r'^[🌅🏢🌙☀️]',x.strip()) else fmt(x)
            if link:
                items.append('<li class="seg-li" title="%s"><a href="%s" target="_blank" style="color:inherit;text-decoration:none">%s</a></li>'%(html.escape(x.strip()),html.escape(link),txt))
            else:
                items.append('<li class="seg-li" title="%s">%s</li>'%(html.escape(x.strip()),txt))
        return '<ul class="seg" style="margin:0;padding:0;list-style:none">%s</ul>'%(''.join(items))
    # 完成列：同样按时段拆成列表（一一对应），但去掉时段 icon 只留勾选
    def to_act_list(s):
        segs=re.split(r' (?=🌅|🏢|🌙|☀️)', s.strip())
        def clean(seg):
            t=re.sub(r'^[🌅🏢🌙☀️]\s*','',seg).strip()  # 去时段 icon
            t=re.sub(r'^[43]\s*','',t).strip()          # 去科目编号 4/3
            t=re.sub(r'^🏠\s*','',t).strip()             # 去家标识
            t=re.sub(r'^⬜\s*🏠⬜','⬜',t)               # ⬜🏠⬜ → ⬜
            t=re.sub(r'🏠','',t).strip()                 # 去残余 🏠
            return fmt(t) if t else '⬜'
        lis=''.join('<li class="seg-li" title="%s">%s</li>'%(html.escape(x.strip()),clean(x)) for x in segs if x.strip())
        return '<ul class="seg" style="margin:0;padding:0;list-style:none">%s</ul>'%lis
    rows.append('<tr%s data-date="%s"><td>%s · %s%s</td><td style="padding:0">%s</td><td class="act-col" style="font-size:12px;padding:0">%s</td><td class="note-col" style="font-size:12px;padding:6px 8px">%s</td></tr>'%(
        ' class="we"' if wk else '',date,date,fmt(ctype),extra,to_list(plan),to_act_list(act),note))

table='<table>\n<tr><th>日期</th><th>当天计划（🌅早通勤 / 🏢公司＝404·301 / 🌙晚通勤）</th><th>完成情况</th><th>备注</th></tr>\n'+"\n".join(rows)+"\n</table>"

# JS 列表渲染函数（计划列 + 完成列去 icon）（提到 f-string 外避免反斜杠问题）
js_multi = "function toList(s){var segs=s.split(/ (?=🌅|🏢|🌙|☀️)/);return '<ul class=\"seg\" style=\"margin:0;padding:0;list-style:none\">'+segs.map(function(x){return '<li style=\"display:block;border-bottom:1px solid #e0e0e0;padding:4px 8px;margin:0\"><b>'+x+'</b></li>'}).join('')+'</ul>';}"
js_act_list = "function toActList(s){var segs=s.split(/ (?=🌅|🏢|🌙|☀️)/).map(function(x){return x.replace(/^[🌅🏢🌙☀️]\\s*/,'').replace(/^[43]\\s*/,'').replace(/^🏠\\s*/,'').replace(/⬜\\s*🏠⬜/,'⬜').replace(/🏠/g,'').trim()||'⬜';});return '<ul class=\"seg\" style=\"margin:0;padding:0;list-style:none\">'+segs.map(function(x){return '<li style=\"display:block;border-bottom:1px solid #e0e0e0;padding:4px 8px;margin:0\">'+x+'</li>'}).join('')+'</ul>';}"

H=f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>学习计划表 v4 · 二战补差版</title>
<style>
  :root{{--pink:#ffdeeb;--blue:#e8f4fd;--yellow:#fff8c6;--ink:#2b2b2b;--line:#eee}}
  *{{box-sizing:border-box}}
  body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);max-width:900px;margin:0 auto;padding:24px 16px 60px;line-height:1.65}}
  h1{{font-size:25px;border-bottom:3px solid #ff7ab8;padding-bottom:10px}}
  h1 small{{font-size:13px;color:#888;font-weight:normal}}
  h2{{font-size:18px;margin:28px 0 10px;padding-left:10px;border-left:5px solid #ff7ab8}}
  .card{{border-radius:10px;padding:13px 16px;margin:10px 0;border:1px solid var(--line);page-break-inside:avoid}}
  .pink{{background:var(--pink)}}.blue{{background:var(--blue)}}.yellow{{background:var(--yellow)}}
  .tag{{display:inline-block;font-size:12px;font-weight:700;background:#fff;border-radius:20px;padding:2px 10px;margin-bottom:6px;border:1px solid rgba(0,0,0,.12)}}
  table{{width:100%;border-collapse:collapse;margin:8px 0;font-size:13px}}
  th,td{{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}}
  .seg li:last-child{{border-bottom:none !important}}
  .seg-li{{display:block;border-bottom:1px solid #e0e0e0;padding:4px 8px;margin:0;height:28px;line-height:20px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .seg-li:has(a):hover{{background:#fffbe6}}
  .seg-li a{{text-decoration:none;color:inherit}}
  th{{background:#f9f9f9}}
  tr.we{{background:#f3fbf3}}
  tr.today{{background:#ffe9a8;outline:3px solid #ffb400;outline-offset:-2px}}
  tr.today td:first-child{{font-weight:800}}
  tr.today td:first-child::after{{content:"\\A📍今天";white-space:pre;color:#d9480f;font-weight:800}}
  mark{{background:var(--yellow);padding:0 3px;border-radius:3px}}
  .must{{color:#d6336c;font-weight:700}}
  ol,ul{{padding-left:22px}}li{{margin:4px 0}}
  code{{background:#f1f1f1;border-radius:4px;padding:1px 5px;font-size:12.5px}}
  footer{{margin-top:34px;color:#999;font-size:12px;text-align:center}}
  @media print{{body{{padding:0}}}}
</style>
</head>
<body>
<h1>学习计划表 v4 · 二战补差版 <small>制表 2026-08-26 · 笔试 9/12 · 只考 301 + 404</small></h1>

<div class="card yellow" style="text-align:center;font-size:17px">⏳ 距 9/12 笔试还有 <b id="cd" style="font-size:26px;color:#d6336c">--</b> 天</div>

<div class="card yellow" id="today-focus" style="border:2px solid #ffb400">
  <span class="tag" style="background:#ffb400;color:#fff"> 今天计划 · 完成打勾</span>
  <div id="tf-body" style="font-size:15px"></div>
</div>

<div class="card pink">
  <span class="tag">🩺 上次怎么死的（66 / 50）</span>
  <ul style="margin:6px 0 0;">
    <li><b>301＝66</b>：作文没写够 1000 字 → <mark>速度与字数</mark>问题，不是知识问题。</li>
    <li><b>404＝50</b>：计算没思路、主观无框架 → <mark>公式记忆 + 主观框架</mark>双缺。</li>
    <li>结论：6 成时间给 404（速记卡+框架）；301 每天 15 分钟维护＋作文速度训练；科二 78 已过。</li>
  </ul>
</div>

<div class="card blue">
  <span class="tag">⚔️ 404 丢分点对策（40选+35简+10解+15论+20案+30设）</span>
  <table>
    <tr><th>丢分点</th><th>分值</th><th>症状</th><th>对策</th></tr>
    <tr><td>单选1–6 大学数学</td><td>40</td><td>公式忘/无思路</td><td><code>404速记卡</code> 三簇晨背15分</td></tr>
    <tr><td>简答5题</td><td>35</td><td>不知从哪写</td><td><code>404主观题框架</code> 三句法</td></tr>
    <tr><td>案例20/设计30</td><td>50</td><td>不知从哪写</td><td>四角度套句 / 五件套套句库</td></tr>
  </table>
  主观相关约 95 分＝<span class="must">背框架性价比是刷难题的10倍</span>。
</div>

<h2>一、逐日安排（白=工作日 · 绿=周末 · <span style="background:#ffe9a8;padding:0 4px;border:1px solid #ffb400;border-radius:4px">黄=当天</span>）</h2>
{table}

<h2>二、三条新铁律</h2>
<div class="card yellow"><ol>
  <li><span class="must">404 主观＝套框架</span>：先写结论句，空白也写满五类标题。</li>
  <li><span class="must">301 作文＝先写够</span>：开考75分钟先动作文，写够1000字再回头。</li>
  <li><span class="must">公式不裸背</span>：背卡后立刻做2道单选验证。</li>
</ol></div>

<h2>三、让老师（AI）配合的事</h2>
<div class="card blue"><ul>
  <li>[已备] 301升级模板＋立意清单＋354字全稿＋音频01/03/04/05/06。</li>
  <li>[已完成8/26] 404速记卡、404主观题框架（含📚角度库＋人读版html锚点）。</li>
  <li>每天按报到时点回填完成列（工作日到岗/下班/到家；周末12/18/22点）；只打勾不解释，例外才备注；没做顺延不扣分。</li>
  <li>每讲完一卷：双写解析双档＋新音频；白天不push，下班听口令一次推。</li>
</ul></div>

<footer>md 为权威底，本 html 由 gen_plan.py 生成 · 打印 Cmd+P 存 PDF</footer>
<script>
(function(){{
  var d=new Date(), key=(d.getMonth()+1)+"/"+d.getDate();
  var row=document.querySelector('tr[data-date="'+key+'"]');
  var box=document.getElementById("tf-body");
  var exam=new Date(d.getFullYear(),8,12), now=new Date(d.getFullYear(),d.getMonth(),d.getDate());
  var days=Math.round((exam-now)/86400000);
  document.getElementById("cd").textContent = days>0?days:(days===0?"0·今天考试!":"考完");
  if(!row){{ box.innerHTML=key+" 不在排期内（9/12：先写作文，写够1000字！）"; return; }}
  row.classList.add("today");
  if(row.classList.contains("we")) row.style.background="#ffe9a8";
  var tds=row.querySelectorAll("td");
  // 按时段拆成列表显示；完成列同样拆列表但去 icon
  {js_multi}
  {js_act_list}
  var note=tds[3] ? tds[3].textContent.trim() : '';
  box.innerHTML="<b>① 今天计划：</b>"+toList(tds[1].textContent.trim())+"<br><b>② 完成勾选：</b>"+toActList(tds[2].textContent.trim())+(note? "<br><b>③ 备注：</b>"+note : "");
  row.scrollIntoView({{block:"center"}});
}})();
// 未来日期隐藏完成列和备注列内容
(function(){{
  var today=new Date();
  document.querySelectorAll('tr[data-date]').forEach(function(tr){{
    var ds=tr.dataset.date.split('/');
    var d=new Date(today.getFullYear(),parseInt(ds[0])-1,parseInt(ds[1]));
    if(d>today){{
      var ac=tr.querySelector('.act-col'), nc=tr.querySelector('.note-col');
      if(ac) ac.innerHTML='';
      if(nc) nc.innerHTML='';
    }}
  }});
}})();</script>
</body>
</html>'''
open(os.path.join(D,"学习计划表.html"),"w",encoding="utf-8").write(H)
print("rows:",len(rows)," we:",H.count('class="we"'))
