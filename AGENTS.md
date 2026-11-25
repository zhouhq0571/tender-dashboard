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
6. 二次驱动刷新决策组件：`python3 build_decide_page.py` 重建 decide.html（待确认清零）→ 随 safe_deploy 部署 → curl 比对线上 hash 与本地一致（2026-11-20 修订：原引用的 `refresh_board_widgets.py` 已不存在，以 decide.html 重建为组件刷新标准动作）。
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

## ②、事故年鉴（2026-11-19~20 复盘沉淀，周老师"低级问题超出预期"批评后建）

| # | 事故 | 根因 | 固化位置 |
|---|---|---|---|
| 1 | 11-19 23:50 千里马 JSONL 批次漏跑银信标讯送审通道 | 技能层从未定义"收到结构化 JSONL 批次"的双通道触发链 | 本文件 〇.5 节 + SKILL.md 触发条件 |
| 2 | 11-20 00:01 用 Markdown 表代送审 | 前晚修复写入"生成候选表发送"被机械执行，忘了 decide.html 组件已是钦定交互 | 本文件 〇.5 节（禁 Markdown 代送审） |
| 3 | 11-20 00:09 保险/证券/基金/期货条目混入送审 | 直接信上游 is_fin_inst（周报宽口径），未逐步骤2.5；机构范围规则只写在文档无代码消费 | `config.company_board_scope` + validate/safe_deploy/sweep/wb_board_candidates 四线挂载 |
| 4 | 11-20 00:09 纯数据库采购/DNS设备/存储硬件/云平台授权混入送审 | 同上：业务排除表未代码化消费 | 同上（业务排除词表后续 likewise 代码化，见 SKILL 步骤2.5） |
| 5 | 11-20 00:31 网页版 decide 与侧栏组件交互不一致 | 两份 UI 各自演进，无同源契约 | decide.html 已重写为组件同款表格（build_decide_page.py 与 refresh_board_widgets.py 决策表列序一致：编号/单位·项目/预算/截止/标签/建议/决策） |
| 6 | 11-20 00:31 免密 30 分钟从未生效 | dek 存 base64、恢复按 hex 解析，必然失败 | build_decide_page.py GATE_JS hexE 修复 + Playwright 回归 |
| 7 | 11-20 序号 16 起引困惑 | push_no 全局递增无说明 | decide 页 tip 已注明"编号为台账全局递增编号" |
| 8 | 11-23 12:45 decide/晨报显示 74 项·待决策 10，与板上 81·0 双失真 | 决策管线上板后从不回写 latest_meta.json，单一 stale 真源污染全部 meta 消费方 | `tools/sync_loop_meta.py`（version/total/candidates/added 从 index.html+台账派生）挂载 build_decide_page.py 构建前 + safe_deploy.sh 步骤3.5（凡部署必自愈）；台账新增 decision_date 字段 |
| 9 | 11-23 14:54 侧栏「标讯晨报·决策一体」Widget 仍显示凌晨快照（v439/74/10 候选） | Widget 数据为 05:47 主任务烘焙的静态内嵌，对话决策管线无刷新触发器；修 meta 不触发 Widget 文件重烘焙（与 #8 同型上下层） | `tools/refresh_morning_widget.py`（4 处动态点重烘焙，锚点断言）挂载 build_decide_page.py main()——decide.html 每次重建必联动刷新 Widget，同源同刻 |
| 10 | 11-25 12:49 看板白屏"清零"近 7 小时（v448-v451 连续四版损坏）+ 决策任务假"执行中"206 分钟 | ①凌晨主任务全量重写 HTML 产出 JS 语法损坏文件（try 缺 catch），safe_deploy 文件级检查（hash/字段/正则）发现不了语法错，连过四道部署；②Widget 进度面板只靠 onStatusChange 收口，状态机漏态即永久"执行中"（结果其实已回显） | safe_deploy.sh 新增步骤3.6 **渲染硬闸**（Playwright 实测：无 pageerror+统计=项目数+表格行=项目数，不过即中止部署；v449 反向测试实证拦截）；Widget onDataChange 收结果即强制 stopProgress(true) 兜底 |

**处分（2026-11-25 13:02 周老师裁定）：记大过一次**——特级故障（白屏7小时），记入本工作区处分台账，与事故 #10 同档。

**事故 #10 根因终审（2026-11-25 13:30 彻查结论）**：非"全量重写 HTML"，而是凌晨主任务日期刷新脚本把正则的**日期锚点丢了**——19/20 日用的是 `re.sub(r'数据更新时间：2026年11月20日 [^<]*', ...)`（带具体日期锚点，只碰静态文本），25 日错写成 `re.sub(r'数据更新时间：[^<]*', ...)`（无锚），该正则吞掉 JS 动态模板行 ``coverEl.textContent = `数据更新时间：${timeStr}` `` 的 `${timeStr}` 及后续代码直到下一个 `<`，把静态日期文本缝进 live JS → 主脚本 SyntaxError（Missing catch or finally after try）→ 整段 JS 不执行 → 白屏。safe_deploy 当时只 curl 查版本号/日期字符串/JSON，不验 JS 语法与渲染 → 坏版照常"验证通过"上线。固化：SKILL.md 新增"无锚正则替换禁令"（必须锚定具体旧日期值或精确字符串 replace，写回后 node --check 自检）。

**教训通则（全工作区生效）**：
- **规则必须代码化**：凡"每次都要判"的口径，只写文档=没写。新增口径同日建消费函数（config.py）并挂 validate/safe_deploy 兜底双保险（本工作区已有先例：简称映射 11-19 失守→normalize_company 代码化）。
- **单文件看板内嵌资源体积闸（2026-11-20 周老师钦定，防"厂商看板签章 1.25MB 内嵌致手机白屏 1 分钟"同类事故）**：单块 base64 >100KB 或单文件总量 >300KB = 违规，必须静态文件外链（展示尺寸小的图禁整图 dataURI 内嵌）。已代码化两处：`health_check.py` check_embedded_bloat（WARN 体检项）+ `safe_deploy.sh` 部署硬检（拒绝部署）；反向测试实证拦截有效。
- **门禁/看板页改动必须 Playwright 无头浏览器真实验证**（登录→免密→点选→生成指令四步全过）后才准汇报，curl/hash 只是部署层证据，不等于用户可见终态（11-16 厂商看板白屏事故同教训，CRITICAL_MEMORY 有档）。
- **上游字段语义不可跨通道混用**：is_fin_inst 是周报宽口径；本看板一切送审/上板以 company_board_scope 为唯一代码真源。
