import json, re, os, sys
from datetime import datetime

HTML_FILE = 'index.html'
TODAY = '2026-07-26'
YESTERDAY = '2026-07-25'

# 读取现有HTML
html = open(HTML_FILE).read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))
projects = data.get('projects', [])

print(f"[基线] 现有项目: {len(projects)} 个, 版本: {data.get('version')}")

# Step 1: 删除过期项目 (deadline < 昨天)
kept = []
deleted = []
for p in projects:
    dl = p.get('deadline', '')
    dl_date = dl.split(' ')[0] if dl else ''
    if dl_date < YESTERDAY:
        deleted.append(p)
    else:
        kept.append(p)

print(f"[删除] {len(deleted)} 个过期项目, 保留 {len(kept)} 个")

# Step 2: 新项目 (用户确认纳入)
new_project = {
    "id": 77,
    "region": "东北",
    "province": "吉林",
    "company": "吉林信托",
    "project": "家办系统建设软硬件平台采购项目",
    "overview": "吉林信托公司家办系统建设软硬件平台采购，分2个标段：1标段软件平台采购（155万元），2标段硬件平台采购（20万元）。1标段交付期5个月，2标段1个月。",
    "budget": "175万元（1标段155万+2标段20万）",
    "deadline": "2026-07-30 09:30",
    "method": "公开招标",
    "contact": "联系人：董天 13041093518 / 徐工 18611886439；邮箱：guoxinzhaobiao123@163.com",
    "tags": ["资产服务信托"],
    "rec": "⭐ ★★☆ 建议投标",
    "url": "http://www.qgzbcgjypt.com/xinwenzhongxin/103847.html",
    "source": "国信招标与采购信息平台"
}

kept.append(new_project)
print(f"[新增] 1 个项目: {new_project['company']} {new_project['project']}")

# Step 3: 重新编号
for i, p in enumerate(kept, 1):
    p['id'] = i

# Step 4: 排序
REGION_ORDER = {
    '东北': 1, '华北': 2, '西北': 3, '华东': 4,
    '华中': 5, '西南': 6, '华南': 7,
}

PROVINCE_ORDER = {
    '黑龙江': 1, '吉林': 2, '辽宁': 3,
    '内蒙古': 4, '北京': 5, '天津': 6, '河北': 7, '山西': 8,
    '陕西': 9, '甘肃': 10, '宁夏': 11, '青海': 12, '新疆': 13,
    '山东': 14, '江苏': 15, '浙江': 16, '安徽': 17, '福建': 18, '江西': 19, '上海': 20,
    '河南': 21, '湖北': 22, '湖南': 23,
    '重庆': 24, '四川': 25, '贵州': 26, '云南': 27, '西藏': 28,
    '广东': 29, '广西': 30, '海南': 31,
}

REC_PRIORITY = {
    '🔥 ★★★ 强烈建议投标': 1,
    '⭐ ★★☆ 建议投标': 2,
    '★☆☆ 可关注': 3,
    '👀 ★☆☆ 可关注': 3,
    '☆☆☆ 已截止': 4,
    '☆☆☆ 不建议': 5,
}

def sort_key(p):
    region_pri = REGION_ORDER.get(p.get('region', ''), 99)
    province_pri = PROVINCE_ORDER.get(p.get('province', ''), 99)
    rec = p.get('rec', '')
    rec_pri = REC_PRIORITY.get(rec, 99)
    dl = p.get('deadline', '9999-99-99')
    return (region_pri, province_pri, p['company'], rec_pri, dl)

kept.sort(key=sort_key)

# 重新编号（排序后）
for i, p in enumerate(kept, 1):
    p['id'] = i

print(f"[排序] 完成, 共 {len(kept)} 个项目")

# Step 5: 构建新 JSON
new_data = {
    "version": "v110",
    "date": "2026年07月26日",
    "timePeriod": "凌晨",
    "projects": kept
}

# Step 6: 替换 HTML 中的 JSON
json_str = json.dumps(new_data, ensure_ascii=False, indent=2)
new_html = re.sub(
    r'<script type="application/json" id="tender-data">.*?</script>',
    f'<script type="application/json" id="tender-data">\n{json_str}\n</script>',
    html,
    count=1,
    flags=re.DOTALL
)

# Step 7: 更新 <title>
new_html = re.sub(
    r'<title>恒生银信招标资讯每日速递 \| .*?</title>',
    '<title>恒生银信招标资讯每日速递 | 2026年07月26日（更新）v110</title>',
    new_html
)

# Step 8: 更新封面日期
new_html = re.sub(
    r'数据更新时间：\d{4}年\d{2}月\d{2}日\s+\S+',
    '数据更新时间：2026年07月26日 凌晨',
    new_html
)

# Step 9: 更新封底日期
new_html = re.sub(
    r'<p class="update-time">\d{4}年\d{2}月\d{2}日\s+\S+</p>',
    '<p class="update-time">2026年07月26日 凌晨</p>',
    new_html
)

# Step 10: 更新部署注释
new_html = re.sub(
    r'<!-- Deployed v\d+ at .*? -->',
    f'<!-- Deployed v110 at 2026-07-26 01:25:00 -->',
    new_html
)

with open(HTML_FILE, 'w') as f:
    f.write(new_html)

print(f"[写入] {HTML_FILE} 完成")
print(f"[版本] v109 → v110")
print(f"[项目] 76 → {len(kept)} (删除23 + 新增1)")

# Step 11: 保存更新后数据供Excel生成
with open('updated_projects.json', 'w') as f:
    json.dump(kept, f, ensure_ascii=False, indent=2)

# Step 12: 保存删除记录
with open('deleted_projects_final.json', 'w') as f:
    json.dump(deleted, f, ensure_ascii=False, indent=2)

# Step 13: 保存状态
status = {
    "run_time": "2026-07-26T01:25:00+0800",
    "version_before": "v109",
    "version_after": "v110",
    "projects_before": 76,
    "projects_after": len(kept),
    "deleted_count": len(deleted),
    "new_count": 1,
    "deleted_ids": [p['id'] for p in deleted],
    "new_projects": [{"company": new_project['company'], "project": new_project['project'], "deadline": new_project['deadline']}],
    "pending_supplement": ["北京农商银行-数据治理和数据架构实施项目供应商征集(2026-07-23)", "北京农商银行-应用服务网关系统信创改造项目供应商征集(2026-07-22)", "北京农商银行-微服务平台建设项目供应商征集(2026-07-22)"]
}
with open('LAST_RUN_STATUS.md', 'w') as f:
    f.write(f"# 增量更新状态 - {status['run_time']}\n\n")
    f.write(f"- 版本: {status['version_before']} → {status['version_after']}\n")
    f.write(f"- 项目数: {status['projects_before']} → {status['projects_after']}\n")
    f.write(f"- 删除: {status['deleted_count']} 个\n")
    f.write(f"- 新增: {status['new_count']} 个\n")
    f.write(f"- 待补充: {len(status['pending_supplement'])} 项\n")
    f.write(f"\n## 删除项目\n")
    for p in deleted:
        f.write(f"- id={p['id']} {p['company']} {p['project'][:30]} deadline={p['deadline']}\n")
    f.write(f"\n## 新增项目\n")
    f.write(f"- {new_project['company']} {new_project['project']} deadline={new_project['deadline']}\n")
    f.write(f"\n## 待补充项目\n")
    for item in status['pending_supplement']:
        f.write(f"- {item}\n")

print("[状态] LAST_RUN_STATUS.md 已更新")
print("[完成] index.html 增量更新成功")
