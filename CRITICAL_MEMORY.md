# 关键凭据与配置持久化记忆
# 本文件用于解决AI助手记忆丢失问题
# 每次涉及对应服务时，必须先读取本文件

## 千里马招标网VIP账号
- **网址**: https://www.qianlima.com/
- **账号**: chaxun032322
- **密码**: Chaxun!2026
- **用途**: 获取招标公告完整内容（含隐藏联系方式）
- **使用场景**: 所有招标信息核实、联系方式补充、URL验证
- **重要性**: P0 - 核心生产凭据

## 看板项目数据规范
- **标准字段名**: id, company, project, overview, budget, deadline, method, contact, region, province, tags, rec, url, source
- **禁止字段名**: description（用overview）, suggestion（用rec）
- **rec标准格式**: 🔥 ★★★ 强烈建议投标 / ⭐ ★★☆ 建议投标 / 👀 ★☆☆ 可关注
- **验证脚本**: validate_new_projects.py（部署前必须运行）

## 看板关键要素字段（用户确认用）
1. 招标单位
2. 项目名称
3. 投标截止日期
4. 业务标签
5. 投标建议

## 机构简称规范
- 苏州农村商业银行 → 苏州农商
- 宁波银行股份有限公司 → 宁波银行
- 兴宝国际信托 → 兴宝信托
- 中国农业银行江苏分行 → 农业银行江苏分行

## 部署流程（安全红线）
1. **修改 index.html 数据（必须使用Python脚本结构化更新，禁止文本替换）**
2. **运行 `python3 validate_new_projects.py` 验证**（强制）
3. **运行 `python3 health_check.py` 检查**（强制）
4. **运行 `bash deploy.sh` 部署**（唯一允许的部署方式）
5. **运行 `python3 verify_deployed_site.py` 部署后验证**（强制 - 从实际网站抓取验证）

### ❌ 绝对禁止
- **禁止手动 `git push origin gh-pages`**（已导致 v77→v48 回退事故）
- **禁止直接操作 gh-pages 分支**（本地 gh-pages 已删除）
- **禁止在 JSON 字符串中写入裸换行符**（已导致项目清零事故）
- **禁止跳过验证直接部署**
- **禁止使用 Edit 工具修改 JSON 数据字段**（已导致 ID 11/27/48 字段丢失事故）
- **禁止使用文本替换方式更新 index.html 中的 JSON 数据**
- **禁止部署后不运行 verify_deployed_site.py 验证**

### 数据更新安全规范
- **唯一允许方式**: 使用 Python 脚本读取 → 修改 → 写回
- **禁止方式**: Edit 工具、sed、文本替换
- **更新后必须验证**: 每个项目必须包含 13 个标准字段
- **部署后必须验证**: 运行 verify_deployed_site.py 从实际网站抓取验证

### 部署问题根因与根除机制
详见: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/DEPLOY_SAFETY.md`
1. **修改 index.html 数据**
2. **运行 `python3 validate_new_projects.py` 验证**（强制）
3. **运行 `python3 health_check.py` 检查**（强制）
4. **运行 `bash deploy.sh` 部署**（唯一允许的部署方式）
5. **验证网站** `curl -s -L https://hstender.cn/ | grep -o 'company' | wc -l`

### ❌ 绝对禁止
- **禁止手动 `git push origin gh-pages`**（已导致 v77→v48 回退事故）
- **禁止直接操作 gh-pages 分支**（本地 gh-pages 已删除）
- **禁止在 JSON 字符串中写入裸换行符**（已导致项目清零事故）
- **禁止跳过验证直接部署**

### 部署问题根因与根除机制
详见: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/DEPLOY_SAFETY.md`

## 信源存档清单（持续更新）
### 银行类
- 千里马招标网 (https://www.qianlima.com/) - VIP账号，核心信源
- 国信招标与采购信息平台 (http://www.qgzbcgjypt.com/)
- 全国招标采购信息平台 (http://www.qgzbcgjypt.com/)
- 浦发银行采购供应商门户 (https://ebuy.spdb.com.cn/)
- 湖南银行官网 (https://www.hunan-bank.com/)
- 温州银行官网 (https://www.wzbank.cn/)
- 苏州农商银行采购管理平台 (https://www.szrcb.com/)
- 必联网 (https://www.ebnew.com/)
- 天眼查API (https://m.tianyancha.com/)
- 海南农商银行官网 (https://www.hainanbank.com.cn/) - 2026-07-14新增

### 信托类
- 中信信托采购平台 (https://ebuy.citic.com/)
- 中招联合 (https://365trade.com.cn/)
- 水滴标讯 (https://biaoxun.shuidi.cn/)
- 全国招标采购信息平台

### 新增信源记录
- 2026-07-14: 海南农商银行官网 (https://www.hainanbank.com.cn/) - 用户主动提供
- 2026-07-14: 浦发银行采购门户需登录访问，已记录账号体系

### 信源使用规则
- 每次生成报告时优先搜索已存档信源
- 新发现的有效信源必须立即加入本清单
- 失效信源标记为[已失效]并记录替代方案

## 凭据存储
- **加密存储**: `credential_store.py` → `~/.config/tender-dashboard/credentials.enc`
- **读取方式**: `python3 credential_store.py get qianlima`
- **切勿硬编码**: 任何脚本不得明文写入密码

## 文件位置
- 看板文件: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html`
- 验证脚本: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/validate_new_projects.py`
- 健康检查: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/health_check.py`
- 部署后验证: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/verify_deployed_site.py`（新增 - 从实际网站抓取验证）
- 部署脚本: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/deploy.sh`
- 安全配置: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/DEPLOY_SAFETY.md`
- 新增项目指南: `/Users/zhouhq/Documents/kimi/workspace/bidding-daily/NEW_PROJECT_GUIDE.md`
1. 修改index.html
2. 运行 validate_new_projects.py 验证
3. git add -A && git commit -m "..." && git push origin main
4. 确认GitHub Pages已更新（curl -I https://hstender.cn/）

## 文件位置
- 看板文件: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html
- 验证脚本: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/validate_new_projects.py
- 部署后验证: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/verify_deployed_site.py（新增）
- 新增项目指南: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/NEW_PROJECT_GUIDE.md
