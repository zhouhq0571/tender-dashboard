import re, json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.+?)</script>', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    print(f'基准版本: {data["version"]}')
    print(f'基准日期: {data["date"]}')
    print(f'基准项目数: {len(data["projects"])}')
else:
    print('未找到 tender-data')
