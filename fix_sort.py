import json, re

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
projects = data['projects']

REGION_ORDER = {'东北': 1, '华北': 2, '西北': 3, '华东': 4, '华中': 5, '西南': 6, '华南': 7}
PROVINCE_ORDER = {
    '黑龙江': 1, '吉林': 2, '辽宁': 3, '内蒙古': 4, '北京': 5, '天津': 6, '河北': 7, '山西': 8,
    '陕西': 9, '甘肃': 10, '宁夏': 11, '青海': 12, '新疆': 13, '山东': 14, '江苏': 15, '浙江': 16,
    '安徽': 17, '福建': 18, '江西': 19, '上海': 20, '河南': 21, '湖北': 22, '湖南': 23,
    '重庆': 24, '四川': 25, '贵州': 26, '云南': 27, '西藏': 28, '广东': 29, '广西': 30, '海南': 31,
}
REC_PRIORITY = {
    '🔥 ★★★ 强烈建议投标': 1, '⭐ ★★☆ 建议投标': 2, '👀 ★☆☆ 可关注': 3,
    '☆☆☆ 已截止': 4, '☆☆☆ 不建议': 5,
}

def sort_key(p):
    return (
        REGION_ORDER.get(p.get('region', ''), 99),
        PROVINCE_ORDER.get(p.get('province', ''), 99),
        p['company'],
        REC_PRIORITY.get(p.get('rec', ''), 99),
        p.get('deadline', '9999-99-99')
    )

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
