import json, re
import sys
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from config import sort_key

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
projects = data['projects']

# 检查排序
for i in range(len(projects)-1):
    k1 = sort_key(projects[i])
    k2 = sort_key(projects[i+1])
    if k1 > k2:
        print(f'排序错误 @位置{i+1}:')
        print(f'  ID {projects[i]["id"]}: {projects[i]["region"]} {projects[i]["province"]} {projects[i]["company"]} {projects[i]["rec"]} -> key={k1}')
        print(f'  ID {projects[i+1]["id"]}: {projects[i+1]["region"]} {projects[i+1]["province"]} {projects[i+1]["company"]} {projects[i+1]["rec"]} -> key={k2}')
        break
else:
    print('排序正确')
