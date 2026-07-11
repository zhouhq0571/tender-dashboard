import json
import re
from datetime import datetime, date, timedelta

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/merged_data.json', 'r') as f:
    data = json.load(f)

projects = data['projects']
today = date.today()
yesterday = today - timedelta(days=1)

errors = []
warnings = []

# Gate 1: "已截止"项目deadline检查
for p in projects:
    rec = p.get('rec', '')
    dl = p.get('deadline', '')
    if '已截止' in rec:
        # Parse deadline
        m = re.search(r'(\d{4}-\d{2}-\d{2})', str(dl))
        if m:
            dl_date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
            if dl_date not in [today, yesterday]:
                errors.append(f"Gate 1 FAIL: id={p['id']} {p['company']} deadline={dl} 不在今天或昨天，但rec='已截止'")
        else:
            errors.append(f"Gate 1 FAIL: id={p['id']} {p['company']} deadline='{dl}' 无法解析，但rec='已截止'")

# Gate 2: 人力外包/运维评级检查
for p in projects:
    tags = p.get('tags', [])
    rec = p.get('rec', '')
    if '人力外包' in tags or '运维服务' in tags:
        if '★★' in rec or '★★★' in rec:
            errors.append(f"Gate 2 FAIL: id={p['id']} {p['company']} 标签含人力外包/运维，但rec='{rec}' (应≤★☆☆)")

# Gate 3: "其他"标签检查
for p in projects:
    tags = p.get('tags', [])
    if '其他' in tags:
        errors.append(f"Gate 3 FAIL: id={p['id']} {p['company']} 标签含'其他'")

# Gate 4: 排除新媒体/品牌/纯硬件/数据库软件
excluded_keywords = ['新媒体', '品牌', '数据库软件', '服务器采购', '网络设备', '硬件采购']
for p in projects:
    proj_name = p.get('project', '')
    overview = p.get('overview', '')
    for kw in excluded_keywords:
        if kw in proj_name or kw in overview:
            warnings.append(f"Gate 4 WARN: id={p['id']} {p['company']} 可能含排除项 '{kw}'")

# Gate 5: 重复检查（company + project）
seen = {}
for p in projects:
    key = f"{p['company']}|{p['project']}"
    if key in seen:
        errors.append(f"Gate 5 FAIL: 重复项目 id={p['id']} 与 id={seen[key]}: {p['company']} - {p['project']}")
    else:
        seen[key] = p['id']

# Gate 6: 新项目字段完整性检查
for p in projects:
    required = ['region', 'province', 'company', 'project', 'overview', 'deadline', 'method', 'contact', 'tags', 'rec']
    for field in required:
        if not p.get(field):
            errors.append(f"Gate 6 FAIL: id={p['id']} {p['company']} 缺少字段 '{field}'")
    # Check budget can be "-"
    # Check url
    if not p.get('url'):
        warnings.append(f"Gate 6 WARN: id={p['id']} {p['company']} 缺少 url")

# Gate 7: 单一来源项目检查
for p in projects:
    method = p.get('method', '')
    rec = p.get('rec', '')
    if '单一来源' in method:
        # Check if rec is appropriate
        if '★★' in rec or '★★★' in rec:
            warnings.append(f"Gate 7 WARN: id={p['id']} {p['company']} 单一来源但rec='{rec}'")

# Summary
print("="*60)
print("QUALITY GATE REPORT")
print("="*60)
print(f"Total projects: {len(projects)}")
print(f"Errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")
print()

if errors:
    print("ERRORS (must fix):")
    for e in errors:
        print(f"  ❌ {e}")
    print()

if warnings:
    print("WARNINGS (review):")
    for w in warnings:
        print(f"  ⚠️ {w}")
    print()

if not errors and not warnings:
    print("✅ ALL GATES PASSED")
else:
    print(f"Result: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors, {len(warnings)} warnings)")

# Save report
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/quality_gate_report.txt', 'w') as f:
    f.write("QUALITY GATE REPORT\n")
    f.write("="*60 + "\n")
    f.write(f"Total projects: {len(projects)}\n")
    f.write(f"Errors: {len(errors)}\n")
    f.write(f"Warnings: {len(warnings)}\n\n")
    if errors:
        f.write("ERRORS:\n")
        for e in errors:
            f.write(f"  ❌ {e}\n")
        f.write("\n")
    if warnings:
        f.write("WARNINGS:\n")
        for w in warnings:
            f.write(f"  ⚠️ {w}\n")
