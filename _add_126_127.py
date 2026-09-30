import json, re, sys, shutil, datetime
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from config import sort_key, VALID_TAGS

HTML = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'
html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
projects = data['projects']
ids = {p['id'] for p in projects}
assert 126 not in ids and 127 not in ids, "id conflict"

new_projects = [
    {
        "id": 126,
        "region": "华北",
        "province": "内蒙古",
        "company": "蒙商银行",
        "project": "2026-2029年风险计量、估值模型及资产托管数据源服务项目（二次）（竞争性磋商）",
        "overview": "风险计量、估值模型及资产托管数据源服务，服务期2026-2029年。项目地点：内蒙古包头。发布时间：2026-08-31。",
        "budget": "46.16万元",
        "deadline": "2026-09-11",
        "method": "竞争性磋商",
        "contact": "-",
        "tags": ["风控合规", "数据服务"],
        "rec": "⭐ ★★☆ 建议投标",
        "url": "-",
        "source": "快查App查招标导出+脉拓宝补全",
        "date": "2026-08-31"
    },
    {
        "id": 127,
        "region": "华北",
        "province": "北京",
        "company": "中信银行",
        "project": "资产托管核算系统2026年政策性需求产品升级包采购项目（公开招标）",
        "overview": "资产托管核算系统2026年政策性需求产品升级包，含12项政策性需求改造（XBRL信披、估值表穿透、北交所ETF等）。项目编号0733-26143855。开标时间2026-09-10 09:30。发布时间：2026-08-20。",
        "budget": "-",
        "deadline": "2026-09-10 09:30",
        "method": "公开招标",
        "contact": "中信国际招标有限公司：石辛迪、原菲、王璟琳 010-87945198-575/577",
        "tags": ["资产托管"],
        "rec": "⭐ ★★☆ 建议投标",
        "url": "https://ebid.group.citic",
        "source": "快查App查招标导出+中信金控采购共享平台(ebid.group.citic)",
        "date": "2026-08-20"
    }
]
for p in new_projects:
    for t in p['tags']:
        assert t in VALID_TAGS, "invalid tag " + t

projects.extend(new_projects)
projects.sort(key=sort_key)
data['projects'] = projects
data['version'] = 'v209'

new_json = json.dumps(data, ensure_ascii=False, indent=1)
html_new = html[:m.start(2)] + '\n' + new_json + '\n' + html[m.end(2):]
html_new = html_new.replace('（更新）v208</title>', '（更新）v209</title>')
assert 'v209</title>' in html_new
html_new = re.sub(r'<!-- Deployed v\d+ at [^>]*-->',
    '<!-- Deployed v209 at %s -->' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    html_new)
shutil.copy(HTML, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html.v208.backup')
open(HTML, 'w', encoding='utf-8').write(html_new)
print("OK: version v209, projects =", len(projects))
for p in projects:
    if p['id'] in (126, 127):
        print(json.dumps(p, ensure_ascii=False, indent=1))
