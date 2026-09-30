import json, sys

d = json.load(open('baseline_before_update.json', 'r', encoding='utf-8'))
projects = d.get('projects', d if isinstance(d, list) else [])

keywords = [
    ('九江银行', 'AI测试平台'),
    ('广州农村商业银行', '数据脱敏'),
    ('广州农村商业银行', '重点目标客群'),
    ('黄河农村商业银行', 'Oracle'),
    ('黄河农商银行', 'Oracle'),
]

found = []
for p in projects:
    company = p.get('company', '')
    project = p.get('project', '')
    for comp_kw, proj_kw in keywords:
        if comp_kw in company and proj_kw in project:
            found.append(p)
            break

print(f"FOUND={len(found)}")
for p in found:
    print(f"---")
    print(f"company={p.get('company')}")
    print(f"project={p.get('project')}")
    print(f"deadline={p.get('deadline')}")
    print(f"budget={p.get('budget')}")
    print(f"tags={p.get('tags')}")
    print(f"rec={p.get('rec')}")
    print(f"url={p.get('url')}")
