#!/usr/bin/env python3
"""PWA 构建脚本：把学习计划表和所有链接的 html 资料复制到 docs/ 下，
保持相对路径结构，确保 GitHub Pages 能正常访问。
用法：python3 build_pwa.py
之后 git add docs/ && git push 即可自动部署。"""
import re, os, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')

# 1) 复制学习计划表
plan_src = os.path.join(ROOT, '00_考试总览', '学习计划表.html')
plan_dst = os.path.join(DOCS, '00_考试总览', '学习计划表.html')
os.makedirs(os.path.dirname(plan_dst), exist_ok=True)
shutil.copy2(plan_src, plan_dst)
print('复制: 00_考试总览/学习计划表.html')

# 2) 解析学习计划表里所有 href 链接，把对应的 html 文件复制到 docs/ 下
plan_html = open(plan_src, encoding='utf-8').read()
links = set()
for m in re.finditer(r'href="([^"]+)"', plan_html):
    link = m.group(1)
    if link.startswith('http') or link.startswith('#'):
        continue
    links.add(link)

copied = 0
for link in sorted(links):
    # 解析相对路径：学习计划表在 00_考试总览/ 下，链接是相对于它的
    src = os.path.normpath(os.path.join(ROOT, '00_考试总览', link))
    # 目标路径在 docs/ 下保持相同结构
    dst = os.path.normpath(os.path.join(DOCS, '00_考试总览', link))
    if os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        print(f'复制: {link}')
    else:
        print(f'跳过(不存在): {link}')

# 3) 复制 PWA 静态文件（manifest/sw/icon/index 已在 docs/ 下，无需复制）
print(f'\n共复制 {copied + 1} 个文件到 docs/')
print('下一步: git add docs/ && git commit -m "build pwa" && git push')
