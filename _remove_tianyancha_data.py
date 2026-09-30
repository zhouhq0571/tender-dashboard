import json, os, re, glob, csv

report = {'files_modified': [], 'total_tyc_records': 0, 'total_csv_tyc': 0}

BASE_DIR = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily'

# URL -> source 映射规则
URL_MAP = {
    'ctbpsp.com': '中国招标投标公共服务平台',
    'cfcpn.com': '金采网',
    'qianlima.com': '千里马招标网',
    'cqrcb.com': '重庆农商行官网',
    'szecp.crc.com.cn': '华润集团电子招标平台',
    'ksrcb.cn': '昆山农商行官网',
    'gfcg.cgbchina.com.cn': '广银理财采购平台',
    'sntba.com': '陕西招标投标信息网',
    'crpsz.com': '华润集团招标平台',
    'swueecg.com': '西南大学电子招标平台',
    'jszbcg.com': '江苏省招标中心',
    'szecp.com.cn': '深圳电子招标平台',
    'qdygcg.com': '青岛阳光采购平台',
    'ec.chng.com.cn': '华能集团电子招标平台',
    'scm.esinochem.com': '中国中化电子招标平台',
    'ahtba.org.cn': '安徽招标投标信息网',
    'gjpt.ahtba.org.cn': '安徽公共资源交易平台',
    'chengezhao.com': '中国招标投标公共服务平台',
}

def resolve_source_by_url(url):
    if not url:
        return '信息来源待确认'
    for domain, source_name in URL_MAP.items():
        if domain in url:
            return source_name
    return '信息来源待确认'

def is_tyc_source(val):
    return isinstance(val, str) and '天眼查' in val

def clean_source(val, url):
    if is_tyc_source(val):
        new_source = resolve_source_by_url(url)
        if new_source != '信息来源待确认':
            return new_source
        return '千里马招标网'
    return val

def clean_contact(val):
    if isinstance(val, str) and '' in val:
        return val.replace('', '').replace('', '').replace('', '')
    return val

def deep_clean_dict(obj, changes_ref):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'source' and is_tyc_source(v):
                url = obj.get('url', '') or obj.get('link', '') or obj.get('href', '') or obj.get('source_url', '') or ''
                obj[k] = clean_source(v, url)
                changes_ref[0] += 1
            elif k == 'contact' and isinstance(v, str) and '天眼查' in v:
                obj[k] = clean_contact(v)
                changes_ref[0] += 1
            else:
                deep_clean_dict(v, changes_ref)
    elif isinstance(obj, list):
        for item in obj:
            deep_clean_dict(item, changes_ref)

def process_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f'  [SKIP] {os.path.basename(filepath)}: JSON parse error: {e}')
        return 0

    changes_ref = [0]
    deep_clean_dict(data, changes_ref)

    if changes_ref[0] > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'  [OK] {os.path.basename(filepath)}: {changes_ref[0]} records updated')
    return changes_ref[0]

def process_csv_file(filepath):
    changes = 0
    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                modified = False
                for k in list(row.keys()):
                    v = row[k]
                    if k in ('source', '信息来源') and is_tyc_source(v):
                        url = row.get('url', '') or row.get('link', '') or row.get('href', '') or row.get('原始链接', '') or ''
                        row[k] = clean_source(v, url)
                        changes += 1
                        modified = True
                    elif k == 'contact' and isinstance(v, str) and '天眼查' in v:
                        row[k] = clean_contact(v)
                        changes += 1
                        modified = True
                rows.append(row)
    except Exception as e:
        print(f'  [SKIP] {os.path.basename(filepath)}: CSV error: {e}')
        return 0

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f'  [OK] {os.path.basename(filepath)}: {changes} records updated')
    return changes

def process_python_file(filepath):
    changes = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0

    original = content
    # Replace hardcoded source assignments containing 天眼查
    content = re.sub(r"source\s*[=:]\s*['\"]天眼查[^'\"]*['\"]", lambda m: m.group(0).replace(re.search(r"['\"]天眼查[^'\"]*['\"]", m.group(0)).group(0), "'千里马招标网''), content)
    # Replace contact strings containing 
    content = re.sub(r'['\"][^'\']*[^'\"]*['\"]", lambda m: "'" + m.group(0)[1:-1].replace('', '').replace('', '').replace('', '') + "'", content)
    if content != original:
        changes = original.count('天眼查') - content.count('天眼查')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  [OK] {os.path.basename(filepath)}: source/contact updated')
    return changes

# ===== 遍历所有文件（递归） =====
def collect_files(base_dir, extensions):
    result = []
    for root, dirs, files in os.walk(base_dir):
        # 排除 backup, backups, archive 目录
        dirs[:] = [d for d in dirs if d.lower() not in ('backup', 'backups', 'archive')]
        for f in files:
            if f.endswith(extensions):
                result.append(os.path.join(root, f))
    return result

all_files = collect_files(BASE_DIR, ('.json', '.csv', '.py'))
json_files = [f for f in all_files if f.endswith('.json')]
csv_files = [f for f in all_files if f.endswith('.csv')]
py_files = [f for f in all_files if f.endswith('.py')]

print('\n=== Processing JSON files ===')
for filepath in sorted(json_files):
    c = process_json_file(filepath)
    if c > 0:
        report['files_modified'].append({'file': os.path.relpath(filepath, BASE_DIR), 'changes': c})
        report['total_tyc_records'] += c

print('\n=== Processing CSV files ===')
for filepath in sorted(csv_files):
    c = process_csv_file(filepath)
    if c > 0:
        report['files_modified'].append({'file': os.path.relpath(filepath, BASE_DIR), 'changes': c})
        report['total_csv_tyc'] += c

print('\n=== Processing Python scripts ===')
for filepath in sorted(py_files):
    c = process_python_file(filepath)
    if c > 0:
        report['files_modified'].append({'file': os.path.relpath(filepath, BASE_DIR), 'changes': c})

print('\n=== Summary ===')
print(f'JSON records updated: {report["total_tyc_records"]}')
print(f'CSV records updated: {report["total_csv_tyc"]}')
print(f'Files modified: {len(report["files_modified"])}')
for item in report['files_modified']:
    print(f'  - {item["file"]}: {item["changes"]} changes')
