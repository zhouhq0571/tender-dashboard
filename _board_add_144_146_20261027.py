#!/usr/bin/env python3
"""2026-10-27 周老师候选决策执行：晨报候选 1、6、9 纳入（id144-146），其余 8 条不纳入。
决策原文：「候选决策：1、6、9纳入，1业务标签增加"资产管理"、投标建议改为"强烈建议投标"；其他不纳入」（2026-10-27 12:15 指令）。
防串台核验：本批（date=2026-10-27，11 条，idx44-54）status 均为缺省或「待确认」，无决策注记，无会话执行过。
编号口径：按台账本批顺序 1-11。
"""
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PENDING = WS / "pending_candidates.json"
REJECTED = WS / "rejected_candidates.json"

BATCH_DATE = "2026-10-27"
DECISION = "2026-10-27 周老师晨报候选决策（12:15）：1、6、9纳入，1标签+资产管理、建议改强烈建议投标；其他不纳入"

# (编号, 公司, 项目, board_id, 补充信息)
ACCEPTS = [
    (1, "建信信托", "2026至2027恒生电子系统维护服务采购项目（供应商征集）", 144,
     {"region": "华北", "province": "北京",
      "overview": "建信信托2026至2027年度恒生电子系统维护服务采购，供应商征集；龙集采直连采集，投标截止2026-11-02。",
      "budget": "-", "method": "供应商征集",
      "tags": ["运维服务", "资产管理"], "rec": "🔥 ★★★ 强烈建议投标",
      "source": "建设银行集采平台"}),
    (6, "光大银行", "家族财富业务管理系统开发服务选型入围项目（二次招标）", 145,
     {"region": "华北", "province": "北京",
      "overview": "光大银行家族财富业务管理系统开发服务选型入围项目（二次招标）；快查渠道提取截止日2026-11-16，建议以招标文件复核。",
      "budget": "-", "method": "公开招标",
      "tags": ["财富管理"], "rec": "⭐ ★★☆ 建议投标",
      "source": "快查"}),
    (9, "北京银行", "2026年国际业务处理系统SWIFT报文标准优化项目", 146,
     {"region": "华北", "province": "北京",
      "overview": "北京银行2026年国际业务处理系统SWIFT报文标准优化项目；快查渠道提取截止日2026-11-02，建议以招标文件复核。",
      "budget": "-", "method": "竞争性磋商",
      "tags": ["公司金融"], "rec": "⭐ ★★☆ 建议投标",
      "source": "快查"}),
]

STD_FIELDS = ["id", "company", "project", "overview", "budget", "deadline",
              "method", "contact", "region", "province", "tags", "rec", "url", "source"]


def main():
    pend0 = json.loads(PENDING.read_text(encoding="utf-8"))
    batch = [x for x in pend0 if x.get("date") == BATCH_DATE]
    assert len(batch) == 11, f"本批应 11 条，实取 {len(batch)}"
    bad = [x["project"] for x in batch if x.get("status") in ("纳入", "不纳入")]
    assert not bad, f"❌ 防串台拦截：{bad} 已有会话执行"

    # 按台账顺序编号 1-11
    new_projects = []
    for num, comp, proj, bid, extra in ACCEPTS:
        x = batch[num - 1]
        assert x.get("company") == comp and x.get("project") == proj, \
            f"❌ 第{num}条定位失败：实为 {x.get('company')}|{x.get('project')}"
        url = x.get("source_url") or x.get("url") or ""
        np_ = {
            "id": bid, "company": comp, "project": proj.split("（")[0],
            "overview": extra["overview"], "budget": extra["budget"],
            "deadline": x["deadline"], "method": extra["method"], "contact": "-",
            "region": extra["region"], "province": extra["province"],
            "tags": extra["tags"], "rec": extra["rec"], "url": url,
            "source": extra["source"], "date": BATCH_DATE,
        }
        assert all(k in np_ for k in STD_FIELDS)
        new_projects.append((num, bid, np_))
    print("✅ 防串台核验通过：本批 11 条均未决策；1/6/9 定位成功")

    # 1) index.html 上板
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)',
                  html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    existing = {p["id"] for p in projects}
    for num, bid, np_ in new_projects:
        assert bid not in existing, f"❌ id{bid} 已存在"
        projects.append(np_)
        print(f"✅ 上板 id{bid}: {np_['company']} | {np_['project']}")
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 写回：共 {len(projects)} 项")

    # 2) pending 台账闭环（11 条全部回写）
    acc_keys = {(a[1], a[2]) for a in ACCEPTS}
    n_acc = n_rej = 0
    bid_map = {a[2]: a[3] for a in ACCEPTS}
    for x in pend0:
        if x.get("date") != BATCH_DATE:
            continue
        key = (x.get("company"), x.get("project"))
        if key in acc_keys:
            x["status"] = "纳入"
            x["decision"] = DECISION
            x["board_id"] = bid_map[key[1]]
            if key[1].startswith("2026至2027恒生电子"):
                x["tags"] = "运维服务、资产管理"
                x["rec"] = "强烈建议投标"
            n_acc += 1
        else:
            x["status"] = "不纳入"
            x["decision"] = DECISION
            n_rej += 1
    assert n_acc == 3 and n_rej == 8, f"❌ 回写计数异常 纳入{n_acc}/不纳入{n_rej}"
    PENDING.write_text(json.dumps(pend0, ensure_ascii=False, indent=1), encoding="utf-8")
    print("✅ pending_candidates.json：1/6/9 纳入（id144-146，含第 1 条标签与建议修改）/ 其余 8 条不纳入")

    # 3) rejected_candidates.json 记录 8 条
    rej = json.loads(REJECTED.read_text(encoding="utf-8"))
    if not isinstance(rej, list):
        raise SystemExit("❌ rejected_candidates.json 非数组")
    added = 0
    for x in pend0:
        if x.get("date") != BATCH_DATE or (x.get("company"), x.get("project")) in acc_keys:
            continue
        item = {
            "company": x.get("company"), "project": x.get("project"),
            "deadline": x.get("deadline"),
            "tags": x.get("tags") if isinstance(x.get("tags"), list) else [x.get("tags")],
            "suggestion": x.get("suggestion") or (x.get("rec") or "").split()[-1],
            "url": x.get("source_url") or x.get("url") or "",
            "source": "晨报候选" + BATCH_DATE, "date": BATCH_DATE,
            "reject_reason": "周老师 2026-10-27 晨报候选决策：不纳入（1、6、9纳入；其他不纳入）",
        }
        if not any(r.get("project") == item["project"] and r.get("date") == item["date"] for r in rej):
            rej.append(item)
            added += 1
    if added:
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ rejected_candidates.json：新增 {added} 条不纳入记录")


if __name__ == "__main__":
    main()
