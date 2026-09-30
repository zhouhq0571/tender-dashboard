import json

with open('cleaned_data.json') as f:
    data = json.load(f)

# Check for specific projects
check_list = [
    '智能资产配置',
    '湖北银行',
    '视频监控系统国密改造',
    '身份证联网核查系统信创',
    '农业银行',
    '光大银行',
    '渤海银行',
]

for keyword in check_list:
    matches = []
    for p in data['projects']:
        if keyword in p.get('project', '') or keyword in p.get('company', ''):
            matches.append((p.get('company',''), p.get('project','')[:50], p.get('deadline','')))
    print(f"\n=== 关键词: {keyword} ===")
    if matches:
        for m in matches:
            print(f"  {m[0]} | {m[1]} | {m[2]}")
    else:
        print("  无匹配")

print(f"\n总项目数: {len(data['projects'])}")
