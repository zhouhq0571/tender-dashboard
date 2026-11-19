#!/usr/bin/env python3
"""2026-10-26 周老师候选决策执行：晨报候选 4 纳入（id143），其余 7 条不纳入。
决策原文：「候选决策：4纳入 ；其他不纳入」（2026-10-26 08:29 指令）。
防串台核验：本批（date=2026-10-26，8 条）status 字段均缺省（None），无任何决策注记，
无会话执行过，准予执行。
编号口径：按台账本批顺序 1-8，第 4 条 = 北京银行支付清算运营支撑（二次）。
"""
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PENDING = WS / "pending_candidates.json"
REJECTED = WS / "rejected_candidates.json"

BATCH_DATE = "2026-10-26"
DECISION = "2026-10-26 周老师晨报候选决策（08:29）：4纳入；其他不纳入"

NEW_PROJECT = {
    "id": 143,
    "region": "华北",
    "province": "北京",
    "company": "北京银行",
    "project": "2026年支付清算系统功能优化项目运营支撑（二次）",
    "overview": "北京银行2026年支付清算系统功能优化项目运营支撑（二次采购），竞争性磋商，预算73.2万元；千里马 bid-641468168。板上首轮条目 id12（截止2026-10-27）为同一项目前次采购，本条为二次独立采购，两者并行保留。",
    "budget": "73.2万元",
    "deadline": "2026-11-03",
    "method": "竞争性磋商",
    "contact": "-",
    "tags": ["公司金融"],
    "rec": "⭐ ★★☆ 建议投标",
    "url": "https://www.qianlima.com/bid-641468168.html",
    "source": "千里马招标网",
    "date": "2026-10-26",
}

# 第 4 条判定键（纳入），其余 7 条不纳入
ACCEPT_KEY = ("北京银行", "2026年支付清算系统功能优化项目运营支撑（二次）")
STD_FIELDS = ["id", "company", "project", "overview", "budget", "deadline",
              "method", "contact", "region", "province", "tags", "rec", "url", "source"]


def main():
    # 0) 防串台核验：本批 8 条必须全部 status 缺省
    pend0 = json.loads(PENDING.read_text(encoding="utf-8"))
    batch = [x for x in pend0 if x.get("date") == BATCH_DATE]
    assert len(batch) == 8, f"本批应 8 条，实取 {len(batch)}"
    bad = [x["project"] for x in batch if x.get("status") in ("纳入", "不纳入")]
    assert not bad, f"❌ 防串台拦截：{bad} 已有会话执行"
    keys = [(x.get("company"), x.get("project")) for x in batch]
    assert ACCEPT_KEY in keys, f"❌ 第 4 条定位失败：{keys}"
    print("✅ 防串台核验通过：本批 8 条均未决策，第 4 条定位成功")

    # 1) index.html 上板 id143
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)',
                  html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    assert all(k in NEW_PROJECT for k in STD_FIELDS), "❌ id143 缺字段"
    if NEW_PROJECT["id"] in {p["id"] for p in projects}:
        raise SystemExit("❌ id143 已存在，禁止重复上板")
    projects.append(NEW_PROJECT)
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 上板 id143（北京银行 支付清算运营支撑二次），共 {len(projects)} 项")

    # 2) pending 台账闭环（8 条全部回写）
    n_acc, n_rej = 0, 0
    for x in pend0:
        if x.get("date") != BATCH_DATE:
            continue
        key = (x.get("company"), x.get("project"))
        if key == ACCEPT_KEY:
            x["status"] = "纳入"
            x["decision"] = DECISION
            x["board_id"] = 143
            x["rec"] = "⭐ ★★☆ 建议投标"
            n_acc += 1
        else:
            x["status"] = "不纳入"
            x["decision"] = DECISION
            n_rej += 1
    assert n_acc == 1 and n_rej == 7, f"❌ 回写计数异常 纳入{n_acc}/不纳入{n_rej}"
    PENDING.write_text(json.dumps(pend0, ensure_ascii=False, indent=1), encoding="utf-8")
    print("✅ pending_candidates.json：4 纳入（id143）/ 其余 7 条不纳入，全部回写")

    # 3) rejected_candidates.json 记录 7 条
    rej = json.loads(REJECTED.read_text(encoding="utf-8"))
    if not isinstance(rej, list):
        raise SystemExit("❌ rejected_candidates.json 非数组")
    added = 0
    for x in pend0:
        if x.get("date") != BATCH_DATE or (x.get("company"), x.get("project")) == ACCEPT_KEY:
            continue
        item = {
            "company": x.get("company"),
            "project": x.get("project"),
            "deadline": x.get("deadline"),
            "tags": x.get("tags") if isinstance(x.get("tags"), list) else [x.get("tags")],
            "suggestion": x.get("suggestion") or (x.get("rec") or "").split()[-1],
            "url": x.get("source_url") or x.get("url") or "",
            "source": "晨报候选" + BATCH_DATE,
            "date": BATCH_DATE,
            "reject_reason": "周老师 2026-10-26 晨报候选决策：不纳入（4纳入；其他不纳入）",
        }
        if not any(r.get("project") == item["project"] and r.get("date") == item["date"] for r in rej):
            rej.append(item)
            added += 1
    if added:
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ rejected_candidates.json：新增 {added} 条不纳入记录")


if __name__ == "__main__":
    main()
