# 关键凭据与配置持久化记忆
# 本文件用于解决AI助手记忆丢失问题
# 每次涉及对应服务时，必须先读取本文件

## 千里马招标网VIP账号
- **账号**: 13675825771
- **密码**: Hengsheng123
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

## 部署流程
1. 修改index.html
2. 运行 validate_new_projects.py 验证
3. git add -A && git commit -m "..." && git push origin main
4. 确认GitHub Pages已更新（curl -I https://hstender.cn/）

## 文件位置
- 看板文件: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html
- 验证脚本: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/validate_new_projects.py
- 新增项目指南: /Users/zhouhq/Documents/kimi/workspace/bidding-daily/NEW_PROJECT_GUIDE.md
