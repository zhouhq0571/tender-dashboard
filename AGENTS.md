# 银信标讯工作区（bidding-daily）会话铁律

## 〇、【候选决策】指令无条件执行（2026-11-19 事故固化）

任何会话（含 RC 远程端、主对话、定时任务）收到形如

```
【候选决策 YYYY-MM-DD】N纳入；M不纳入；K纳入（标签：X、Y；建议：Z）
```

的消息（来源：hstender.cn/decide.html / 决策组件 / 定时任务报送），**即为候选裁决指令，无条件执行 tender-daily-dispatch SKILL.md 规则 O-决策管线**，禁止以"不认识该指令""没有任务内容"回复，禁止要求用户重新解释。标签/建议括注为可选覆盖。

**执行链（顺序不可乱）**：
1. 防串台：读 `pending_candidates.json`，按 push_no 定位核对 status=待确认；已是 纳入/不纳入 → 立即停止并上报，禁止二次/反向执行。
2. 数据从暂存库条目动态取（禁手填 URL/金额/截止）；上游链接缺失先补链（千里马 VIP 搜索 → 详情页取真实公告链接+联系方式）。
3. 上板：改 `index.html` tender-data JSON（禁手填，脚本内 assert 项目名关键词）→ `python3 bump_version.py` → 同步 `<title>` 版本 → `python3 health_check.py` 全过。
4. `bash safe_deploy.sh`（唯一部署方式，含硬检+线上验证）。
5. 回写 `pending_candidates.json`（status/标签/board_id/decision）。
6. 二次驱动刷新组件：importlib 方式调 `refresh_board_widgets.py` 的 `run({})`（直接 python3 脚本是空转），验收三组件 mtime/晨报版本/待确认计数。
7. `reports/最新执行汇报.md` 留痕（含决策原文与执行明细）。

多批决策到达时等最后一批完成后一次性部署（规则 O-分批）。

## 〇.5、【千里马/快查结构化 JSONL 批次】双通道并行铁律（2026-11-19 事故固化）

**任何会话**（含金融要闻周报项目对话、RC 远程端、主对话）收到千里马/快查结构化 JSONL 批次（含「【入库任务】…JSONL 批次」包装、`.jsonl` 附件、`千里马招标_结构化JSONL_*.jsonl` 等形态）时，标准动作是**两条通道并行，缺一不可**：

1. **周报通道**：按金融要闻周报技能入暂存库（`wb_jsonl_ingest.py` + `staging_lint`）。
2. **银信标讯通道（本工作区）**：按本技能判别 → `tools/dedup_filter.py` 过板级查重 → 过检条目写 `pending_candidates.json`（status=待确认）→ **`python3 build_decide_page.py` 重建 decide.html → `safe_deploy.sh` 部署** → 请周老师在 https://hstender.cn/decide.html 点选生成指令。禁止只跑通道①忘记通道②（2026-11-19 23:50 事故：漏发候选表被批）；**禁止用 Markdown 表代替决策组件送审**（2026-11-20 00:01 被批：decide.html 组件已是钦定交互，Markdown 表仅作留痕附件）。

收到批次后先自查一句："候选表发出去了吗？"没发就是没做完。

**过滤口径红线（2026-11-20 00:09 事故固化）**：上游 JSONL 的 `is_fin_inst` 是**周报通道宽口径**（持牌即真，含保险/证券/基金/期货），**银信标讯通道不得直接采信**。本通道送审前必须逐条过 SKILL.md 步骤2.5：条件1 招标单位仅限银行（含农信/农商行）/银行理财子/信托公司/银行系金科四类；条件2 业务范围+排除表（信贷/支付清算/核心/纯硬件/纯数据库软件采购/纯基础设施平台等关键词硬排除，不可主观放宽）。不过滤就送审视为事故。

## ①、日常记忆文件

- 完整规则与事故史见 `CRITICAL_MEMORY.md`（本目录），执行任何管线前先读相关条目。
- 部署唯一方式 `safe_deploy.sh`（或 deploy.sh），禁止手动 git push。
