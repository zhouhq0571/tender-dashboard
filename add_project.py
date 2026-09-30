import json, re

HTML_PATH = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html"

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))

# 新项目
new_project = {
    "id": 53,
    "region": "华南",
    "province": "海南",
    "company": "海南农商",
    "project": "应用研发安全管控平台项目",
    "overview": "海南农商银行采取竞争性磋商方式采购应用研发安全管控平台，项目预算120万元。供应商须提供2024或2025年度经审计的完整财务报告，须参与并通过POC测试。",
    "budget": "120万元",
    "deadline": "2026-07-30 15:00",
    "method": "竞争性磋商",
    "contact": "杨先生 15986436232；邮箱：yangchenghai@hainanbank.com.cn；地址：海南省海口市美兰区国兴大道5号海南大厦副楼",
    "tags": ["风控合规", "渠道系统"],
    "rec": "👀 ★☆☆ 可关注",
    "url": "https://www.hainanbank.com.cn/html/swgk/tzgg/2026/0709/7108.html",
    "source": "海南农商银行官网"
}

# 添加新项目
data['projects'].append(new_project)

# 重新排序
import sys
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from config import sort_key

data['projects'] = sorted(data['projects'], key=sort_key)

# 重新编号
for i, p in enumerate(data['projects'], 1):
    p['id'] = i

# 更新版本和时间
from datetime import datetime
now = datetime.now()
data['version'] = 'v87'
data['date'] = f"{now.year}年{now.month:02d}月{now.day:02d}日"
hour = now.hour
if 6 <= hour < 12:
    data['timePeriod'] = '上午'
elif 12 <= hour < 14:
    data['timePeriod'] = '中午'
elif 14 <= hour < 18:
    data['timePeriod'] = '下午'
else:
    data['timePeriod'] = '晚上'

# 写回HTML
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_html = html.replace(match.group(1), new_json)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"✅ 已添加项目: 海南农商 - 应用研发安全管控平台项目")
print(f"✅ 当前项目数: {len(data['projects'])}")
print(f"✅ 版本: {data['version']}, 日期: {data['date']} {data['timePeriod']}")
