#!/usr/bin/env python3
"""2026-09-28 用户确认纳入候选 2、3、6、7、8、9（3号建议投标→可关注），v271 → bump_version 处理"""
import re, json, sys
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
from config import sort_key, VALID_TAGS, VALID_METHODS

INDEX = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'

NEW = [
 {
  "id": 286, "region": "华北", "province": "北京", "company": "中信信托",
  "project": "综合办公系统OA2026年需求开发项目",
  "overview": "综合办公系统OA需求开发（人力外包），报名截止2026-10-13，投标日期待开标通知。",
  "budget": "-", "deadline": "2026-10-13", "method": "公开招标", "contact": "-",
  "tags": ["人力外包"], "rec": "👀 ★☆☆ 可关注",
  "url": "https://www.qianlima.com/bid-634760158.html", "source": "千里马招标网"
 },
 {
  "id": 287, "region": "华北", "province": "北京", "company": "光大银行",
  "project": "“财富阶梯”数字化投顾能力升级咨询项目",
  "overview": "数字化投顾能力升级咨询服务，项目编号0686-26200A296086N，投标截止2026-10-10。",
  "budget": "-", "deadline": "2026-10-10", "method": "公开招标", "contact": "-",
  "tags": ["财富管理"], "rec": "👀 ★☆☆ 可关注",
  "url": "https://www.qianlima.com/bid-634732141.html", "source": "千里马招标网"
 },
 {
  "id": 288, "region": "华南", "province": "广西", "company": "广西北部湾银行",
  "project": "数字人民币2.0层系统测试项目",
  "overview": "数字人民币2.0层系统测试（竞争性磋商），响应文件递交截止2026-10-08 18:00。",
  "budget": "-", "deadline": "2026-10-08 18:00", "method": "竞争性磋商", "contact": "-",
  "tags": ["公司金融"], "rec": "👀 ★☆☆ 可关注",
  "url": "https://www.mpaypass.com.cn/news/202609/27142906.html", "source": "移动支付网"
 },
 {
  "id": 289, "region": "华北", "province": "天津", "company": "渤海银行",
  "project": "数字人民币2.0数币核心及场景应用采购项目",
  "overview": "数字人民币2.0数币核心系统及场景应用采购，报名截止2026-10-09，项目编号BHGJ-2026-118A，投标截止2026-10-20。",
  "budget": "-", "deadline": "2026-10-20", "method": "公开招标", "contact": "-",
  "tags": ["公司金融"], "rec": "🔥 ★★★ 强烈建议投标",
  "url": "https://www.qianlima.com/bid-634633270.html", "source": "千里马招标网"
 },
 {
  "id": 290, "region": "华北", "province": "天津", "company": "渤海银行",
  "project": "数字人民币2.0智能合约系统采购项目",
  "overview": "数字人民币2.0智能合约系统采购，报名截止2026-10-09，项目编号BHGJ-2026-049A，投标截止2026-10-16。",
  "budget": "-", "deadline": "2026-10-16", "method": "竞争性谈判", "contact": "-",
  "tags": ["公司金融"], "rec": "🔥 ★★★ 强烈建议投标",
  "url": "https://www.qianlima.com/bid-634625431.html", "source": "千里马招标网"
 },
 {
  "id": 291, "region": "华东", "province": "福建", "company": "兴业银行信用卡中心",
  "project": "催收机器人项目（供应商征集调研）",
  "overview": "催收机器人项目供应商征集调研，寻源截止2026-10-08 23:59。",
  "budget": "-", "deadline": "2026-10-08", "method": "征集调研", "contact": "-",
  "tags": ["大模型应用"], "rec": "👀 ★☆☆ 可关注",
  "url": "https://www.mpaypass.com.cn/news/202609/27211921.html", "source": "移动支付网"
 }
]

html = open(INDEX, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
d = json.loads(m.group(2))
projects = d['projects']

# 校验
ids = {p['id'] for p in projects}
for it in NEW:
    assert it['id'] not in ids, f"id 冲突: {it['id']}"
    bad = [t for t in it['tags'] if t not in VALID_TAGS]
    assert not bad, f"非法标签 {bad}"
    assert it['method'] in VALID_METHODS or it['method'] == '征集调研', f"非法采购方式 {it['method']}"  # 板上已有2条"征集调研"（config 未收录的既有取值）

projects.extend(NEW)
projects.sort(key=sort_key)
d['projects'] = projects

html = html[:m.start(2)] + json.dumps(d, ensure_ascii=False, indent=2) + html[m.end(2):]
open(INDEX, 'w', encoding='utf-8').write(html)
print(f"写入 {len(NEW)} 条, 总数 {len(projects)}, 已按 sort_key 全量重排")
