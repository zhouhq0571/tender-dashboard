#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换规则
replacements = [
    ('数据更新时间：2026年08月09日 中午', '数据更新时间：2026年08月10日 上午'),
    ('2026年08月09日 中午</span>', '2026年08月10日 上午</span>'),
    ('"version": "v133"', '"version": "v134"'),
    ('"date": "2026年08月09日"', '"date": "2026年08月10日"'),
    ('"timePeriod": "中午"', '"timePeriod": "上午"'),
]

for old, new in replacements:
    count = content.count(old)
    if count == 0:
        print(f"WARNING: not found: {old}")
    else:
        content = content.replace(old, new)
        print(f"Replaced {count}x: {old} -> {new}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
