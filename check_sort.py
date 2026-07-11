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
        REC_PRIORITY.get(p.get('rec', ''), 99),
        int(p.get('id', 999)),
    )

# 检查排序
for i in range(len(projects)-1):
    k1 = sort_key(projects[i])
    k2 = sort_key(projects[i+1])
    if k1 > k2:
        print(f'排序错误 @位置{i+1}:')
        print(f'  ID {projects[i]["id"]}: {projects[i]["region"]} {projects[i]["province"]} {projects[i]["rec"]} -> key={k1}')
        print(f'  ID {projects[i+1]["id"]}: {projects[i+1]["region"]} {projects[i+1]["province"]} {projects[i+1]["rec"]} -> key={k2}')
        break
else:
    print('排序正确')
