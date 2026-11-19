#!/usr/bin/env python3
"""2026-10-23 周老师候选决策执行：晨报候选 3 纳入（id141），1/2/4 不纳入。
决策原文：「候选决策：3纳入 ；其他不纳入」（2026-10-23 17:35 指令）。
安全红线：Python 结构化读写，禁止文本替换；执行前已核 pending 台账 2026-10-23 批 4 条均为「待确认」。
id141 概况核实：千里马 bid-641093595 页面确认招标估价 500,000 元、竞争性磋商公告（PDF 附件）、发布 2026-10-22/23；联系人为会员隐藏内容，记 "-"，不臆造。
"""
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PENDING = WS / "pending_candidates.json"
REJECTED = WS / "rejected_candidates.json"

NEW_PROJECT = {
    "id": 141,
    "region": "华北",
    "province": "北京",
    "company": "北京银行",
    "project": "2026年私募股权数据采购项目",
    "overview": "北京银行2026年私募股权数据采购项目，竞争性磋商。千里马页面披露招标估价50万元；公告以PDF附件发布（发布日期2026-10-22/23），供应商报名及响应文件递交截止2026-11-03。联系人与代理机构信息为千里马会员隐藏内容，以原始公告PDF为准。",
    "budget": "50万元",
    "deadline": "2026-11-03",
    "method": "竞争性磋商",
    "contact": "-",
    "tags": ["数据服务"],
    "rec": "👀 ★☆☆ 可关注",
    "url": "https://www.qianlima.com/bid-641093595.html",
    "source": "千里马招标网",
    "date": "2026-10-23",
}

FINAL_MAP = {
    ("天津银行", "2026-2027年度智能运维合规管理系统软件维保（第三次）（招标公告）"): ("不纳入", None),
    ("中原银行", "国际结算业务系统重构测试服务项目（竞争性磋商）"): ("不纳入", None),
    ("北京银行", "2026年私募股权数据采购项目（竞争性磋商）"): ("纳入", 141),
    ("宁银理财", "财务预警系统维保及数据服务项目（供应商二次征集）"): ("不纳入", None),
}
DECISION = "2026-10-23 周老师候选决策（17:35）：3纳入；其他不纳入"

REJECT_ITEMS = [
    {"company": "天津银行", "project": "2026-2027年度智能运维合规管理系统软件维保（第三次）（招标公告）",
     "deadline": "2026-11-13", "tags": ["运维服务"], "suggestion": "可关注",
     "url": "https://www.qianlima.com/bid-640985052.html", "source": "千里马招标网",
     "date": "2026-10-23", "reject_reason": "周老师 2026-10-23 候选决策：不纳入"},
    {"company": "中原银行", "project": "国际结算业务系统重构测试服务项目（竞争性磋商）",
     "deadline": "2026-11-04", "tags": ["人力外包"], "suggestion": "可关注",
     "url": "https://www.qianlima.com/bid-641008616.html", "source": "千里马招标网",
     "date": "2026-10-23", "reject_reason": "周老师 2026-10-23 候选决策：不纳入"},
    {"company": "宁银理财", "project": "财务预警系统维保及数据服务项目（供应商二次征集）",
     "deadline": "2026-10-31", "tags": ["运维服务"], "suggestion": "可关注",
     "url": "https://www.kuaicha365.com/", "source": "快查API",
     "date": "2026-10-23", "reject_reason": "周老师 2026-10-23 候选决策：不纳入"},
]

STD_FIELDS = ["id", "company", "project", "overview", "budget", "deadline",
              "method", "contact", "region", "province", "tags", "rec", "url", "source"]


def main():
    # 0) 执行前防串台核验：本批 4 条必须全部「待确认」
    pend0 = json.loads(PENDING.read_text(encoding="utf-8"))
    batch = [x for x in pend0 if (x.get("company"), x.get("project")) in FINAL_MAP]
    assert len(batch) == 4, f"本批应 4 条，实取 {len(batch)}"
    bad = [x["project"] for x in batch if x.get("status") != "待确认"]
    assert not bad, f"❌ 防串台拦截：{bad} 已有状态，禁止二次执行"
    print("✅ 防串台核验通过：本批 4 条均为「待确认」")

    # 1) index.html 结构化上板 id141
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)',
                  html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    assert all(k in NEW_PROJECT for k in STD_FIELDS), "❌ id141 缺字段"
    if NEW_PROJECT["id"] in {p["id"] for p in projects}:
        raise SystemExit("❌ id141 已存在，禁止重复上板")
    projects.append(NEW_PROJECT)
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 上板 id141（北京银行 私募股权数据采购），共 {len(projects)} 项")

    # 2) pending_candidates.json 台账闭环
    done = set()
    for x in pend0:
        key = (x.get("company"), x.get("project"))
        if key in FINAL_MAP:
            st, bid = FINAL_MAP[key]
            x["status"] = st
            x["decision"] = DECISION
            if bid:
                x["board_id"] = bid
                x["rec"] = "👀 ★☆☆ 可关注"
            done.add(key)
    missing = set(FINAL_MAP) - done
    if missing:
        raise SystemExit(f"❌ 台账未闭环: {missing}")
    PENDING.write_text(json.dumps(pend0, ensure_ascii=False, indent=1), encoding="utf-8")
    print("✅ pending_candidates.json：3 纳入（id141）/ 1、2、4 不纳入，已闭环")

    # 3) rejected_candidates.json 记录 1/2/4
    rej = json.loads(REJECTED.read_text(encoding="utf-8"))
    if not isinstance(rej, list):
        raise SystemExit("❌ rejected_candidates.json 非数组")
    added = 0
    for item in REJECT_ITEMS:
        if not any(r.get("project") == item["project"] and r.get("date") == item["date"] for r in rej):
            rej.append(item)
            added += 1
    if added:
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ rejected_candidates.json：新增 {added} 条（1 天津银行 / 2 中原银行 / 4 宁银理财）")


if __name__ == "__main__":
    main()
