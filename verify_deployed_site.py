#!/usr/bin/env python3
"""
部署后强制验证脚本
用途：部署后从实际网站抓取数据，验证每个项目字段完整性
禁止：此脚本不得修改任何文件，只读取和报告
"""
import json, re, urllib.request, sys

def main():
    url = 'https://hstender.cn/'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
    })
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        html = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ 无法访问网站: {e}")
        sys.exit(1)
    
    # 提取JSON数据
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
    if not m:
        print("❌ 网站HTML中未找到JSON数据")
        sys.exit(1)
    
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        sys.exit(1)
    
    projects = data.get('projects', [])
    
    # 验证每个项目的关键字段
    required_fields = ['id', 'company', 'project', 'overview', 'budget', 'deadline', 'method', 'contact', 'tags', 'rec', 'url', 'source', 'region', 'province']
    
    bad_projects = []
    for p in projects:
        missing = [f for f in required_fields if not p.get(f)]
        if missing:
            bad_projects.append({
                'id': p.get('id'),
                'company': p.get('company'),
                'project': p.get('project'),
                'missing': missing
            })
    
    # 报告结果
    print(f"✅ 版本: {data.get('version', '未知')}")
    print(f"✅ 日期: {data.get('date', '未知')} {data.get('timePeriod', '未知')}")
    print(f"✅ 项目总数: {len(projects)}")
    
    if bad_projects:
        print(f"\n❌ 发现 {len(bad_projects)} 个项目字段缺失:")
        for bp in bad_projects:
            print(f"  ID {bp['id']}: {bp['company']} - {bp['project']}")
            print(f"    缺失字段: {', '.join(bp['missing'])}")
        print("\n❌ 验证失败！请立即回退并修复！")
        sys.exit(1)
    else:
        print(f"✅ 所有 {len(projects)} 个项目字段完整")
        print("✅ 部署后验证通过！")
        sys.exit(0)

if __name__ == '__main__':
    main()
