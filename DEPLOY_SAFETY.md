# 招标看板部署问题根除机制
# 本文件是部署安全的最高准则，任何部署操作必须遵循

## 一、部署问题根因分析

### 历史故障模式

| 时间 | 故障 | 根因 | 影响 |
|------|------|------|------|
| 2026-07-07 | v77→v48回退 | 手动`git push origin gh-pages`推送了本地旧分支 | 版本回退29个 |
| 2026-07-11 | 项目数清零 | JSON数据含裸换行符导致解析失败 | 网站显示0项目 |
| 多次 | 时间未更新 | deploy.sh步骤2时间更新逻辑有bug（重复代码块） | 用户困惑 |
| 2026-09-28 | v273→v271回退 | 定时任务凭会话记忆推断版本号，未读 index.html 实际版本 | 版本号回退，已三重修复（bump_version.py 机械递增 + safe_deploy 步骤4.5 单调守卫 + prompt 红线） |
| 2026-09-29 | 误报"Pages构建未触发"(exit 42) | api.github.com 匿名调用被共享出口 IP 限流，轮询拿到空响应被当成"未触发"，实际构建正常 | 虚假告警；已修复：检出限流/空响应时降级为以线上版本（步骤8）为权威判据，仅 API 明确返回非本次 SHA 才判失败 |

### 根因分类

1. **手动操作陷阱**：用户/AI在deploy.sh失败后手动执行git命令，误推旧分支
2. **数据污染**：从PDF/网页提取的内容未做JSON转义处理
3. **脚本缺陷**：deploy.sh有重复代码块，时间更新逻辑不可靠
4. **缺乏验证**：部署前没有强制验证环节

---

## 二、根除机制（已实施/待实施）

### ✅ 已实施

1. **强制部署脚本** (`deploy.sh`)：唯一允许的部署方式
2. **分支保护**：必须在main分支执行，禁止直接操作gh-pages
3. **健康检查** (`health_check.py`)：部署前自动验证
4. **统一配置** (`config.py`)：避免分散定义导致不一致
5. **加密凭据** (`credential_store.py`)：避免记忆丢失
6. **关键记忆** (`CRITICAL_MEMORY.md`)：持久化重要信息

### 🔧 待实施改进

1. **部署前强制验证**：deploy.sh增加`python3 validate_new_projects.py`调用
2. **JSON数据清洗**：所有写入index.html的数据必须经过`json.dumps()`序列化
3. **本地gh-pages分支清理**：删除本地gh-pages分支，消除误推风险
4. **部署后自动验证**：deploy.sh增加网站curl验证环节
5. **单点部署入口**：禁止任何其他部署方式

---

## 三、部署安全红线（不可违反）

### ❌ 绝对禁止

1. **禁止手动git push**：任何情况下不得手动执行`git push origin gh-pages`
2. **禁止直接修改gh-pages分支**：gh-pages分支只能由deploy.sh管理
3. **禁止在JSON字符串中写入裸换行符**：所有文本必须经过json.dumps转义
4. **禁止跳过验证部署**：health_check.py和validate_new_projects.py必须通过

### ✅ 强制流程

```
修改数据 → 运行validate_new_projects.py → 运行health_check.py → 运行deploy.sh → 验证网站
```

---

## 四、应急回退机制

### 自动回退（deploy.sh内置）

如果部署后验证失败，deploy.sh会自动：
1. 保留上一次成功的git commit hash
2. 快速回退到上一个已知良好版本

### 手动回退（紧急）

```bash
cd /Users/zhouhq/Documents/kimi/workspace/bidding-daily
# 查看历史版本
git log --oneline main | head -10
# 回退到指定版本（替换<hash>为实际hash）
git push origin <hash>:gh-pages --force
```

---

## 五、责任清单

| 角色 | 责任 |
|------|------|
| AI助手 | 严格执行deploy.sh，绝不手动git操作，部署后验证网站 |
| 用户 | 发现网站异常立即报告，不自行操作git |
| deploy.sh | 唯一部署入口，包含完整验证和回退逻辑 |
| health_check.py | 部署前强制检查，发现问题阻止部署 |

## 2026-07-20 教训：GitHub Pages 构建未触发（外部故障）

**现象**：代码已推送 main + gh-pages，但网站停留在旧版本（v107），deployments API 无新记录。

**根因**：GitHub 官方故障（事件 8vfyvq16hzh9，2026-07-19T23:34Z 起，Actions/Pages/API 全部降级）。Pages 构建走 Actions 基础设施，GitHub 侧故障期间推送不会触发构建，且无排队补偿——恢复后必须重新推送触发。

**排查标准动作**：
1. `curl "https://api.github.com/repos/zhouhq0571/tender-dashboard/deployments?environment=github-pages&per_page=1"` 看最新部署 SHA 是否等于本地 HEAD
2. `curl "https://www.githubstatus.com/api/v2/summary.json"` 看 Pages/Actions/API 状态
3. 推送成功但无新部署 = GitHub 侧问题，恢复后 `git commit --allow-empty -m retrigger && git push origin main:gh-pages --force`

**机制改进（已实施）**：safe_deploy.sh 新增步骤7/8——部署后自动轮询 Pages 部署记录（exit 42=构建未触发）和线上版本号（exit 43=CDN未刷新），未验证通过前禁止汇报"部署成功"。
