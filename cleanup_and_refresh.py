import re, json, sys
from datetime import datetime, timedelta

TODAY = datetime(2026, 8, 20).date()  # 当前执行日期
DELETE_CUTOFF = TODAY - timedelta(days=1)  # 删除截止日：昨天及之前

def parse_deadline(deadline_str):
    """解析deadline字符串，返回date对象"""
    if not deadline_str or deadline_str in ['-', '另行通知']:
        return None
    try:
        # 尝试提取日期部分
        parts = deadline_str.split()
        date_part = parts[0]
        return datetime.strptime(date_part, '%Y-%m-%d').date()
    except:
        return None

def should_delete(project):
    """判断项目是否应该删除"""
    deadline_str = project.get('deadline', '')
    deadline_date = parse_deadline(deadline_str)
    if deadline_date is None:
        return False  # 无法解析的保留
    # 仅当执行日期比 deadline 晚 2 天及以上时才删除
    # 即：deadline <= 今天 - 2天 → 删除
    # 等价于：deadline < 昨天 → 删除
    return deadline_date < DELETE_CUTOFF

def should_mark_expired(project):
    """判断项目是否应该标记为已截止（但保留）"""
    deadline_str = project.get('deadline', '')
    deadline_date = parse_deadline(deadline_str)
    if deadline_date is None:
        return False
    # 昨天或今天过期的标记为已截止
    return deadline_date == DELETE_CUTOFF or deadline_date == TODAY

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.+?)</script>', html, re.DOTALL)
if not m:
    print('未找到 tender-data')
    sys.exit(1)

data = json.loads(m.group(1))
original_count = len(data['projects'])
original_version = data.get('version', '')

deleted = []
kept = []
expired = []

for p in data['projects']:
    if should_delete(p):
        deleted.append(p)
    else:
        if should_mark_expired(p):
            expired.append(p)
            p['rec'] = '☆☆☆ 已截止'
        kept.append(p)

# 重新编号
for i, p in enumerate(kept, 1):
    p['id'] = i

# 更新元数据
data['projects'] = kept
data['version'] = 'v165'
data['date'] = '2026年08月20日'
data['timePeriod'] = '上午'

# 序列化JSON（紧凑格式）
json_str = json.dumps(data, ensure_ascii=False, separators=(', ', ': '))

# 替换HTML中的JSON数据
new_html = re.sub(
    r'<script type="application/json" id="tender-data">.+?</script>',
    f'<script type="application/json" id="tender-data">{json_str}</script>',
    html,
    flags=re.DOTALL
)

# 更新title
new_html = re.sub(
    r'<title>恒生银信招标资讯每日速递 \| .*?</title>',
    '<title>恒生银信招标资讯每日速递 | 2026年08月20日（更新）v165</title>',
    new_html
)

# 更新封面时间
new_html = re.sub(
    r'id="cover-update-time">.*?</div>',
    'id="cover-update-time">数据更新时间：2026年08月20日 上午</div>',
    new_html
)

# 更新封底时间
new_html = re.sub(
    r'id="footer-update-time">.*?</span>',
    'id="footer-update-time">2026年08月20日 上午</span>',
    new_html
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'原版本: {original_version}')
print(f'原项目数: {original_count}')
print(f'删除项目数: {len(deleted)}')
print(f'保留项目数: {len(kept)}')
print(f'标记已截止: {len(expired)}')
print(f'新版本: v165')

if deleted:
    print('\n删除的项目:')
    for p in deleted:
        print(f'  - {p["company"]} | {p["project"][:40]} | deadline: {p["deadline"]}')
