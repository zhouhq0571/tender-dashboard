import json, re
HTML = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'
html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
urls = [p['url'] for p in data['projects']]
new_url = 'https://www.cebpubservice.com'
assert new_url not in urls, 'url not unique'
for p in data['projects']:
    if p['id'] == 126:
        p['url'] = new_url
        p['overview'] = p['overview'].rstrip('。') + '。公告原文见中国招标投标公共服务平台（cebpubservice.com）检索“蒙商银行 风险计量”。'
new_json = json.dumps(data, ensure_ascii=False, indent=1)
html_new = html[:m.start(2)] + '\n' + new_json + '\n' + html[m.end(2):]
open(HTML, 'w', encoding='utf-8').write(html_new)
print('fixed id 126 url')
