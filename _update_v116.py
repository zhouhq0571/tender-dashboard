#!/usr/bin/env python3
import json, re
from datetime import datetime

# ====== 1. 读取保留项目 ======
with open('work_current_projects.json', 'r', encoding='utf-8') as f:
    projects = json.load(f)

print(f"[基线] 保留项目: {len(projects)} 个")

# ====== 2. 添加新项目 ======
new_project = {
    "region": "华北",
    "province": "北京",
    "company": "北京农商",
    "project": "信披系统指数型业绩比较基准改造项目",
    "overview": "北京农商银行拟对现有信披系统进行指数型业绩比较基准改造，支持指数信息维护、行情接入、存款利率信息维护、达基净值计算逻辑调整等功能，满足资管产品信息披露监管合规要求。",
    "budget": "-",
    "deadline": "2026-08-04 16:00",
    "method": "竞争性谈判",
    "contact": "张老师 010-****8154",
    "tags": ["财富管理", "数据平台"],
    "rec": "★☆☆ 可关注",
    "url": "https://bj.qianlima.com/zbcontent-617832038.html",
    "source": "千里马招标网"
}

projects.append(new_project)
print(f"[新增] 1 个项目: {new_project['company']} {new_project['project']}")

# ====== 3. 排序 ======
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
    rec_pri = REC_PRIORITY.get(p.get('rec', ''), 99)
    dl = p.get('deadline', '9999-99-99')
    # 处理 "另行通知" 等情况
    if not dl or dl == '-' or '另行通知' in str(dl):
        dl = '9999-99-99'
    return (region_pri, province_pri, rec_pri, dl)

projects.sort(key=sort_key)

# 重新编号
for i, p in enumerate(projects, 1):
    p['id'] = i

print(f"[排序] 完成, 共 {len(projects)} 个项目")

# ====== 4. 保存更新后数据 ======
with open('updated_projects.json', 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

# ====== 5. 构建新 JSON 嵌入 HTML ======
new_data = {
    "version": "v116",
    "date": "2026年07月30日",
    "timePeriod": "上午",
    "projects": projects
}

json_str = json.dumps(new_data, ensure_ascii=False, indent=2)

# ====== 6. 读取并更新 HTML ======
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 替换 JSON 数据
html = re.sub(
    r'<script type="application/json" id="tender-data">.*?</script>',
    f'<script type="application/json" id="tender-data">\n{json_str}\n</script>',
    html,
    count=1,
    flags=re.DOTALL
)

# 更新 <title>
html = re.sub(
    r'<title>恒生银信招标资讯每日速递 \| .*?</title>',
    '<title>恒生银信招标资讯每日速递 | 2026年07月30日（更新）v116</title>',
    html
)

# 更新封面时间
html = re.sub(
    r'<div class="cover-meta" id="cover-update-time">.*?</div>',
    '<div class="cover-meta" id="cover-update-time">数据更新时间：2026年07月30日 上午</div>',
    html
)

# 更新封底时间
html = re.sub(
    r'<span id="footer-update-time">.*?</span>',
    '<span id="footer-update-time">2026年07月30日 上午</span>',
    html
)

# ====== 7. 验证标签闭合（简单检查） ======
open_div = html.count('<div')
close_div = html.count('</div>')
if open_div != close_div:
    print(f"[警告] div 标签不平衡: 开={open_div}, 闭={close_div}")
else:
    print(f"[验证] div 标签平衡: {open_div} 对")

# ====== 8. 写入 HTML ======
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"[写入] index.html 完成")
print(f"[版本] v115 → v116")
print(f"[项目] 52 → {len(projects)} (删除7 + 新增1)")

# ====== 9. 生成 LAST_RUN_STATUS ======
status = {
    "run_time": "2026-07-30T08:03:00+0800",
    "version_before": "v115",
    "version_after": "v116",
    "projects_before": 52,
    "projects_after": len(projects),
    "deleted_count": 7,
    "new_count": 1,
    "deleted_companies": ["中信信托", "中信信托", "光大银行", "山西信托", "江苏银行", "杭州工商信托", "浦发银行"],
    "new_projects": [{"company": new_project['company'], "project": new_project['project'], "deadline": new_project['deadline']}],
}

with open('LAST_RUN_STATUS.md', 'w', encoding='utf-8') as f:
    f.write(f"# 增量更新状态 - {status['run_time']}\n\n")
    f.write(f"- 版本: {status['version_before']} → {status['version_after']}\n")
    f.write(f"- 项目数: {status['projects_before']} → {status['projects_after']}\n")
    f.write(f"- 删除过期: {status['deleted_count']} 个\n")
    f.write(f"- 新增: {status['new_count']} 个\n")
    f.write(f"\n## 新增项目\n")
    f.write(f"- {new_project['company']} | {new_project['project']} | deadline={new_project['deadline']}\n")

print("[状态] LAST_RUN_STATUS.md 已更新")
print("[完成] 增量更新成功，准备部署")
