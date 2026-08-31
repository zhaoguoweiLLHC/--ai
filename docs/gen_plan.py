#!/usr/bin/env python3
"""学习计划表生成器：md 为唯一权威底，整张渲染 学习计划表.html（倒计时/今日卡/框勾选/图例）。
用法：python3 gen_plan.py   生成后 git push 即可通过 PWA 查看。
目录结构：.ai-cache/ = AI机器档(md/json)，资料/ = 人看原件(doc/pdf/img/html)，docs/通勤库/ = 通勤页面+音频。
表结构：| 日期 | 当天计划（🌅早 / 🏢公司404·301 / 🌙晚） | 完成情况（纯勾选，例外才备注） |"""
import re, html, os, json
D=os.path.dirname(os.path.abspath(__file__))  # docs/
md=open(os.path.join(D,"..",".ai-cache","00_考试总览","学习计划表.md"),encoding="utf-8").read()
def fmt(t):  # escape 后把 **xx** 变粗体
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(t))

rows=[]; rows_meta=[]
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
    R='../../'  # 从 资料/00_考试总览/ 到项目根
    LINK_MAP=[
        # (正则关键词, 链接路径, 优先级)
        (r'速记卡[A-D]簇[^＋]*', R+'资料/404_高中数学学科/404.05速记卡/404速记卡.html', 1),
        (r'404\s*速记卡[^＋]*', R+'资料/404_高中数学学科/404.05速记卡/404速记卡.html', 1),
        (r'速记卡[^＋]*', R+'资料/404_高中数学学科/404.05速记卡/404速记卡.html', 1),
        (r'主观题.*框架[^＋]*|五类框架[^＋]*|框架终背[^＋]*', R+'资料/404_高中数学学科/404.05速记卡/404主观题框架.html', 2),
        (r'301\s*作文立意[^＋]*', R+'资料/301_综合素质/301.05答题模板升级版.html', 3),
        (r'作文立意[^＋]*', R+'资料/301_综合素质/301.05答题模板升级版.html', 3),
        (r'301.*模板[^＋]*', R+'资料/301_综合素质/301.05答题模板升级版.html', 3),
        (r'301\s*材料分析[^＋]*', R+'资料/301_综合素质/301.05答题模板升级版.html', 3),
        (r'材料分析[^＋]*', R+'资料/301_综合素质/301.05答题模板升级版.html', 3),
        (r'404\s*\d{4}[上下].*第1[5-7]题[^＋]*', None, 4),  # 动态：404 2020下第17题教学设计(框架)
        (r'404\s*\d{4}[上下].*整卷[^＋]*', None, 4),  # 动态：404 2021上整卷大题
        (r'404\s*\d{4}[上下].*大题[^＋]*', None, 4),  # 动态：404 2021下整卷大题
        (r'404\s*\d{4}[上下].*单选[^＋]*', None, 4),  # 动态：404 2022上单选刷
        (r'错题录入', R+'资料/404_高中数学学科/错题本.html', 5),
        (r'总结', R+'资料/00_考试总览/每日总结.html', 6),
    ]
    def add_links(seg_text):
        """在纯文本中把关键词替换成超链接，跳过已有<a>标签内的内容"""
        for pattern, link, _ in LINK_MAP:
            if not link:
                m=re.search(r'(20\d{2}[上下])', seg_text)
                if m and re.search(pattern, seg_text):
                    y=m.group(1)
                    link=R+'资料/404_高中数学学科/真题分卷/'+y+'/解析.html'
            if link:
                # 只在不在<a>标签内的文本里匹配
                parts=re.split(r'(<a [^>]*>.*?</a>)', seg_text)
                for i,part in enumerate(parts):
                    if part.startswith('<a '): continue  # 跳过已有链接
                    if re.search(pattern, part):
                        m=re.search(pattern, part)
                        kw=m.group(0)
                        parts[i]=part.replace(kw, '<a href="%s" target="_blank">%s</a>'%(html.escape(link),kw), 1)
                        break  # 每个pattern只替换一次
                seg_text=''.join(parts)
        return seg_text
    def to_list(s):
        segs=re.split(r' (?=🌅|🏢|🌙|☀️)', s.strip())
        items=[]
        for x in segs:
            if not x.strip(): continue
            txt=re.sub(r'^([🌅🏢🌙☀️])\s*',r'\1&nbsp;&nbsp;',fmt(x)) if re.match(r'^[🌅🏢🌙☀️]',x.strip()) else fmt(x)
            # 在文本内添加多个超链接
            txt=add_links(txt)
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
    # 收集通勤任务（早通勤🌅 + 晚通勤🌙 的音频编号）
    commute_tasks=[]
    for seg in re.split(r' (?=🌅|🏢|🌙|☀️)', plan.strip()):
        seg=seg.strip()
        if not seg: continue
        slot='morning' if seg.startswith('🌅') else 'evening' if seg.startswith('🌙') else None
        if not slot: continue
        nm=re.search(r'0([1-6])', seg)
        if nm:
            commute_tasks.append({'slot':slot,'audio':'0'+nm.group(1),'text':re.sub(r'^[🌅🌙]\s*','',seg).strip()})
    rows_meta.append({'date':date,'commute_tasks':commute_tasks})

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
  table{{width:100%;border-collapse:collapse;margin:8px 0;font-size:13px;table-layout:fixed}}
  th,td{{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}}
  th:nth-child(1),td:nth-child(1){{white-space:nowrap;width:16%}}
  th:nth-child(3),td:nth-child(3){{width:12%}}
  th:nth-child(4),td:nth-child(4){{width:12%}}
  .seg li:last-child{{border-bottom:none !important}}
  .seg-li{{display:block;border-bottom:1px solid #e0e0e0;padding:4px 8px;margin:0;height:28px;line-height:20px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
  .seg-li a{{text-decoration:none;color:#1971c2}}
  .seg-li a:hover{{background:#fffbe6;border-radius:4px;text-decoration:underline}}
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
# 学习计划表 html 输出到 资料/source/
src_dir=os.path.join(D,"..","资料","00_考试总览")
os.makedirs(src_dir,exist_ok=True)
open(os.path.join(src_dir,"学习计划表.html"),"w",encoding="utf-8").write(H)

# 生成通勤任务 JSON（供 PWA 通勤页面读取）
commute=[]
for r in rows_meta:
    commute.append({"date":r["date"],"tasks":r["commute_tasks"]})
json_path=os.path.join(D,"通勤库","通勤任务.json")
open(json_path,"w",encoding="utf-8").write(json.dumps(commute,ensure_ascii=False))
print("rows:",len(rows)," we:",H.count('class="we"'))
