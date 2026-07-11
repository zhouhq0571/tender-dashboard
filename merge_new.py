import json
from datetime import datetime

# Read existing kept data
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/step1_2_result.json', 'r') as f:
    data = json.load(f)

kept = data['kept']

# New project: 恒丰银行 电子验印平台信创版
new_project = {
    "region": "华北",
    "province": "山东",
    "company": "恒丰银行",
    "project": "2026年电子验印应用平台信创版核心算法产品及配套实施服务采购项目",
    "overview": "使电子验印应用平台终端支持麒麟、统信桌面操作系统、国产浏览器等国产化硬件（ARM或者兆芯）和基础软件，将相关业务平滑迁移至国产化环境。供应商已确定为方正国际软件（北京）有限公司，采用单一来源采购。",
    "budget": "-",
    "deadline": "2026-07-06",
    "method": "单一来源采购",
    "contact": "郭经理 0531-59667176；代理机构：港投工程咨询有限公司 杜云飞 15192562900",
    "tags": ["信创/国产化"],
    "rec": "☆☆☆ 不建议",
    "url": "http://www.ygcgfw.com/gggs/001002/001002005/20260629/7bc491ec-8e2e-4c25-beeb-a99d6d6aba0a.html",
    "source": "阳光采购服务平台",
    "id": "48",
    "new": True
}

# Add new project
kept.append(new_project)

# 完整排序规则：大区→省份→公司名→投标建议→截止日期
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
    '👀 ★☆☆ 可关注': 3,
    '☆☆☆ 已截止': 4,
    '☆☆☆ 不建议': 5,
}

def parse_dl(d):
    if not d or d == '-' or '另行通知' in d:
        return '9999-99-99'
    import re
    m = re.search(r'(\d{4}-\d{2}-\d{2})', str(d))
    if m:
        return m.group(1)
    return '9999-99-99'

def sort_key(x):
    region_pri = REGION_ORDER.get(x.get('region', ''), 99)
    province_pri = PROVINCE_ORDER.get(x.get('province', ''), 99)
    rec_pri = REC_PRIORITY.get(x.get('rec', ''), 99)
    dl = parse_dl(x.get('deadline', ''))
    return (region_pri, province_pri, x.get('company', ''), rec_pri, dl)

kept.sort(key=sort_key)

# Re-number after sort
for i, item in enumerate(kept, 1):
    item['id'] = str(i)

# Remove 'new' flag before writing
for item in kept:
    if 'new' in item:
        del item['new']

# Save merged result
result = {
    "version": data.get('version', 'v1'),
    "date": data.get('date', ''),
    "timePeriod": data.get('timePeriod', ''),
    "projects": kept
}

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/merged_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Merged {len(kept)} projects")
