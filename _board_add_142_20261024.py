#!/usr/bin/env python3
"""2026-10-24 周老师候选决策执行：候选 1 纳入（id142）。
决策原文：「1纳入」（2026-10-24 14:24）。
安全红线：Python 结构化读写；执行前已核 pending 该条为「待确认」，在板/已否决无重复。
"""
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PENDING = WS / "pending_candidates.json"

NEW_PROJECT = {
    "id": 142,
    "region": "华东",
    "province": "福建",
    "company": "兴业银行",
    "project": "2026年智能体平台一期软件产品及研发实施采购项目",
    "overview": "构建具有高级认知和作业处理能力的金融智能体平台，实现智能体Agent应用低成本开发和管理、主流大模型支持、插件集成调用、知识库构建、流程自主规划、思维链和可视化编排等功能；平台内置智能数据分析、智能问数、图表生成、报告生成等基础组件，集成企业级知识问答能力。本次软件产品为许可买断，含研发实施服务，中标候选人1名。资格要求：2023年1月1日至今投标人与国内21家系统重要性银行开展的总行级智能体同类型成功案例（合同须体现智能体平台/AI应用创新平台等字样）；不接受联合体。招标文件在福易采电子交易平台发售（10-21至10-26，售价300元），电子标（etnd格式）+密封纸质标并行递交。招标编号FJTP-FJTC261313260。",
    "budget": "未披露",
    "deadline": "2026-11-13",
    "method": "公开招标",
    "contact": "招标人 段先生 0591-86313348；代理机构（福建省招标中心）宋斌妹/谢启橧/高宇 0591-87513248",
    "tags": ["大模型应用"],
    "rec": "⭐ ★★☆ 建议投标",
    "url": "https://mp.weixin.qq.com/s/NYtOpxLsmFh6DWt13NPSIw",
    "source": "智探AI应用（公众号）",
    "date": "2026-10-24",
}

KEY = ("兴业银行", "2026年智能体平台一期软件产品及研发实施采购项目（公开招标）")
DECISION = "2026-10-24 周老师候选决策（14:24）：1纳入"
STD_FIELDS = ["id", "company", "project", "overview", "budget", "deadline",
              "method", "contact", "region", "province", "tags", "rec", "url", "source"]


def main():
    # 0) 防串台核验
    pend0 = json.loads(PENDING.read_text(encoding="utf-8"))
    hit = [x for x in pend0 if (x.get("company"), x.get("project")) == KEY]
    assert len(hit) == 1, f"应恰 1 条，实取 {len(hit)}"
    assert hit[0].get("status") == "待确认", f"❌ 防串台拦截：status={hit[0].get('status')}"
    print("✅ 防串台核验通过：该条为「待确认」")

    # 1) index.html 上板 id142
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)',
                  html, re.DOTALL)
    if not m:
        raise SystemExit("❌ 找不到 tender-data JSON")
    data = json.loads(m.group(2))
    projects = data["projects"]
    assert all(k in NEW_PROJECT for k in STD_FIELDS), "❌ id142 缺字段"
    if NEW_PROJECT["id"] in {p["id"] for p in projects}:
        raise SystemExit("❌ id142 已存在，禁止重复上板")
    projects.append(NEW_PROJECT)
    data["total"] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")
    print(f"✅ index.html 上板 id142（兴业银行 智能体平台一期），共 {len(projects)} 项")

    # 2) pending 闭环
    hit[0]["status"] = "纳入"
    hit[0]["decision"] = DECISION
    hit[0]["board_id"] = 142
    hit[0]["rec"] = "⭐ ★★☆ 建议投标"
    hit[0]["project"] = KEY[1]
    PENDING.write_text(json.dumps(pend0, ensure_ascii=False, indent=1), encoding="utf-8")
    print("✅ pending_candidates.json：已闭环（纳入，id142）")


if __name__ == "__main__":
    main()
