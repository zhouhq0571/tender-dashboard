#!/usr/bin/env python3
"""
招标看板新增项目验证脚本
用法: python3 validate_new_projects.py

修改记录：
  2026-07-11: 统一从 config.py 导入常量
"""

import json
import re
import sys

from config import VALID_REGIONS, VALID_METHODS, VALID_RECS, VALID_TAGS, BLOCKED_SOURCE_PATTERNS, normalize_source as _normalize_source, normalize_company as _normalize_company, company_board_scope

HTML_FILE = 'index.html'

# 2026-11-20 机构范围硬检的待确认收集（warn 不拦截但报告必须可见）
SCOPE_WARNINGS = []

REQUIRED_FIELDS = ['id', 'company', 'project', 'overview', 'budget', 'deadline', 
                   'method', 'contact', 'region', 'province', 'tags', 'rec', 'url', 'source']

def load_projects():
    """加载看板数据"""
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
    if not match:
        print("❌ 错误: 无法找到项目数据")
        sys.exit(1)
    
    data = json.loads(match.group(1))
    return data.get('projects', [])

def check_field_names(project):
    """检查字段名是否正确"""
    errors = []
    if 'description' in project:
        errors.append(f"使用了错误字段名 'description'，应该用 'overview'")
    if 'suggestion' in project:
        errors.append(f"使用了错误字段名 'suggestion'，应该用 'rec'")
    return errors

def check_required_fields(project):
    """检查必填字段是否完整"""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in project or project[field] is None or project[field] == '':
            errors.append(f"缺少必填字段: {field}")
    return errors

def check_field_values(project):
    """检查字段值是否规范"""
    errors = []
    
    if project.get('region') not in VALID_REGIONS:
        errors.append(f"region值不规范: '{project.get('region')}'，应为: {VALID_REGIONS}")
    
    if project.get('rec') not in VALID_RECS:
        errors.append(f"rec值不规范: '{project.get('rec')}'，应为: {VALID_RECS}")

    # 2026-09-30 新增：招标方式白名单硬检（根治"征集调研/谈判采购/公开招标（入围）"等非标准值混入，
    # 映射口径见 SKILL.md 步骤2.7）
    if project.get('method') not in VALID_METHODS:
        errors.append(f"method值不规范: '{project.get('method')}'，只能取10种标准值: {sorted(VALID_METHODS)}")

    # 2026-09-30 新增：信息来源归一化硬检（根治"千里马订阅/（微信公众号）"等同一信源多种写法，
    # 口径见 config.SOURCE_ALIASES；新来源须用规范全名，渠道差异不入 source）
    src = project.get('source') or ''
    if any(pat in src for pat in BLOCKED_SOURCE_PATTERNS):
        errors.append(f"source值不规范: '{src}'，同一信源只许一种写法（如 千里马订阅→千里马招标网、"
                      f"（微信公众号）→（公众号）），别名表见 config.SOURCE_ALIASES")

    # 2026-10-15 新增：规范全名硬检（根治裸写"银行科技研究社"漏（公众号）后缀等；
    # 口径：normalize_source(src) != src 即非规范写法，别名表见 config.SOURCE_ALIASES）
    if _normalize_source(src) != src.strip():
        errors.append(f"source非规范全名: '{src}'，归一后应为 '{_normalize_source(src)}'"
                      f"（网站类裸名/公众号类带（公众号）后缀），见 config.SOURCE_ALIASES")

    # 2026-11-19 新增：招标单位简称硬检（根治"北京农村商业银行股份有限公司"等全称上板，
    # 失守根因=映射只写在 SKILL.md 无代码消费；口径：normalize_company(c) != c 即非规范写法，
    # 映射表见 config.COMPANY_SHORT_MAP，新增简称只改 config.py）
    comp = project.get('company') or ''
    if _normalize_company(comp) != comp.strip():
        errors.append(f"company非规范简称: '{comp}'，归一后应为 '{_normalize_company(comp)}'"
                      f"（映射表见 config.COMPANY_SHORT_MAP）")

    # 2026-11-20 新增：机构范围硬检（步骤2.5条件1代码化，根治 JSONL 批次直接信上游 is_fin_inst
    # 宽口径致保险/证券/基金条目混入送审，用户 00:09 抓包；口径见 config.company_board_scope）
    _verdict, _scope_reason = company_board_scope(comp)
    if _verdict == 'block':
        errors.append(f"company机构范围越界: '{comp}'（{_scope_reason}）；银信标讯看板只纳银行/理财子/信托/银行系金科，"
                      f"保险/证券/基金/期货/AIC/集团财务公司请在周报通道使用")
    elif _verdict == 'warn':
        SCOPE_WARNINGS.append(f"ID {project.get('id')} company机构类型待确认: '{comp}'（{_scope_reason}）")

    if not isinstance(project.get('tags'), list):
        errors.append("tags必须是数组")
    else:
        # 2026-11-19 新增：业务标签白名单硬检（对照 11-19 全字段代码闸自查补齐，
        # 与看板导航 15 个标准标签同源 config.VALID_TAGS；越界标签即拦截，新增标签只改 config.py）
        _bad_tags = [t for t in project['tags'] if t not in VALID_TAGS]
        if _bad_tags:
            errors.append(f"tags越界: {_bad_tags}，只许标准标签: {sorted(VALID_TAGS)}")

    # 2026-10-30 规则 O-联系方式：增量硬检（id >= CONTACT_HARD_CHECK_MIN_ID 的项目禁止空联系方式）
    try:
        from config import CONTACT_HARD_CHECK_MIN_ID as _cmin
    except Exception:
        _cmin = 10**9
    _c = str(project.get('contact') or '').strip()
    if isinstance(project.get('id'), int) and project.get('id') >= _cmin and _c in ('', '-', '/', '无', '暂无'):
        errors.append("contact为空（规则 O-联系方式：新上板必须带真实项目咨询/联系方式，"
                      "用 tools/ql_vip_fetch.py extract_contact 从公告提取；快查来源至少填代理机构名）")
    
    url = project.get('url', '')
    if not url.startswith('http'):
        errors.append(f"URL格式错误: {url}")
    # 2026-10-30：平台首页占位 URL 硬检（新增项目）
    _u = url.strip().rstrip('/')
    if isinstance(project.get('id'), int) and project.get('id') >= _cmin and \
            _u in ('https://www.kuaicha365.com', 'http://www.kuaicha365.com'):
        errors.append("url为快查首页占位（快查来源应用 url_id 拼 /outer/tender-bid/project-process 详情链接）")
    
    overview = project.get('overview', '')
    if len(overview) < 10:
        errors.append(f"overview太短（{len(overview)}字），应至少10字")

    # 2026-11-02 规则 P-预算纯金额：全场景硬检（2026-08-24 立规"预算金额字段只写金额"此前未固化，
    # 致"未披露/1500万元（预估）/954万元（最高限价，含税）"等修饰字样混入，用户 11-02 质检查获）。
    # 只允许：纯金额（如 60万元 / 500元）或 '-'；未知金额一律 '-'，备注性字样只能写进 overview。
    # 口径唯一来源 config.BUDGET_OK_RE / normalize_budget。
    from config import BUDGET_OK_RE as _BUDGET_OK_RE
    _b = str(project.get('budget') or '').strip()
    if not _BUDGET_OK_RE.fullmatch(_b):
        errors.append(f"budget含修饰字样: '{_b}'，只许纯金额（如 60万元）或 '-'，"
                      f"未披露/预估/最高限价/含税等备注写入 overview")

    return errors

def check_url_uniqueness(project, all_projects):
    """检查URL是否重复"""
    errors = []
    url = project.get('url', '')
    duplicates = [p for p in all_projects if p.get('url') == url and p.get('id') != project.get('id')]
    if duplicates:
        errors.append(f"URL重复: {url} (与ID {duplicates[0]['id']}重复)")
    return errors

def check_url_content(project):
    """检查URL是否为分类页面"""
    errors = []
    url = project.get('url', '')
    suspicious_patterns = ['/industry/', '/area/', '/category/', '/list/']
    for pattern in suspicious_patterns:
        if pattern in url:
            errors.append(f"URL可能是分类页面: {url} (包含 {pattern})")
            break
    return errors

def validate_all():
    """验证所有项目"""
    projects = load_projects()
    
    print(f"=" * 60)
    print(f"招标看板项目验证报告")
    print(f"=" * 60)
    print(f"总项目数: {len(projects)}")
    print()
    
    total_errors = 0
    
    for p in projects:
        pid = p.get('id')
        company = p.get('company', '')
        project_name = p.get('project', '')[:30]
        
        errors = []
        errors.extend(check_field_names(p))
        errors.extend(check_required_fields(p))
        errors.extend(check_field_values(p))
        errors.extend(check_url_uniqueness(p, projects))
        errors.extend(check_url_content(p))
        
        if errors:
            total_errors += len(errors)
            print(f"❌ ID {pid} [{company}] {project_name}")
            for err in errors:
                print(f"   - {err}")
            print()
    
    print("=" * 60)
    if SCOPE_WARNINGS:
        print(f"⚠️ 机构类型待确认 {len(SCOPE_WARNINGS)} 条（不拦截，须人工确认）:")
        for w in SCOPE_WARNINGS:
            print(f"   - {w}")
        print()
    if total_errors == 0:
        print("✅ 验证通过！所有项目检查无误。")
        return 0
    else:
        print(f"❌ 发现 {total_errors} 个问题，请修复后再部署。")
        return 1

if __name__ == '__main__':
    sys.exit(validate_all())
