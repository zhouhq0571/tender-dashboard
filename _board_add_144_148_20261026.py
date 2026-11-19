#!/usr/bin/env python3
"""2026-10-26 千里马Excel候选批次1（seek_1026_b1）裁决执行：1/3/6/7/10纳入（id144-148），
2/4/5/8/9不纳入。周老师裁决（20:39）：「1、3、6、7、10纳入，3业务标签增加“公司金融”，
6删除业务标签“资产管理”，3、6投标建议改为“可关注”；其他不纳入」。
防串台：先验看板无同 company+project 条目。
"""
import json, re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
REJECTED = WS / "rejected_candidates.json"
DECISION = "2026-10-26 20:39 周老师seek_1026_b1裁决：1/3/6/7/10纳入；3加标签公司金融+改可关注；6删标签资产管理+改可关注；2/4/5/8/9不纳入"

NEW = [
 {"id":144,"region":"华北","province":"北京","company":"北京银行",
  "project":"私行代销业务掌上银行家系统功能优化项目（第二次）",
  "overview":"北京银行私行代销业务掌上银行家系统功能优化项目（第二次），竞争性磋商，预算9万元；千里马 bid-641289946。",
  "budget":"9万元","deadline":"2026-11-03","method":"竞争性磋商","contact":"-",
  "tags":["财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641289946.html","source":"千里马招标网","date":"2026-10-26"},
 {"id":145,"region":"华东","province":"江苏","company":"江苏银行",
  "project":"物业资金监管智能体建设项目",
  "overview":"江苏银行物业资金监管智能体建设项目，公开招标，预算130万元；千里马 bid-641070351。",
  "budget":"130万元","deadline":"2026-11-05","method":"公开招标","contact":"-",
  "tags":["大模型应用","金市/资金/同业","公司金融"],"rec":"⭐ ★★☆ 可关注",
  "url":"https://www.qianlima.com/bid-641070351.html","source":"千里马招标网","date":"2026-10-26"},
 {"id":146,"region":"华东","province":"浙江","company":"宁波银行",
  "project":"智投行系统募集撰写项目",
  "overview":"宁波银行智投行系统募集撰写项目，公开招标；千里马 bid-641387160。",
  "budget":"-","deadline":"2026-11-02","method":"公开招标","contact":"-",
  "tags":["其他"],"rec":"⭐ ★★☆ 可关注",
  "url":"https://www.qianlima.com/bid-641387160.html","source":"千里马招标网","date":"2026-10-26"},
 {"id":147,"region":"华北","province":"河北","company":"秦皇岛银行",
  "project":"资金业务核算改造项目",
  "overview":"秦皇岛银行资金业务核算改造项目，单一来源采购，预算19.71万元；千里马 bid-641391968。",
  "budget":"19.71万元","deadline":"2026-11-06","method":"单一来源采购","contact":"-",
  "tags":["资产管理","金市/资金/同业"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641391968.html","source":"千里马招标网","date":"2026-10-26"},
 {"id":148,"region":"华中","province":"河南","company":"中原银行",
  "project":"国际结算业务系统重构测试服务项目",
  "overview":"中原银行国际结算业务系统重构测试服务项目，竞争性磋商；千里马 bid-641008616。",
  "budget":"-","deadline":"2026-11-04","method":"竞争性磋商","contact":"-",
  "tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641008616.html","source":"千里马招标网","date":"2026-10-26"},
]

REJ = [
 ("南京银行","南京银行股份有限公司集中作业平台优化升级项目","2026-11-13","其他","https://www.qianlima.com/bid-641467574.html"),
 ("江苏银行","江苏银行股份有限公司2026年腾讯反欺诈数据采购项目","2026-10-30","风控合规","https://www.qianlima.com/bid-641472994.html"),
 ("中国银行大连分行","中国银行股份有限公司大连分行银行卡综合信息管理系统维护项目","2026-11-03","运维服务","https://www.qianlima.com/bid-641192375.html"),
 ("辽宁农商银行","辽宁农村商业银行股份有限公司反诈模型建设二期采购项目","2026-11-13","风控合规","https://www.qianlima.com/bid-641392507.html"),
 ("中原银行","中原银行股份有限公司2026年网络安全等级保护测评项目","2026-11-06","风控合规","https://www.qianlima.com/bid-640898989.html"),
]

def main():
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    existing = {(p.get("company"), p.get("project")) for p in projects}
    # 防串台：同 company+project（或project包含关系）禁止重复上板
    for it in NEW:
        for (c, p) in existing:
            if it["project"] in (p or "") or (p or "") in it["project"]:
                raise SystemExit(f"❌ 防串台拦截：看板已存在 {c}/{p}")
        if it["id"] in {p["id"] for p in projects}:
            raise SystemExit(f"❌ id{it['id']} 已存在")
    projects.extend(NEW)
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 上板 id144-148 共5条（总 {len(projects)} 项）")

    rej = json.loads(REJECTED.read_text(encoding="utf-8"))
    added = 0
    for comp, proj, dl, tag, url in REJ:
        item = {"company": comp, "project": proj, "deadline": dl, "tags": [tag],
                "suggestion": "建议投标", "url": url,
                "source": "千里马Excel候选seek_1026_b1", "date": "2026-10-26",
                "reject_reason": DECISION}
        if not any(r.get("project") == proj and r.get("date") == "2026-10-26" for r in rej):
            rej.append(item); added += 1
    if added:
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ rejected_candidates.json 新增 {added} 条不纳入记录")

if __name__ == "__main__":
    main()
