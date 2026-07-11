#!/usr/bin/env python3
"""
招标看板新增项目验证脚本
用法: python3 validate_new_projects.py
"""

import json
import re
import urllib.request
import sys

HTML_FILE = 'index.html'

# 规范值定义
VALID_REGIONS = ['东北', '华北', '华东', '华中', '华南', '西南', '西北', '-']
VALID_RECS = ['🔥 ★★★ 强烈建议投标', '⭐ ★★☆ 建议投标', '👀 ★☆☆ 可关注', '☆☆☆ 已截止', '☆☆☆ 不建议']
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
    """检查字段名是否正确（避免description/suggestion等错误字段名）"""
    errors = []
    
    # 检查是否使用了错误的字段名
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
    
    # 检查region
    if project.get('region') not in VALID_REGIONS:
        errors.append(f"region值不规范: '{project.get('region')}'，应为: {VALID_REGIONS}")
    
    # 检查rec
    if project.get('rec') not in VALID_RECS:
        errors.append(f"rec值不规范: '{project.get('rec')}'，应为: {VALID_RECS}")
    
    # 检查tags是数组
    if not isinstance(project.get('tags'), list):
        errors.append("tags必须是数组")
    
    # 检查url格式
    url = project.get('url', '')
    if not url.startswith('http'):
        errors.append(f"URL格式错误: {url}")
    
    # 检查overview长度
    overview = project.get('overview', '')
    if len(overview) < 10:
        errors.append(f"overview太短（{len(overview)}字），应至少10字")
    
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
    """检查URL是否为分类页面（简单启发式检查）"""
    errors = []
    url = project.get('url', '')
    
    # 检查是否是分类页面URL
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
    if total_errors == 0:
        print("✅ 验证通过！所有项目检查无误。")
        return 0
    else:
        print(f"❌ 发现 {total_errors} 个问题，请修复后再部署。")
        return 1

if __name__ == '__main__':
    sys.exit(validate_all())
