#!/usr/bin/env python3
"""通用 txt/md → html 转换器：统一风格，人读版。
用法：python3 txt2html.py <源文件路径> [标题]
输出：同目录下同名 .html"""
import sys, os, re, html

def convert(src, title=None):
    D = os.path.dirname(os.path.abspath(src))
    base = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(D, base + '.html')
    if not title:
        title = base
    ext = os.path.splitext(src)[1]
    raw = open(src, encoding='utf-8').read()

    lines = raw.split('\n')
    body_parts = []

    for line in lines:
        line = line.rstrip('\r')
        if not line.strip():
            body_parts.append('')
            continue
        # Markdown 标题
        if ext == '.md':
            m = re.match(r'^(#{1,3})\s+(.+)', line)
            if m:
                lvl = len(m.group(1))
                body_parts.append('<h%d>%s</h%d>' % (lvl, fmt(m.group(2)), lvl))
                continue
            # 分割线 ────
            if re.match(r'^─{6,}', line):
                body_parts.append('<hr>')
                continue
            # 引用 >
            m = re.match(r'^>\s*(.+)', line)
            if m:
                body_parts.append('<blockquote>%s</blockquote>' % fmt(m.group(1)))
                continue
            # 列表项
            m = re.match(r'^(\s*)[-*]\s+(.+)', line)
            if m:
                body_parts.append('<li>%s</li>' % fmt(m.group(2)))
                continue
        # Markdown 表格：| xxx | yyy | 格式
        if re.match(r'^\|.*\|\s*$', line):
            body_parts.append('TABLE:'+line)
            continue
        # 通用：全角空格开头 = 缩进说明
        if line.startswith('　'):
            body_parts.append('<p style="margin:2px 0;padding-left:1.5em;color:#555">%s</p>' % fmt(line.strip()))
            continue
        # 普通段落
        body_parts.append('<p style="margin:4px 0">%s</p>' % fmt(line))

    # 组装列表：连续 <li> 包进 <ul>
    # 组装表格：连续 TABLE: 行转为 <table>
    body_html = []
    in_ul = False
    in_table = False
    for p in body_parts:
        if p.startswith('<li>'):
            if in_table: body_html.append('</table>'); in_table=False
            if not in_ul:
                body_html.append('<ul style="padding-left:22px">')
                in_ul = True
            body_html.append(p)
        elif p.startswith('TABLE:'):
            if in_ul: body_html.append('</ul>'); in_ul=False
            if not in_table:
                body_html.append('<table style="width:100%;border-collapse:collapse;margin:8px 0;font-size:13.5px">')
                in_table = True
                is_header = True
            else:
                is_header = False
            # 解析表格行
            cells = [c.strip() for c in p[6:].strip('|').split('|')]
            # 跳过分隔行 |---|---|
            if all(re.match(r'^[-:]+$', c) for c in cells):
                is_header = False
                continue
            if is_header:
                body_html.append('<tr>'+''.join('<th style="border:1px solid #ddd;padding:6px 8px;background:#f9f9f9;text-align:left">%s</th>' % fmt(c) for c in cells)+'</tr>')
            else:
                body_html.append('<tr>'+''.join('<td style="border:1px solid #ddd;padding:6px 8px;vertical-align:top">%s</td>' % fmt(c) for c in cells)+'</tr>')
        else:
            if in_ul: body_html.append('</ul>'); in_ul=False
            if in_table: body_html.append('</table>'); in_table=False
            body_html.append(p)
    if in_ul: body_html.append('</ul>')
    if in_table: body_html.append('</table>')

    h = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<style>
  :root { --pink:#ffdeeb; --blue:#e8f4fd; --yellow:#fff8c6; --ink:#2b2b2b; --line:#eee; }
  * { box-sizing:border-box; }
  body { font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; color:var(--ink);
         max-width:860px; margin:0 auto; padding:24px 16px 60px; line-height:1.7; }
  h1 { font-size:25px; border-bottom:3px solid #ff7ab8; padding-bottom:10px; }
  h1 small { font-size:13px; color:#888; font-weight:normal; }
  h2 { font-size:18px; margin:28px 0 10px; padding-left:10px; border-left:5px solid #ff7ab8; }
  h3 { font-size:16px; margin:20px 0 8px; }
  .card { border-radius:10px; padding:13px 16px; margin:10px 0; border:1px solid var(--line); }
  .yellow { background:var(--yellow); }
  hr { border:none; border-top:1px dashed #ccc; margin:14px 0; }
  blockquote { border-left:4px solid #ff7ab8; margin:8px 0; padding:6px 14px; background:#fff5fa; border-radius:0 8px 8px 0; }
  ul,li { margin:3px 0; }
  .must { color:#d6336c; font-weight:700; }
  mark { background:var(--yellow); padding:0 3px; border-radius:3px; }
  @media print { body { padding:0; } }
</style>
</head>
<body>
<h1>%s</h1>
%s
</body>
</html>''' % (html.escape(title), html.escape(title), '\n'.join(body_html))

    open(out, 'w', encoding='utf-8').write(h)
    return out

def fmt(t):
    """escape + 简单 markdown 粗体/高亮"""
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'`(.+?)`', r'<code style="background:#f1f1f1;border-radius:4px;padding:1px 5px;font-size:12.5px">\1</code>', t)
    return t

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 txt2html.py <源文件> [标题]')
        sys.exit(1)
    src = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    out = convert(src, title)
    print('生成: %s' % out)
