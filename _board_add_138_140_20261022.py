#!/usr/bin/env python3
"""2026-10-22 周老师候选决策执行：晨报候选 1-3 纳入（id138-140），4 不纳入。
决策原文：1-3纳入且投标建议均改为"可关注"，1业务标签增加"公司金融"，2业务标签增加"渠道系统"；4不纳入。
安全红线：Python 结构化读写，禁止文本替换；执行前已核 pending 台账 4 条均为「待确认」。
"""
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PENDING = WS / "pending_candidates.json"
REJECTED = WS / "rejected_candidates.json"

NEW_PROJECTS = [
    {
        "id": 138,
        "region": "华南",
        "province": "广东",
        "company": "光大银行广州分行",
        "project": "综合前置系统信创改造项目",
        "overview": "综合前置系统须在2026年底完成信创改造，部分业务涉及调用总行核心系统接口，需与总行新核心项目协同联动、同步实施，完成分行前置功能改造并升级系统性能，实现关键技术自主可控并满足信创监管合规要求，保障生活缴费及代扣代缴等业务平稳运行；2026年12月31日前整体上线。最高投标限价75.4万元（含税）。投标截止2026-11-11 10:00，报名/领购招标文件截止2026-11-10。",
        "budget": "75.4万元",
        "deadline": "2026-11-11",
        "method": "公开招标",
        "contact": "招标人 李小姐 020-****0247；代理机构 钟智泳/陈浩岚 020-****0115",
        "tags": ["信创", "公司金融"],
        "rec": "👀 ★☆☆ 可关注",
        "url": "https://www.qianlima.com/bid-640637559.html",
        "source": "千里马招标网",
        "date": "2026-10-22",
    },
    {
        "id": 139,
        "region": "华南",
        "province": "广西",
        "company": "广西北部湾银行",
        "project": "远程银行智能服务平台项目",
        "overview": "远程银行智能服务平台项目1项，竞争性磋商，预算不公布。响应文件递交截止2026-11-02 18:00，磋商时间另行通知。经阳光采购服务平台报名获取采购文件，不接受联合体、不接受转包分包。",
        "budget": "-",
        "deadline": "2026-11-02",
        "method": "竞争性磋商",
        "contact": "项目联系人 龙经理 0771-****275；采购联系人 林经理/黄经理 0771-****363/189****9519",
        "tags": ["大模型应用", "渠道系统"],
        "rec": "👀 ★☆☆ 可关注",
        "url": "https://www.qianlima.com/bid-640633173.html",
        "source": "千里马招标网",
        "date": "2026-10-22",
    },
    {
        "id": 140,
        "region": "华中",
        "province": "河南",
        "company": "招商银行郑州分行",
        "project": "房地产市场数据服务采购项目",
        "overview": "房地产市场数据服务采购（供应商征集），采购发起部门为零售信贷部，项目为外部数据服务；公告未披露预算，报名截止2026-10-27。",
        "budget": "-",
        "deadline": "2026-10-27",
        "method": "供应商征集",
        "contact": "-",
        "tags": ["数据服务"],
        "rec": "👀 ★☆☆ 可关注",
        "url": "https://www.qianlima.com/bid-640542439.html",
        "source": "千里马招标网",
        "date": "2026-10-22",
    },
]

STD_FIELDS = ["id", "company", "project", "overview", "budget", "deadline",
              "method", "contact", "region", "province", "tags", "rec", "url", "source"]


def main():
    # 1) index.html 结构化更新
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)',
                  html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    existing_ids = {p["id"] for p in projects}
    for np_ in NEW_PROJECTS:
        assert all(k in np_ for k in STD_FIELDS), f"缺字段: {np_['id']}"
        if np_["id"] in existing_ids:
            print(f"⚠️ id{np_['id']} 已存在，跳过")
            continue
        projects.append(np_)
        print(f"✅ 上板 id{np_['id']}: {np_['company']} | {np_['project']}")
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 写回：共 {len(projects)} 项")

    # 2) pending_candidates.json 台账闭环（按公司+项目匹配，防错位）
    pend = json.loads(PENDING.read_text(encoding="utf-8"))
    final_map = {
        ("光大银行广州分行", "综合前置系统信创改造项目（公开招标）"): ("纳入", 138),
        ("广西北部湾银行", "远程银行智能服务平台项目（竞争性磋商）"): ("纳入", 139),
        ("招商银行郑州分行", "房地产市场数据服务采购项目（供应商征集）"): ("纳入", 140),
        ("中国银行湖南省分行", "数据管理类项目数据技术支持服务项目（邀请招标）"): ("不纳入", None),
    }
    done = set()
    for x in pend:
        key = (x.get("company"), x.get("project"))
        if key in final_map and str(x.get("status", "待确认")) in ("待确认", "None", ""):
            st, bid = final_map[key]
            x["status"] = st
            x["decision"] = "2026-10-22 周老师晨报决策"
            if bid:
                x["board_id"] = bid
            if st == "纳入":
                x["rec"] = "👀 ★☆☆ 可关注"
            done.add(key)
    missing = set(final_map) - done
    if missing:
        raise SystemExit(f"❌ 台账未闭环: {missing}")
    PENDING.write_text(json.dumps(pend, ensure_ascii=False, indent=1), encoding="utf-8")
    print("✅ pending_candidates.json：1-3 纳入（id138-140，rec=可关注），4 不纳入")

    # 3) rejected_candidates.json 记录第 4 项
    rej = json.loads(REJECTED.read_text(encoding="utf-8"))
    if not isinstance(rej, list):
        raise SystemExit("❌ rejected_candidates.json 非数组")
    item4 = {
        "company": "中国银行湖南省分行",
        "project": "数据管理类项目数据技术支持服务项目（邀请招标）",
        "deadline": "2026-11-03",
        "tags": ["数据服务"],
        "suggestion": "可关注",
        "url": "https://www.kuaicha365.com/",
        "source": "快查API",
        "date": "2026-10-22",
        "reject_reason": "周老师 2026-10-22 晨报候选决策：不纳入",
    }
    if not any(r.get("project") == item4["project"] and r.get("date") == item4["date"] for r in rej):
        rej.append(item4)
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding="utf-8")
        print("✅ rejected_candidates.json：已记录第 4 项（周老师决策不纳入）")
    else:
        print("⚠️ rejected_candidates.json 已有该条，跳过")


if __name__ == "__main__":
    main()
