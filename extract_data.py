import json, re, sys

html = open('index.html', encoding='utf-8').read()
m = re.search(r'<script type=["\']application/json["\'] id=["\']tender-data["\']>(.+?)</script>', html, re.S)
if m:
    data = json.loads(m.group(1))
    print('Projects:', len(data['projects']))
    print('Version:', data.get('version'))
    print('Date:', data.get('date'))
    # Save to file for next step
    with open('/tmp/current_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
else:
    print('ERROR: tender-data not found')
    sys.exit(1)
