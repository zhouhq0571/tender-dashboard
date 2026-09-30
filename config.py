#!/usr/bin/env python3
"""
招标看板 - 统一配置文件
用途：集中定义所有常量，确保各脚本一致性

使用方式：
    from config import REC_PRIORITY, REGION_ORDER, PROVINCE_ORDER, VALID_TAGS, VALID_METHODS

修改此文件后，所有引用脚本自动生效。
"""

# ========== 排序权重定义（与 index.html JS 完全一致）==========
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

# ========== 有效性定义 ==========
# 标准业务标签（15个，2026-09-07 用户确认：新增"公司金融"（票据/财资/支付/国结/资金监管/三方存管/银证转账类，
# 对应恒生启金业务范畴）；"金融市场/资金/同业"更名为"金市/资金/同业"。与每日任务 prompt 数据字典、
# SKILL.md 固定标准标签列表、看板筛选按钮四方一致。
# 标准标签中没有"资金业务"、"人力外包入围"、"核心系统"、"咨询服务"；
# "其他"为合法标签，仅用于确实不属于其他类别的项目）
VALID_TAGS = {
    '财富管理', '资产管理', '资产托管', '资产服务信托', '金市/资金/同业', '公司金融',
    '风控合规', '数据平台', '数据服务', '渠道系统', '信创',
    '运维服务', '人力外包', '大模型应用', '其他'
}

VALID_METHODS = {
    '公开招标', '邀请招标', '竞争性谈判', '竞争性磋商',
    '单一来源采购', '询价采购', '框架协议', '供应商征集', '比选采购', '其他'
}

# 2026-09-30 新增：信息来源归一化（同一信源只许一种写法）
# 用法：写入前一律过 normalize_source()；BLOCKED_SOURCE_PATTERNS 用于硬检拦截别名
SOURCE_ALIASES = {
    '千里马订阅': '千里马招标网',
    '千里马招标网订阅': '千里马招标网',
    '千里马招标网（订阅）': '千里马招标网',
    '银行科技研究社（微信公众号）': '银行科技研究社（公众号）',
    '微信公众号（银行科技研究社）': '银行科技研究社（公众号）',
}

# 来源中出现以下特征即判定为别名/非规范写法，硬检直接拦截
# （"XX订阅"本质是XX，渠道差异不入 source；公众号只写（公众号））
BLOCKED_SOURCE_PATTERNS = ('订阅', '（微信公众号）', '微信公众号（', '千里马招标网（')


def normalize_source(s):
    """信息来源归一化：先查别名表，再清尾部渠道括注（如 千里马招标网（天津银行招标公告））"""
    s = (s or '').strip()
    if s in SOURCE_ALIASES:
        return SOURCE_ALIASES[s]
    for main in ('千里马招标网',):
        if s.startswith(main):
            return main
    return s

VALID_REGIONS = {'东北', '华北', '西北', '华东', '华中', '西南', '华南'}
VALID_PROVINCES = set(PROVINCE_ORDER.keys())

# 投标建议的所有有效值（用于验证）
VALID_RECS = list(REC_PRIORITY.keys())

# ========== 路径配置 ==========
REPO_DIR = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily"
HTML_PATH = f"{REPO_DIR}/index.html"
SKILL_PATH = "/Users/zhouhq/.kimi/daimon/skills/tender-daily-dispatch/SKILL.md"

# ========== 排序键函数（供各脚本使用）==========
def sort_key(p):
    """
    统一的排序键函数
    与 index.html 中的 JavaScript 排序逻辑完全一致
    
    排序规则：大区 → 省份 → 投标建议优先级 → 截止日期
    """
    return (
        REGION_ORDER.get(p.get('region', ''), 99),
        PROVINCE_ORDER.get(p.get('province', ''), 99),
        REC_PRIORITY.get(p.get('rec', ''), 99),
        p.get('deadline', '9999-99-99')
    )

def parse_deadline(d):
    """解析截止日期，返回可比较的字符串"""
    if not d or d == '-' or '另行通知' in str(d):
        return '9999-99-99'
    import re
    m = re.search(r'(\d{4}-\d{2}-\d{2})', str(d))
    if m:
        return m.group(1)
    return '9999-99-99'
