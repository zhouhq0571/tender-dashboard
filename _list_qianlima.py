import json

text = open('index.html', 'r', encoding='utf-8').read()
start = text.find('<script type="application/json" id="tender-data">')
start = text.find('{', start)
end = text.find('</script>', start)
json_text = text[start:end].strip()
data = json.loads(json_text)
ps = data.get('projects', [])

qianlima = [(i, p) for i, p in enumerate(ps) if '千里马' in p.get('source', '') or 'qianlima.com' in p.get('url', '')]
print(f'千里马来源项目总数: {len(qianlima)}')
for idx, (i, p) in enumerate(qianlima):
    print(f'{idx}: [{i}] {p["company"]} | {p["project"]} | {p["url"][:80]}')
