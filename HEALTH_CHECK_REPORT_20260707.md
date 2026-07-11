# 恒生银信招标看板系统 — 全面健康自检报告

**检查时间**：2026-07-07 13:00 CST  
**系统版本**：v77  
**项目数量**：56 个（实际 JSON 数据）  
**部署目标**：zhouhq0571/tender-dashboard，gh-pages 分支  
**自定义域名**：hstender.cn  
**检查执行人**：系统健康检查专家（自动化巡检）

---

## 一、执行摘要

| 指标 | 结果 |
|------|------|
| 严重问题 (CRITICAL) | **2 项** |
| 警告问题 (WARNING) | **5 项** |
| 信息提示 (INFO) | **10 项** |
| 线上部署状态 | ✅ 正常（v77 已同步） |
| 数据完整性 | ⚠️ 存在缺陷（5 个项目缺少 id） |
| 自动化脚本健康度 | ❌ health_check.py 崩溃，无法正常运行 |

**总体评估**：系统线上服务正常，但底层数据存在结构性缺陷，自动化检查脚本失效，需要立即修复。

---

## 二、CRITICAL 级别问题（需立即修复）

### 🔴 CRITICAL-01：5 个项目缺少 `id` 字段

**问题描述**：
index.html 的 JSON 数据中，有 5 个项目条目缺少 `id` 字段，导致：
1. `health_check.py` 脚本在执行 `check_duplicates()` 和 `check_id_continuity()` 时因 `KeyError: 'id'` 崩溃
2. 项目 ID 连续性检查失败（实际 ID 范围 1-51，期望 1-56）
3. 前端渲染时这些项目可能无法正常绑定交互事件

**受影响项目**：

| 索引 | 招标单位 | 项目名称 |
|------|---------|---------|
| idx=12 | 哈尔滨银行 | 线上用户行为信息系统项目 |
| idx=32 | 苏州农商 | 2026年度数据类通用技术外包服务项目（应用开发） |
| idx=33 | 苏州农商 | 2026年度数据类通用技术外包服务项目（数据分析） |
| idx=40 | 湖南银行 | 2026年数字人民币系统研发项目 |
| idx=51 | 遂宁银行 | 数字化转型与信息科技战略规划咨询项目（标包2） |

**根因分析**：
这 5 个项目是 2026-07-07 定时任务（v76→v77）新增的 6 个项目中的 5 个（根据 LAST_RUN_STATUS.md 记录）。新增项目时，数据合并逻辑未正确分配连续 ID，而是直接将外部数据插入项目列表，遗漏了 `id` 字段。

**修复建议**：
1. 立即为这 5 个项目分配连续 ID（当前最大 ID 为 51，应分配 52-56）
2. 修改数据合并/插入逻辑，确保所有新增项目自动分配 `id`
3. 在数据入口处添加校验：任何缺少 `id` 的项目拒绝写入 index.html

**修复命令示例**：
```python
# 找出当前最大 ID，为缺少 id 的项目分配连续编号
max_id = max(int(p['id']) for p in projects if 'id' in p)
for p in projects:
    if 'id' not in p:
        max_id += 1
        p['id'] = str(max_id)
```

---

### 🔴 CRITICAL-02：health_check.py 脚本因 KeyError 崩溃

**问题描述**：
`health_check.py` 第 85 行 `seen[key] = p['id']` 在碰到缺少 `id` 字段的项目时抛出 `KeyError`，导致整个健康检查流程中断，无法输出任何有效结果。

**错误堆栈**：
```
File "health_check.py", line 85, in check_duplicates
    seen[key] = p['id']
KeyError: 'id'
```

**修复建议**：
1. 在 `check_duplicates()` 中使用 `p.get('id', '?')` 代替 `p['id']`
2. 在 `check_id_continuity()` 中过滤掉缺少 `id` 的项目或给予明确提示
3. 在 `check_required_fields()` 中将 `id` 缺失列为 FAIL 项
4. 建议在所有字段访问处统一使用 `.get()` 方法，增强脚本鲁棒性

---

## 三、WARNING 级别问题（建议尽快处理）

### ⚠️ WARNING-01：Git 提交信息中的项目数计数严重失真

**问题描述**：
deploy.sh 使用以下命令统计项目数量：
```bash
PROJECT_COUNT=$(grep -o '"company"' index.html | wc -l | tr -d ' ')
```
该命令匹配 index.html 中**所有**包含 `"company"` 的文本，包括：
- JSON 数据中的项目字段（正确）
- JavaScript 代码中的 `p.company`、`data.company` 等引用
- 其他硬编码的 `"company"` 字符串

**实际结果**：
- deploy.sh 报告：104 个项目（严重虚高）
- 实际 JSON 项目数：56 个
- Git 提交信息记录："66 个项目"、"67 个项目"（与上述两个数字均不符）

**影响**：
- 部署日志和提交信息中的项目数完全不可信
- 运维人员无法通过提交历史快速判断数据规模变化
- 可能误导数据质量判断

**修复建议**：
1. 修改 deploy.sh 中的计数逻辑，仅统计 JSON 数据区块内的 `"company"` 出现次数：
   ```bash
   PROJECT_COUNT=$(python3 -c "import json,re; h=open('index.html').read(); m=re.search(r'<script type=\\\"application/json\" id=\"tender-data\">(.*?)</script>', h, re.DOTALL); d=json.loads(m.group(1)); print(len(d['projects']))")
   ```
2. 或直接提取 JSON 中的 `projects` 数组长度

---

### ⚠️ WARNING-02：苏州农商 3 个项目疑似重复或拆分不当

**问题描述**：
苏州农商存在 3 个名称高度相似的项目：

| ID/索引 | 项目名称 |
|---------|---------|
| id=31 | 2026年度数据类通用技术外包服务项目 |
| idx=32（无 id） | 2026年度数据类通用技术外包服务项目（应用开发） |
| idx=33（无 id） | 2026年度数据类通用技术外包服务项目（数据分析） |

问题：
1. id=31 的项目与 idx=32/33 的 `company + project[:15]` 完全一致，触发重复检测
2. 这 3 个项目可能是同一招标的不同标段/分包，但处理为独立项目时缺少明确的标段标识
3. 如果确实是同一招标的拆分，应在项目名称中明确标注"标段一/标段二"或合并为一个项目

**修复建议**：
1. 确认这 3 个项目是否为同一招标公告的不同标段
2. 如果是同一招标：合并为 1 个项目，在 `overview` 中说明各标段详情
3. 如果是独立招标：确保项目名称有足够区分度（当前前 15 字完全相同）

---

### ⚠️ WARNING-03：本地工作目录存在 39 个未跟踪文件

**问题描述**：
`git status` 显示 39 个未跟踪文件，包括：
- 临时数据文件：`current_projects.json`、`updated_data.json`、`merged_data.json`、`after_step1_step2.json` 等
- CSV 数据：`tianyancha_*.csv`（5 个文件）
- 脚本文件：`health_check.py`、`merge_new.py`、`quality_gate.py` 等
- 历史归档：`恒生银信招标看板_20260629_v50.csv`、`.xlsx` 等

**风险**：
1. 临时数据文件可能包含敏感信息或过期数据
2. 工作目录混乱，增加误操作风险
3. 部分文件（如 `.DS_Store`）不应被跟踪

**修复建议**：
1. 在 `.gitignore` 中添加排除规则：
   ```
   # 临时数据文件
   *.json
   !index.html
   !tender-data.json
   
   # CSV 数据（已处理完毕）
   *.csv
   
   # macOS
   .DS_Store
   **/.DS_Store
   
   # 备份目录（保留但忽略内容变化）
   backup/
   archive/
   ```
2. 清理已确认无用的临时文件
3. 将需要保留的脚本文件纳入版本控制

---

### ⚠️ WARNING-04：本地 gh-pages 分支仍停留在 v48

**问题描述**：
- 远程 `origin/gh-pages`：v77 ✅（最新）
- 本地 `main`：v77 ✅（最新）
- **本地 gh-pages 分支：不存在**（已被 `deploy.sh` 在部署时删除）

等等，让我再确认一下...从之前的输出来看，本地分支只有 `main`，没有 `gh-pages`。让我确认一下。

从之前的 `git branch -a` 输出：
```
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/gh-pages
  remotes/origin/main
```

本地确实没有 gh-pages 分支了。但是 `deploy.sh` 第 42 行有 `git branch -D ${DEPLOY_BRANCH} 2>/dev/null || true`，这会在每次部署时删除本地 gh-pages。所以这个问题已经被 deploy.sh 的处理解决了。

不过，从故障报告来看，之前的问题已经通过修复 deploy.sh 解决了。但我应该注意到本地没有 gh-pages 分支了，这是好事。

让我修正这个问题描述。实际上，从 `git branch -a` 的输出看，本地已经没有 gh-pages 分支了（`deploy.sh` 每次部署时都会删除它）。所以这个 WARNING 实际上已经被解决了。

让我更新为：虽然本地 gh-pages 已不存在，但故障报告指出的历史风险仍然值得记录。

实际上，从当前状态来看：
- `git branch -a` 显示本地只有 `main` 分支，没有 `gh-pages`
- `deploy.sh` 已包含分支保护和删除逻辑
- 远程 `origin/gh-pages` 是正确的 v77

所以这个问题实际上已经被修复了。我可以把它降级为 INFO，或者从报告中移除。

让我重新检查...实际上当前 deploy.sh 的设计是每次部署时删除本地 gh-pages，所以本地确实不应该有 gh-pages 分支。这是正确的状态。

好的，我调整这个警告。这个实际上已经不是问题了。

**修正**：本地 gh-pages 分支已被 deploy.sh 自动删除，此问题已修复。但历史故障（v77→v48 回退）的教训仍需记录。

---

### ⚠️ WARNING-05：存在非标准招标方式"公开招标（第二次招标）"

**问题描述**：
项目数据中出现招标方式 `公开招标（第二次招标）`，但 `health_check.py` 中 `VALID_METHODS` 集合定义为：
```python
VALID_METHODS = {
    '公开招标', '邀请招标', '竞争性谈判', '竞争性磋商',
    '单一来源采购', '询价采购', '框架协议', '其他'
}
```
`公开招标（第二次招标）` 不在允许集合内。

**影响**：
- `check_method_values()` 会将其标记为 FAIL（当脚本能正常运行时）
- 数据规范化不足

**修复建议**：
1. 将 `公开招标（第二次招标）` 统一归类为 `公开招标`（在备注中标注"第二次"）
2. 或将其加入 `VALID_METHODS` 集合

---

## 四、INFO 级别信息（正常状态记录）

### ℹ️ INFO-01：线上部署状态正常

| 检查项 | 状态 | 详情 |
|--------|------|------|
| 自定义域名 hstender.cn | ✅ 200 OK | `last-modified: Tue, 07 Jul 2026 04:54:30 GMT` |
| GitHub Pages 源站 | ✅ 同步 | 远程 `origin/gh-pages` = v77 (2215480) |
| 本地 main 分支 | ✅ 最新 | v77 (2215480) |
| CNAME 配置 | ✅ 正确 | `hstender.cn` |

### ℹ️ INFO-02：deploy.sh 部署脚本已修复

- 已添加分支保护：必须在 `main` 分支上执行
- 已明确推送目标：`git push origin ${BACKUP_BRANCH}:${DEPLOY_BRANCH} --force`
- 已添加本地 gh-pages 分支自动删除逻辑
- 已添加封面/封底时间一致性校验

### ℹ️ INFO-03：数据字段完整性良好

| 检查项 | 结果 |
|--------|------|
| overview 为 "-" | 0 个项目 ✅ |
| contact 为 "-" | 0 个项目 ✅ |
| source 缺失 | 0 个项目 ✅ |
| deadline 为 "-" | 0 个项目 ✅ |
| URL 无效 | 0 个项目 ✅ |

### ℹ️ INFO-04：区域/省份一致性 100%

所有 56 个项目的 `region` 与 `province` 字段完全匹配预定义的大区映射关系，无不一致项。

### ℹ️ INFO-05：标签值全部有效

使用的标签集合：
```
{'大模型应用', '信创/国产化', '资产托管', '人力外包', '数据平台', 
 '数据服务', '渠道系统', '资产管理', '风控合规', '财富管理', 
 '资金业务', '运维服务', '金融市场/资金/同业'}
```
全部在 `VALID_TAGS` 允许集合内。

### ℹ️ INFO-06：项目分布统计

**投标建议分布**：
| 建议等级 | 数量 |
|---------|------|
| 🔥 ★★★ 强烈建议投标 | 5 |
| ⭐ ★★☆ 建议投标 | 25 |
| ★☆☆ 可关注 | 20 |
| ☆☆☆ 已截止 | 6 |

**大区分布**：
| 大区 | 数量 |
|------|------|
| 华东 | 26 |
| 华北 | 11 |
| 西南 | 8 |
| 华中 | 4 |
| 西北 | 3 |
| 东北 | 2 |
| 华南 | 2 |

### ℹ️ INFO-07：无过期项目堆积

已截止项目共 6 个，截止日期均在 2026-07-05 至 2026-07-06 之间（即过去 2 天内），无超过 2 天的已截止项目堆积。

### ℹ️ INFO-08：title 标签一致性正确

`<title>` 标签内容：
```
恒生银信招标资讯每日速递 | 2026年07月07日（更新）v77
```
- 包含正确日期：✅ `2026年07月07日`
- 包含正确版本：✅ `v77`

### ℹ️ INFO-09：历史故障已记录并修复

**v77→v48 回退事件**（2026-07-07 12:00-12:30）：
- 根因：手动 `git push origin gh-pages` 推送了本地旧版本
- 修复：手动强制推送 `main→gh-pages` 恢复 v77
- 预防措施：deploy.sh 已添加分支保护和明确推送目标
- 文档：已生成 `故障报告_v77回退至v48.md`

### ℹ️ INFO-10：定时任务配置

根据 LAST_RUN_STATUS.md 记录，系统配置了 3 个 cron 任务：
1. **7:30 主任务**：日常数据更新和部署
2. **9:30 补偿检查**：主任务失败后的补偿执行
3. **12:00 补偿检查**：第二次补偿执行

**注意**：本次检查无法直接验证 cron 任务的实际运行状态，建议通过 `Cron(action="status")` 进行独立核查。

---

## 五、修复优先级建议

| 优先级 | 问题 | 预计修复时间 | 影响 |
|--------|------|-------------|------|
| P0 | CRITICAL-01：为 5 个项目补全 id | 5 分钟 | 高 |
| P0 | CRITICAL-02：修复 health_check.py KeyError | 10 分钟 | 高 |
| P1 | WARNING-01：修复 deploy.sh 项目计数 | 15 分钟 | 中 |
| P1 | WARNING-02：确认苏州农商项目是否为重复 | 10 分钟 | 中 |
| P2 | WARNING-03：添加 .gitignore 并清理临时文件 | 20 分钟 | 低 |
| P2 | WARNING-05：标准化招标方式值 | 5 分钟 | 低 |

---

## 六、附录

### A. 检查工具输出记录

**本地 index.html 解析结果**：
```
Version: v77
Date: 2026年07月07日
TimePeriod: 中午
Projects count: 56
ID continuous: False (实际范围 1-51，期望 1-56)
Projects without 'id': 5
Duplicates (company+project[:15]): 2
Region/province issues: 0
Stale cutoff projects: 0
```

**Git 状态**：
```
分支: main
未跟踪文件: 39 个
修改未提交: 4 个 (.DS_Store, LAST_RUN_STATUS.md, backup/.DS_Store, 补充信源清单.md)
远程 origin/gh-pages: v77 (2215480)
```

### B. 相关文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `index.html` | 主页面（含内嵌 JSON 数据） | ✅ v77, 56 项目 |
| `deploy.sh` | 强制部署脚本 | ✅ 已修复 |
| `health_check.py` | 健康检查脚本 | ❌ KeyError 崩溃 |
| `CNAME` | 自定义域名配置 | ✅ hstender.cn |
| `LAST_RUN_STATUS.md` | 定时任务执行记录 | ⚠️ 与实际情况有出入 |
| `故障报告_v77回退至v48.md` | 历史故障根因分析 | ✅ 已记录 |
| `EXCLUDED_PROJECTS.md` | 排除项目清单 | ✅ 当前为空 |
| `PENDING_PROJECTS.md` | 待处理项目记录 | ⚠️ 含历史记录需更新 |

---

*报告生成时间：2026-07-07 13:00 CST*  
*下次建议检查时间：2026-07-14（一周后）*
