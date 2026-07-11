import json, re
import sys
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from config import sort_key

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
projects = data['projects']

# 排序
projects_sorted = sorted(projects, key=sort_key)

# 重新编号
for i, p in enumerate(projects_sorted, 1):
    p['id'] = i

# 更新数据
data['projects'] = projects_sorted

# 写回HTML
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_html = html.replace(match.group(1), new_json)

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'w') as f:
    f.write(new_html)

print('排序已修复并重新编号')
print(f'项目数: {len(projects_sorted)}')

# 验证排序
for i in range(len(projects_sorted)-1):
    k1 = sort_key(projects_sorted[i])
    k2 = sort_key(projects_sorted[i+1])
    if k1 > k2:
        print(f'仍有排序错误 @位置{i+1}')
        print(f'  ID {projects_sorted[i]["id"]}: {projects_sorted[i]["company"]} {projects_sorted[i]["rec"]}')
        print(f'  ID {projects_sorted[i+1]["id"]}: {projects_sorted[i+1]["company"]} {projects_sorted[i+1]["rec"]}')
        break
else:
    print('排序验证通过')
