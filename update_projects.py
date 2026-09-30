import json, sys

data = json.load(open('/tmp/current_data.json', encoding='utf-8'))
projects = data['projects']

# 4个新增项目
new_projects = [
    {
        "region": "华东",
        "province": "浙江",
        "company": "杭州工商信托",
        "project": "代码安全管理服务采购项目",
        "overview": "杭州工商信托股份有限公司代码安全管理服务采购项目，竞争性磋商（非政府采购），委托浙江省成套招标代理有限公司。",
        "budget": "-",
        "deadline": "2026-08-20",
        "method": "竞争性磋商",
        "contact": "代理：浙江省成套招标代理有限公司",
        "tags": ["风控合规"],
        "rec": "⭐ ★★☆ 建议投标",
        "url": "https://www.qianlima.com/hot1590008/",
        "source": "千里马招标网"
    },
    {
        "region": "华东",
        "province": "浙江",
        "company": "杭州工商信托",
        "project": "反洗钱系统更新建设项目",
        "overview": "杭州工商信托股份有限公司反洗钱系统更新建设项目，竞争性磋商（非政府采购），委托浙江省成套招标代理有限公司。",
        "budget": "-",
        "deadline": "2026-08-20",
        "method": "竞争性磋商",
        "contact": "代理：浙江省成套招标代理有限公司",
        "tags": ["风控合规"],
        "rec": "⭐ ★★☆ 建议投标",
        "url": "https://www.qianlima.com/hot1590008/",
        "source": "千里马招标网"
    },
    {
        "region": "华东",
        "province": "浙江",
        "company": "杭州工商信托",
        "project": "接口总线系统改造项目",
        "overview": "杭州工商信托股份有限公司接口总线系统改造项目，竞争性磋商（非政府采购），委托浙江省成套招标代理有限公司。",
        "budget": "-",
        "deadline": "2026-08-20",
        "method": "竞争性磋商",
        "contact": "代理：浙江省成套招标代理有限公司",
        "tags": ["数据平台"],
        "rec": "🔥 ★★★ 强烈建议投标",
        "url": "https://www.qianlima.com/hot1590008/",
        "source": "千里马招标网"
    },
    {
        "region": "华东",
        "province": "山东",
        "company": "莱商银行",
        "project": "理财产品管理系统监管报表等模块升级项目（二次）",
        "overview": "莱商银行理财产品管理系统监管报表等模块升级项目（二次）竞争性磋商。第一次发布于2026-07-21，原截止2026-08-04；二次于2026-07-29重新发布。",
        "budget": "44万元",
        "deadline": "2026-08-12",
        "method": "竞争性磋商",
        "contact": "代理：山东省鲁成招标有限公司 0531-83191862",
        "tags": ["财富管理", "数据服务"],
        "rec": "⭐ ★★☆ 建议投标",
        "url": "https://www.qianlima.com/hot21738/",
        "source": "千里马招标网"
    }
]

# 合并
all_projects = projects + new_projects

# 去重检查（公司+项目名关键词）
seen = set()
unique = []
for p in all_projects:
    key = (p['company'], p['project'])
    if key not in seen:
        seen.add(key)
        unique.append(p)

print(f"Before dedup: {len(all_projects)}, After dedup: {len(unique)}")

# 按deadline排序，"-"放最后
def sort_key(p):
    d = p.get('deadline', '-')
    if d == '-':
        return '9999-99-99'
    return d

unique.sort(key=sort_key)

# 重新编号
for i, p in enumerate(unique, 1):
    p['id'] = i

# 更新元数据
data['projects'] = unique
data['version'] = 'v136'
data['date'] = '2026年08月10日'
data['timePeriod'] = '早上'

# 写回index.html
html = open('index.html', encoding='utf-8').read()
import re
json_str = json.dumps(data, ensure_ascii=False, indent=2)
new_html = re.sub(
    r'<script type=["\']application/json["\'] id=["\']tender-data["\']>.*?</script>',
    f'<script type="application/json" id="tender-data">{json_str}</script>',
    html,
    flags=re.S
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"Updated index.html: {len(unique)} projects, version {data['version']}")

# Save for verification
with open('/tmp/updated_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
