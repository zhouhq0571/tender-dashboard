import json
import re
from datetime import datetime

# 读取完整项目数据
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/excel_all_projects_full.json', 'r', encoding='utf-8') as f:
    all_projects = json.load(f)

# 之前子agent分析的纳入项目列表（按公司名称+项目前15字匹配）
# 第一批：★★★ 强烈建议（12个）
batch1_companies = [
    '山西信托股份有限公司',
    '广东华润银行股份有限公司', 
    '宁波银行股份有限公司',  # 智慧电销
    '招商银行哈尔滨分行',
    '廊坊银行',  # FTP
    '临商银行股份有限公司',  # 外部数据管理平台
    '齐鲁银行股份有限公司',  # 关联交易
    '浙商银行股份有限公司',  # 市场风险
    '大连银行股份有限公司',  # 电子渠道用户行为
    '兴业银行长沙分行',  # 资金管理
    '中国进出口银行',  # 征信
    '天津银行股份有限公司',  # 国际结算AI
]

# 第二批：★★☆ 建议（6个）
batch2_companies = [
    '泰安银行股份有限公司',  # 微贷
    '余杭农商银行',  # 帆软报表
    '上海农商银行',  # 云管平台
    '保定银行股份有限公司',  # 反诈
    '北京银行股份有限公司杭州分行',  # 资金监管
    '北京银行股份有限公司',  # 供应链票据
    '广东省农村信用社联合社',  # 电子凭证
]

# 第三批：★☆☆ 可关注（4个）
batch3_companies = [
    '广东台山农村商业银行股份有限公司',  # 考核管理
    '中国进出口银行',  # 财务数据迁移
    '浙商银行股份有限公司',  # 数据安全监测
    '天津银行股份有限公司',  # 风险暴露
]

# 从项目正文中提取截止日期
def extract_deadline(text):
    if not text:
        return '待补充'
    # 常见截止日期模式
    patterns = [
        r'(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}[:：]\d{2})',  # 2026年7月15日 14:00
        r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})',  # 2026-07-15 14:00
        r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2026年7月15日
        r'(\d{4}-\d{2}-\d{2})',  # 2026-07-15
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return '待补充'

# 从项目正文中提取预算
def extract_budget(text):
    if not text:
        return '待补充'
    patterns = [
        r'预算[：:]\s*([\d,\.]+\s*万?元?)',
        r'招标估价[：:]\s*([\d,\.]+\s*万?元?)',
        r'金额[：:]\s*([\d,\.]+\s*万?元?)',
        r'([\d,\.]+\s*万元)',
        r'([\d,\.]+\s*元)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return '待补充'

# 从项目正文中提取招标方式
def extract_method(text):
    if not text:
        return '待补充'
    methods = ['公开招标', '竞争性谈判', '竞争性磋商', '单一来源采购', '询价采购', '邀请招标', '框架协议']
    for m in methods:
        if m in text:
            return m
    if '征集' in text:
        return '供应商征集'
    if '公示' in text:
        return '单一来源公示'
    return '待补充'

# 生成项目概述（前100字）
def extract_overview(text):
    if not text:
        return '待补充'
    # 取前100字作为概述
    return text[:100] + '...' if len(text) > 100 else text

# 处理所有项目
for p in all_projects:
    p['deadline'] = extract_deadline(p.get('detail_content', ''))
    p['budget'] = extract_budget(p.get('detail_content', ''))
    p['method_detailed'] = extract_method(p.get('detail_content', ''))
    p['overview'] = extract_overview(p.get('detail_content', ''))

# 按批次分组
batch1 = []
batch2 = []
batch3 = []
others = []

for p in all_projects:
    company = p['company']
    title = p['title']
    
    # 匹配第一批
    if company in batch1_companies:
        # 排除宁波银行的员工道德风险管理系统
        if '宁波银行' in company and '道德风险' in title:
            others.append(p)
        else:
            batch1.append(p)
    elif company in batch2_companies:
        batch2.append(p)
    elif company in batch3_companies:
        # 排除进出口银行的财务数据迁移（已在batch2）
        if '进出口银行' in company and '财务' in title and '征信' not in title:
            batch3.append(p)
        elif '进出口银行' in company and '征信' in title:
            batch1.append(p)  # 征信系统归入第一批
        else:
            batch3.append(p)
    else:
        others.append(p)

# 保存结果
result = {
    'batch1_强烈建议': batch1,
    'batch2_建议': batch2,
    'batch3_可关注': batch3,
    'others_排除': others
}

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/excel_batches.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"第一批（★★★）: {len(batch1)}个")
for p in batch1:
    print(f"  - {p['company']}: {p['title'][:50]}")
    print(f"    截止日期: {p['deadline']}, 预算: {p['budget']}, 方式: {p['method_detailed']}")

print(f"\n第二批（★★☆）: {len(batch2)}个")
for p in batch2:
    print(f"  - {p['company']}: {p['title'][:50]}")

print(f"\n第三批（★☆☆）: {len(batch3)}个")
for p in batch3:
    print(f"  - {p['company']}: {p['title'][:50]}")

print(f"\n排除: {len(others)}个")
for p in others:
    print(f"  - {p['company']}: {p['title'][:50]}")
