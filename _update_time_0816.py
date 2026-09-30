import json

text = open('index.html', 'r', encoding='utf-8').read()
start = text.find('<script type="application/json" id="tender-data">')
start = text.find('{', start)
end = text.find('</script>', start)
json_text = text[start:end].strip()
data = json.loads(json_text)

data['date'] = '2026年08月16日'
data['timePeriod'] = '上午'
old_ver = data.get('version', 'v155')
num = int(old_ver.replace('v', ''))
data['version'] = f'v{num + 1}'

print(f"version: {data['version']}, date: {data['date']}, timePeriod: {data['timePeriod']}, projects: {len(data.get('projects', []))}")

new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_html = text[:start] + new_json + text[end:]
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print('updated')
