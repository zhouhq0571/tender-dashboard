import pandas as pd
import json

# 读取分析结果
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/excel_analysis_results.json', 'r') as f:
    results = json.load(f)

# 获取纳入的项目
valid_projects = [r for r in results if r['decision'] == '纳入']

# 读取三个Excel文件获取完整信息
all_rows = []
files = [
    ('信托', '/Users/tmp/信托-20260709.xlsx'),
    ('银行新关键词', '/Users/tmp/银行-20260709使用新关键词.xlsx'),
    ('银行旧关键词', '/Users/tmp/银行-20260709使用旧关键词.xlsx'),
]

for label, filepath in files:
    df = pd.read_excel(filepath)
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict['source'] = label
        all_rows.append(row_dict)

# 匹配纳入项目并输出关键字段
print("=" * 80)
print("纳入项目完整信息（带关键字段）")
print("=" * 80)

for i, vp in enumerate(valid_projects, 1):
    # 在all_rows中找到匹配的行
    matched = None
    for row in all_rows:
        if str(row.get('标题', '')) == vp['project'] and str(row.get('招标单位名称', '')) == vp['company']:
            matched = row
            break
    
    if matched:
        print(f"\n【{i}】{matched.get('招标单位名称', '')}")
        print(f"    项目: {matched.get('标题', '')}")
        print(f"    发布时间: {matched.get('发布时间', '')}")
        print(f"    省份: {matched.get('省份', '')} {matched.get('城市', '')}")
        print(f"    联系人: {matched.get('招标单位联系人', '未披露')}")
        print(f"    电话: {matched.get('招标单位联系电话', '未披露')}")
        preview = str(matched.get('内容预览', ''))[:200]
        print(f"    内容预览: {preview}...")
        print(f"    来源: {matched.get('source', '')}")
    else:
        print(f"\n【{i}】{vp['company']} - {vp['project']} (未找到匹配)")

print(f"\n总计: {len(valid_projects)}个纳入项目")
