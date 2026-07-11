import pandas as pd
import json
from datetime import datetime
import re

# 读取当前看板数据
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
current_data = json.loads(match.group(1))
current_projects = current_data.get('projects', [])

existing_keys = set()
for p in current_projects:
    company = p.get('company', '')
    project = p.get('project', '')[:15]
    existing_keys.add(f'{company}|{project}')

# 读取所有三个文件
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

start_date = datetime(2026, 6, 22)
end_date = datetime(2026, 7, 7)

# 精确业务范围判断
results = []

for row in all_rows:
    title = str(row.get('标题', ''))
    company = str(row.get('招标单位名称', ''))
    pub_date = row.get('发布时间', '')
    preview = str(row.get('内容预览', ''))
    source = row.get('source', '')
    
    try:
        if pd.isna(pub_date):
            pub_dt = None
        else:
            pub_dt = pd.to_datetime(pub_date)
    except:
        pub_dt = None
    
    # 日期检查
    if pub_dt is not None:
        if pub_dt < start_date or pub_dt > end_date:
            results.append({
                'source': source, 'company': company, 'project': title,
                'pub_date': str(pub_date), 'decision': '排除', 'reason': f'日期超出范围: {pub_date}'
            })
            continue
    
    # 非目标机构
    if '银联' in company or '网联' in company or '城商行联盟' in company or '农商行联盟' in company or '省联社' in company:
        results.append({
            'source': source, 'company': company, 'project': title,
            'pub_date': str(pub_date), 'decision': '排除', 'reason': '非目标机构'
        })
        continue
    
    # 重复检查
    key = f'{company}|{title[:15]}'
    if key in existing_keys:
        results.append({
            'source': source, 'company': company, 'project': title,
            'pub_date': str(pub_date), 'decision': '排除', 'reason': '与现有看板重复'
        })
        continue
    
    # 精确业务范围判断
    text = title + ' ' + preview
    
    # 明确排除的项目类型
    excluded = False
    reason = ''
    
    if '食堂' in text or '餐饮' in text or '食材' in text:
        excluded = True; reason = '食堂/餐饮后勤'
    elif '装修' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯装修工程'
    elif '保洁' in text or '保安' in text or '物业' in text:
        excluded = True; reason = '保洁/保安/物业'
    elif '体检' in text or '医疗' in text or '医院' in text:
        excluded = True; reason = '体检/医疗'
    elif '差旅' in text or '机票' in text or '酒店' in text:
        excluded = True; reason = '差旅/酒店/机票'
    elif '礼品' in text or ('宣传' in text and '系统' not in text):
        excluded = True; reason = '礼品/宣传品'
    elif '印刷' in text and '系统' not in text:
        excluded = True; reason = '印刷服务'
    elif '律师' in text or '法律' in text or '诉讼' in text:
        excluded = True; reason = '法律服务'
    elif '会计' in text and '事务所' in text:
        excluded = True; reason = '会计师事务所'
    elif '招聘' in text or '猎头' in text:
        excluded = True; reason = '招聘/猎头'
    elif '培训' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '培训服务'
    elif '党建' in text or '工会' in text or '团委' in text:
        excluded = True; reason = '党建/工会/团委'
    elif '公益' in text or '慈善' in text or '捐赠' in text:
        excluded = True; reason = '公益/慈善/捐赠'
    elif '档案' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '档案管理（非系统）'
    elif '车辆' in text or '租车' in text or '班车' in text:
        excluded = True; reason = '车辆/租车/班车'
    elif '服务器' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯服务器硬件'
    elif '操作系统' in text and '采购' in text:
        excluded = True; reason = '操作系统软件采购'
    elif 'UPS' in text or '空调' in text or '发电机' in text:
        excluded = True; reason = 'UPS/空调/发电机'
    elif 'CDN' in text or '带宽' in text:
        excluded = True; reason = 'CDN/带宽'
    elif '人力外包' in text or '劳务派遣' in text or '驻场' in text:
        excluded = True; reason = '人力外包/劳务派遣'
    elif '运维' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯运维服务'
    elif '维保' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯维保服务'
    elif '新媒体' in text or '抖音' in text or '短视频' in text or '直播' in text:
        excluded = True; reason = '新媒体/抖音/直播'
    elif '品牌' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯品牌服务'
    elif '广告' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯广告服务'
    elif '营销' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯营销服务'
    elif '催收' in text or '不良资产' in text or '呆账' in text:
        excluded = True; reason = '催收/不良资产'
    elif '支付通道' in text or ('清算' in text and '系统' not in text):
        excluded = True; reason = '纯支付/清算通道'
    elif 'POS' in text and '系统' not in text:
        excluded = True; reason = 'POS终端'
    elif '软件采购' in text and '开发' not in text and '建设' not in text and '系统' not in text:
        excluded = True; reason = '纯软件采购'
    elif 'license' in text.lower() or ('许可' in text and '系统' not in text and '平台' not in text):
        excluded = True; reason = 'license/许可采购'
    elif '万得' in text or ('Wind' in text and '系统' not in text and '平台' not in text):
        excluded = True; reason = '万得/Wind数据采购'
    elif '云桌面' in text or '桌面云' in text or '虚拟桌面' in text:
        excluded = True; reason = '云桌面/虚拟桌面'
    elif '新疆开放大学' in company or ('学分银行' in title and '系统' not in text):
        excluded = True; reason = '非金融机构/非系统'
    elif '医保局' in text or '村医' in text:
        excluded = True; reason = '医保/村医'
    elif 'Oracle' in text or 'SQL Server' in text or ('MySQL' in text and '系统' not in text and '平台' not in text):
        excluded = True; reason = '数据库软件采购'
    elif '等保' in text and '测评' in text:
        excluded = True; reason = '等保测评服务'
    elif '密评' in text or '密码测评' in text:
        excluded = True; reason = '密码测评服务'
    elif '审计' in text and '事务所' in text:
        excluded = True; reason = '审计事务所'
    elif '评估' in text and '机构' in text and '系统' not in text:
        excluded = True; reason = '评估机构服务'
    elif '拍卖' in text:
        excluded = True; reason = '拍卖服务'
    elif '招标代理' in text or '采购代理' in text:
        excluded = True; reason = '招标/采购代理'
    elif '中介' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '中介服务'
    elif '保险' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯保险服务'
    elif '财险' in text or '寿险' in text or '再保险' in text:
        excluded = True; reason = '财险/寿险/再保险'
    elif '资产评估' in text or '土地评估' in text or '房产评估' in text:
        excluded = True; reason = '资产评估服务'
    elif ('会议' in text and '系统' not in text) or '会展' in text:
        excluded = True; reason = '会议/会展服务'
    elif '活动' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '活动策划服务'
    elif '论坛' in text and '系统' not in text:
        excluded = True; reason = '论坛服务'
    elif '峰会' in text:
        excluded = True; reason = '峰会服务'
    elif '办公用品' in text or '文具' in text or '耗材' in text:
        excluded = True; reason = '办公用品/文具/耗材'
    elif '家具' in text and '系统' not in text:
        excluded = True; reason = '家具采购'
    elif '家电' in text or '电器' in text:
        excluded = True; reason = '家电/电器采购'
    elif '仪器' in text or '仪表' in text:
        excluded = True; reason = '仪器/仪表采购'
    elif '工具' in text and '软件' not in text and '系统' not in text:
        excluded = True; reason = '工具采购'
    elif '网络设备' in text or '交换机' in text or '路由器' in text:
        excluded = True; reason = '网络设备采购'
    elif '防火墙' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '防火墙硬件采购'
    elif 'WAF' in text and '系统' not in text:
        excluded = True; reason = 'WAF硬件采购'
    elif 'IDS' in text or ('IPS' in text and '系统' not in text):
        excluded = True; reason = 'IDS/IPS硬件采购'
    elif 'VPN' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = 'VPN设备采购'
    elif '堡垒机' in text and '系统' not in text:
        excluded = True; reason = '堡垒机硬件采购'
    elif '门禁' in text and '系统' not in text:
        excluded = True; reason = '门禁设备采购'
    elif '道闸' in text or ('停车' in text and '系统' not in text):
        excluded = True; reason = '道闸/停车设备'
    elif '摄像头' in text or ('监控' in text and '系统' not in text and '平台' not in text):
        excluded = True; reason = '摄像头/监控设备'
    elif '电梯' in text and '系统' not in text:
        excluded = True; reason = '电梯采购'
    elif '暖气' in text or '通风' in text or '照明' in text:
        excluded = True; reason = '暖气/通风/照明'
    elif '油料' in text or '汽油' in text or '柴油' in text or ('充电' in text and '系统' not in text):
        excluded = True; reason = '油料/充电服务'
    elif '消防' in text and '系统' not in text:
        excluded = True; reason = '消防设备/服务'
    elif '安防' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯安防设备'
    elif '绿化' in text:
        excluded = True; reason = '绿化服务'
    elif '短信' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '短信服务'
    elif '邮件' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '邮件服务'
    elif '呼叫中心' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯呼叫中心服务'
    elif '客服' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯客服外包'
    elif '电脑' in text or '笔记本' in text or '台式机' in text or '显示器' in text:
        excluded = True; reason = '电脑/笔记本/显示器采购'
    elif '打印机' in text or '复印机' in text or '扫描仪' in text:
        excluded = True; reason = '打印机/复印机/扫描仪采购'
    elif '电话' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '电话设备/服务'
    elif '手机' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '手机采购'
    elif '办公' in text and '自动化' not in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯办公服务'
    elif '协同' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯协同服务'
    elif '即时通讯' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯即时通讯服务'
    elif 'HR' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯HR服务'
    elif '薪酬' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯薪酬服务'
    elif '考勤' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯考勤服务'
    elif '费用' in text and '系统' not in text and '平台' not in text and '报销' not in text:
        excluded = True; reason = '纯费用服务'
    elif '报销' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯报销服务'
    elif '预算' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯预算服务'
    elif '核算' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯核算服务'
    elif '采购' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯采购服务'
    elif '合同' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯合同服务'
    elif '资产' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯资产管理服务'
    elif '固定资产' in text and '系统' not in text:
        excluded = True; reason = '纯固定资产管理'
    elif '设备' in text and '系统' not in text and '平台' not in text and '软件' not in text and '管理' not in text:
        excluded = True; reason = '纯设备管理'
    elif '车辆' in text and '系统' not in text:
        excluded = True; reason = '纯车辆管理'
    elif '房产' in text and '系统' not in text:
        excluded = True; reason = '纯房产管理'
    elif '项目' in text and '管理' not in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯项目管理服务'
    elif '质量' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯质量服务'
    elif '测试' in text and '系统' not in text and '平台' not in text and '软件' not in text and '服务' not in text:
        excluded = True; reason = '纯测试服务'
    elif '检验' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯检验服务'
    elif '检测' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯检测服务'
    elif '认证' in text and '系统' not in text and '平台' not in text and 'ISO' not in text:
        excluded = True; reason = '纯认证服务'
    elif '环境' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯环境服务'
    elif '能源' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯能源服务'
    elif '节能' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯节能服务'
    elif '环保' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯环保服务'
    elif '绿色' in text and '系统' not in text and '平台' not in text and '金融' not in text:
        excluded = True; reason = '纯绿色服务'
    elif '健康' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯健康服务'
    elif '安全' in text and '系统' not in text and '平台' not in text and '软件' not in text and '管理' not in text:
        excluded = True; reason = '纯安全服务'
    elif '卫生' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯卫生服务'
    elif '文化' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯文化服务'
    elif '宣传' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯宣传服务'
    elif '战略' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯战略服务'
    elif '规划' in text and '系统' not in text and '平台' not in text and '管理' not in text and '设计' not in text:
        excluded = True; reason = '纯规划服务'
    elif '计划' in text and '系统' not in text and '平台' not in text and '管理' not in text:
        excluded = True; reason = '纯计划服务'
    elif '考核' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯考核服务'
    elif '研究' in text and '系统' not in text and '平台' not in text and '开发' not in text:
        excluded = True; reason = '纯研究服务'
    elif '调研' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯调研服务'
    elif '分析' in text and '系统' not in text and '平台' not in text and '软件' not in text and '服务' not in text:
        excluded = True; reason = '纯分析服务'
    elif '评估' in text and '系统' not in text and '平台' not in text and '软件' not in text and '服务' not in text:
        excluded = True; reason = '纯评估服务'
    elif '评价' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯评价服务'
    elif '信息' in text and '系统' not in text and '平台' not in text and '软件' not in text and '科技' not in text and '技术' not in text:
        excluded = True; reason = '纯信息服务'
    elif '科技' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯科技服务'
    elif '技术' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '服务' not in text:
        excluded = True; reason = '纯技术服务'
    elif 'IT' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '服务' not in text:
        excluded = True; reason = '纯IT服务'
    elif '数字化' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text and '转型' not in text:
        excluded = True; reason = '纯数字化服务'
    elif '转型' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯转型服务'
    elif '创新' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯创新服务'
    elif '研发' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯研发服务'
    elif '设计' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '架构' not in text:
        excluded = True; reason = '纯设计服务'
    elif '开发' in text and '系统' not in text and '平台' not in text and '软件' not in text and '建设' not in text and '研发' not in text:
        excluded = True; reason = '纯开发服务'
    elif '实施' in text and '系统' not in text and '平台' not in text and '软件' not in text and '部署' not in text and '上线' not in text:
        excluded = True; reason = '纯实施服务'
    elif '部署' in text and '系统' not in text and '平台' not in text and '软件' not in text and '上线' not in text:
        excluded = True; reason = '纯部署服务'
    elif '上线' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯上线服务'
    elif '运维' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text and '运营' not in text:
        excluded = True; reason = '纯运维服务'
    elif '运营' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯运营服务'
    elif '服务' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text and '支持' not in text and '维护' not in text and '保障' not in text:
        excluded = True; reason = '纯服务'
    elif '支持' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯支持服务'
    elif '维护' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯维护服务'
    elif '保障' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯保障服务'
    elif '优化' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯优化服务'
    elif '升级' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯升级服务'
    elif '改造' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯改造服务'
    elif '更新' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯更新服务'
    elif '替换' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯替换服务'
    elif '淘汰' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯淘汰服务'
    elif '新建' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯新建服务'
    elif '扩建' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯扩建服务'
    elif '改建' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯改建服务'
    elif '迁建' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯迁建服务'
    elif '重建' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯重建服务'
    elif '购置' in text and '系统' not in text and '平台' not in text and '软件' not in text and '开发' not in text and '建设' not in text:
        excluded = True; reason = '纯购置服务'
    elif '租赁' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯租赁服务'
    elif '借用' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯借用服务'
    elif '调拨' in text and '系统' not in text and '平台' not in text:
        excluded = True; reason = '纯调拨服务'
    elif '处置' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯处置服务'
    elif '报废' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯报废服务'
    elif '回收' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯回收服务'
    elif '再利用' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯再利用服务'
    elif '循环' in text and '系统' not in text and '平台' not in text and '软件' not in text:
        excluded = True; reason = '纯循环服务'
    
    if excluded:
        results.append({
            'source': source, 'company': company, 'project': title,
            'pub_date': str(pub_date), 'decision': '排除', 'reason': reason
        })
    else:
        # 默认纳入
        results.append({
            'source': source, 'company': company, 'project': title,
            'pub_date': str(pub_date), 'decision': '纳入', 'reason': '需人工审核'
        })

# 输出结果
valid = [r for r in results if r['decision'] == '纳入']
excluded = [r for r in results if r['decision'] == '排除']

print(f'\n===== 最终汇总 =====')
print(f'纳入项目: {len(valid)}个')
print(f'排除项目: {len(excluded)}个')

print('\n===== 纳入项目（需人工审核）=====')
for i, p in enumerate(valid, 1):
    print(f'{i}. [{p["source"]}] {p["company"]}')
    print(f'   项目: {p["project"]}')
    print(f'   日期: {p["pub_date"]}')
    print()

print('\n===== 排除项目分类统计（前20）=====')
from collections import Counter
reasons = [r['reason'] for r in excluded]
for reason, count in Counter(reasons).most_common(20):
    print(f'{count:3d}个: {reason}')

# 保存结果
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/excel_analysis_results.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n结果已保存到 excel_analysis_results.json')
