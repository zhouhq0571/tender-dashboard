#!/usr/bin/env python3
"""
恒生银信招标看板 - 全面健康自检脚本
运行环境：Daimon 托管 Python 运行时
建议频率：每周一次（或每月一次）
触发方式：手动执行，或设为 cron 任务（每周一 9:00）
"""

import json, re, os, subprocess, sys
from datetime import datetime, date, timedelta

# ========== 配置 ==========
REPO_DIR = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily"
SKILL_PATH = "/Users/zhouhq/.kimi/daimon/skills/tender-daily-dispatch/SKILL.md"
HTML_PATH = os.path.join(REPO_DIR, "index.html")

# 排序权重定义（必须与 SKILL.md 和 index.html 完全一致）
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
VALID_TAGS = {
    '财富管理', '资产管理', '资产托管', '金融市场/资金/同业', '资金业务',
    '风控合规', '数据平台', '数据服务', '渠道系统', '信创/国产化',
    '运维服务', '人力外包', '大模型应用'
}
VALID_METHODS = {
    '公开招标', '邀请招标', '竞争性谈判', '竞争性磋商',
    '单一来源采购', '询价采购', '框架协议', '其他'
}
VALID_REGIONS = {'东北', '华北', '西北', '华东', '华中', '西南', '华南'}
VALID_PROVINCES = set(PROVINCE_ORDER.keys())

def parse_html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
    if not match:
        return None, content
    return json.loads(match.group(1)), content

def check_sorting(data):
    """检查排序是否正确"""
    projects = data['projects']
    def sort_key(p):
        return (
            REGION_ORDER.get(p.get('region', ''), 99),
            PROVINCE_ORDER.get(p.get('province', ''), 99),
            REC_PRIORITY.get(p.get('rec', ''), 99),
            p.get('deadline', '9999-99-99')
        )
    sorted_projects = sorted(projects, key=sort_key)
    is_sorted = all(sort_key(projects[i]) <= sort_key(projects[i+1]) for i in range(len(projects)-1))
    return {
        'check': '排序规则',
        'status': 'PASS' if is_sorted else 'FAIL',
        'detail': f'{len(projects)} 个项目，排序{"正确" if is_sorted else "错误"}'
    }

def check_duplicates(data):
    """检查重复项目"""
    seen = {}
    duplicates = []
    for p in data['projects']:
        key = p.get('company', '') + '|' + p.get('project', '')[:15]
        if key in seen:
            duplicates.append(f"{p.get('company', '')} - {p.get('project', '')[:30]} (id {seen[key]} vs {p.get('id', '?')})")
        seen[key] = p.get('id', '?')
    return {
        'check': '重复项目',
        'status': 'PASS' if not duplicates else 'WARN',
        'detail': '无重复' if not duplicates else f'发现 {len(duplicates)} 个重复: {duplicates[:3]}'
    }

def check_id_continuity(data):
    """检查 ID 连续性"""
    ids = [int(p['id']) for p in data['projects']]
    expected = list(range(1, len(data['projects']) + 1))
    is_continuous = ids == expected
    return {
        'check': 'ID 连续性',
        'status': 'PASS' if is_continuous else 'FAIL',
        'detail': f'1-{len(data["projects"])} 连续' if is_continuous else f'不连续: {ids[:5]}... vs {expected[:5]}...'
    }

def check_required_fields(data):
    """检查必填字段"""
    required = ['id', 'region', 'province', 'company', 'project', 'overview', 'deadline', 'method', 'contact', 'tags', 'rec', 'url']
    issues = []
    for p in data['projects']:
        for f in required:
            if f not in p or not p.get(f):
                issues.append(f"[id={p.get('id', '?')}] 缺少 {f}")
    return {
        'check': '必填字段完整性',
        'status': 'PASS' if not issues else 'FAIL',
        'detail': f'全部完整' if not issues else f'{len(issues)} 个问题: {issues[:3]}'
    }

def check_source_field(data):
    """检查 source 字段"""
    issues = []
    for p in data['projects']:
        src = p.get('source', '')
        if not src or src == 'undefined':
            issues.append(f"[id={p['id']}] {p['company']} source 缺失或 undefined")
    return {
        'check': 'source 字段',
        'status': 'PASS' if not issues else 'FAIL',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个问题: {issues[:3]}'
    }

def check_no_dash_overview(data):
    """检查 overview 不为 '-'"""
    issues = []
    for p in data['projects']:
        if p.get('overview') == '-':
            issues.append(f"[id={p['id']}] {p['company']}")
    return {
        'check': 'overview 不为 "-"',
        'status': 'PASS' if not issues else 'WARN',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个项目 overview="-"'
    }

def check_no_dash_contact(data):
    """检查 contact 不为 '-'"""
    issues = []
    for p in data['projects']:
        if p.get('contact') == '-':
            issues.append(f"[id={p['id']}] {p['company']}")
    return {
        'check': 'contact 不为 "-"',
        'status': 'PASS' if not issues else 'WARN',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个项目 contact="-"'
    }

def check_rec_values(data):
    """检查投标建议值有效性"""
    valid = set(REC_PRIORITY.keys())
    issues = []
    for p in data['projects']:
        if p.get('rec') not in valid:
            issues.append(f"[id={p['id']}] {p['company']}: '{p.get('rec')}'")
    return {
        'check': '投标建议有效性',
        'status': 'PASS' if not issues else 'FAIL',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个无效: {issues[:3]}'
    }

def check_method_values(data):
    """检查招标方式有效性"""
    issues = []
    for p in data['projects']:
        if p.get('method') not in VALID_METHODS:
            issues.append(f"[id={p['id']}] {p['company']}: '{p.get('method')}'")
    return {
        'check': '招标方式有效性',
        'status': 'PASS' if not issues else 'FAIL',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个无效: {issues[:3]}'
    }

def check_region_province_consistency(data):
    """检查 region/province 一致性"""
    region_province_map = {
        '东北': ['黑龙江', '吉林', '辽宁'],
        '华北': ['内蒙古', '北京', '天津', '河北', '山西'],
        '西北': ['陕西', '甘肃', '宁夏', '青海', '新疆'],
        '华东': ['山东', '江苏', '浙江', '安徽', '福建', '江西', '上海'],
        '华中': ['河南', '湖北', '湖南'],
        '西南': ['重庆', '四川', '贵州', '云南', '西藏'],
        '华南': ['广东', '广西', '海南'],
    }
    issues = []
    for p in data['projects']:
        r, prov = p.get('region', ''), p.get('province', '')
        if r in region_province_map and prov not in region_province_map[r]:
            issues.append(f"[id={p['id']}] {p['company']}: region='{r}' vs province='{prov}'")
    return {
        'check': '大区/省份一致性',
        'status': 'PASS' if not issues else 'FAIL',
        'detail': f'全部一致' if not issues else f'{len(issues)} 个不一致: {issues[:3]}'
    }

def check_tags_validity(data):
    """检查标签有效性"""
    issues = []
    for p in data['projects']:
        for t in p.get('tags', []):
            if t not in VALID_TAGS:
                issues.append(f"[id={p['id']}] {p['company']}: '{t}'")
    return {
        'check': '标签有效性',
        'status': 'PASS' if not issues else 'WARN',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个无效标签: {issues[:3]}'
    }

def check_title_tag(data, content):
    """检查 <title> 标签是否与版本号/日期一致"""
    title_match = re.search(r'<title>(.*?)</title>', content)
    if not title_match:
        return {'check': 'title 标签', 'status': 'FAIL', 'detail': '未找到 <title> 标签'}
    
    title = title_match.group(1)
    expected_date = data.get('date', '')
    expected_version = data.get('version', '')
    
    # 检查 title 中是否包含日期和版本号
    date_ok = expected_date in title
    version_ok = expected_version in title
    
    status = 'PASS' if (date_ok and version_ok) else 'FAIL'
    detail = f'title="{title[:50]}...", 日期匹配: {date_ok}, 版本匹配: {version_ok}'
    
    return {
        'check': 'title 标签一致性',
        'status': status,
        'detail': detail
    }

def check_deadline_format(data):
    """检查 deadline 格式（不应为纯 '-'）"""
    issues = []
    for p in data['projects']:
        dl = p.get('deadline', '')
        if dl == '-':
            issues.append(f"[id={p['id']}] {p['company']}")
    return {
        'check': 'deadline 格式',
        'status': 'PASS' if not issues else 'WARN',
        'detail': f'全部有效' if not issues else f'{len(issues)} 个 deadline="-"'
    }

def check_stale_projects(data):
    """检查已截止项目是否堆积（超过昨天+1天）"""
    today = date.today()
    cutoff = today - timedelta(days=2)
    issues = []
    for p in data['projects']:
        rec = p.get('rec', '')
        if '已截止' not in rec:
            continue
        dl = p.get('deadline', '')
        m = re.search(r'(\d{4}-\d{2}-\d{2})', str(dl))
        if m:
            dl_date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
            if dl_date < cutoff:
                issues.append(f"[id={p['id']}] {p['company']} deadline={dl} (早于 {cutoff})")
    return {
        'check': '已截止项目堆积',
        'status': 'PASS' if not issues else 'WARN',
        'detail': f'无堆积' if not issues else f'{len(issues)} 个项目已过期但未删除'
    }

def check_skill_version_sync():
    """检查 SKILL.md 中 PROVINCE_ORDER 与 index.html 是否一致"""
    with open(SKILL_PATH, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 精确提取 SKILL.md 中 PROVINCE_ORDER 定义区域
    skill_match = re.search(r'PROVINCE_ORDER = \{(.*?)\n\}', skill_content, re.DOTALL)
    html_match = re.search(r'PROVINCE_ORDER = \{(.*?)\n\};', html_content, re.DOTALL)
    
    if not skill_match or not html_match:
        return {
            'check': 'SKILL.md 与 index.html 排序定义一致性',
            'status': 'WARN',
            'detail': '无法定位 PROVINCE_ORDER 定义'
        }
    
    # 提取省份:数值对
    skill_pairs = set(re.findall(r"'([^']+)':\s*(\d+)", skill_match.group(1)))
    html_pairs = set(re.findall(r"'([^']+)':\s*(\d+)", html_match.group(1)))
    
    match = skill_pairs == html_pairs
    return {
        'check': 'SKILL.md 与 index.html 排序定义一致性',
        'status': 'PASS' if match else 'FAIL',
        'detail': f'PROVINCE_ORDER 一致 ({len(skill_pairs)} 项)' if match else f'不一致: SKILL={len(skill_pairs)}项, HTML={len(html_pairs)}项'
    }

def check_cron_status():
    """检查 cron 定时任务状态（通过调用外部 cron 工具）"""
    # 这里无法直接调用 Cron 工具，记录为需要人工检查
    return {
        'check': 'cron 定时任务状态',
        'status': 'INFO',
        'detail': '请手动运行: Cron(action="status") 查看 3 个任务是否启用且最近有执行记录'
    }

def run_all_checks():
    data, content = parse_html()
    if not data:
        print("❌ 无法解析 index.html，请检查文件")
        sys.exit(1)
    
    results = []
    
    # 数据检查
    results.append(check_sorting(data))
    results.append(check_duplicates(data))
    results.append(check_id_continuity(data))
    results.append(check_required_fields(data))
    results.append(check_source_field(data))
    results.append(check_no_dash_overview(data))
    results.append(check_no_dash_contact(data))
    results.append(check_rec_values(data))
    results.append(check_method_values(data))
    results.append(check_region_province_consistency(data))
    results.append(check_tags_validity(data))
    results.append(check_deadline_format(data))
    results.append(check_stale_projects(data))
    results.append(check_title_tag(data, content))
    
    # 规则/脚本检查
    results.append(check_skill_version_sync())
    results.append(check_cron_status())
    
    # 输出报告
    print("=" * 60)
    print(f"恒生银信招标看板 - 全面健康自检报告")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"版本: {data.get('version', '?')}, 项目数: {len(data['projects'])}")
    print("=" * 60)
    print()
    
    pass_count = fail_count = warn_count = 0
    for r in results:
        status = r['status']
        icon = {'PASS': '✅', 'FAIL': '❌', 'WARN': '⚠️', 'INFO': 'ℹ️'}.get(status, '?')
        print(f"{icon} {r['check']:30s} [{status:4s}] {r['detail']}")
        if status == 'PASS': pass_count += 1
        elif status == 'FAIL': fail_count += 1
        elif status == 'WARN': warn_count += 1
    
    print()
    print("-" * 60)
    print(f"总计: {pass_count} 通过, {fail_count} 失败, {warn_count} 警告, {len(results)-pass_count-fail_count-warn_count} 信息")
    
    if fail_count > 0:
        print(f"\n❌ 发现 {fail_count} 个失败项，需要立即修复！")
        sys.exit(1)
    elif warn_count > 0:
        print(f"\n⚠️ 发现 {warn_count} 个警告项，建议关注但无需立即修复。")
        sys.exit(0)
    else:
        print(f"\n✅ 所有检查通过，系统健康！")
        sys.exit(0)

if __name__ == '__main__':
    run_all_checks()
