# 招标看板部署问题根除机制
# 本文件是部署安全的最高准则，任何部署操作必须遵循

## 一、部署问题根因分析

### 历史故障模式

| 时间 | 故障 | 根因 | 影响 |
|------|------|------|------|
| 2026-07-07 | v77→v48回退 | 手动`git push origin gh-pages`推送了本地旧分支 | 版本回退29个 |
| 2026-07-11 | 项目数清零 | JSON数据含裸换行符导致解析失败 | 网站显示0项目 |
| 多次 | 时间未更新 | deploy.sh步骤2时间更新逻辑有bug（重复代码块） | 用户困惑 |

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
