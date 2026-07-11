# 恒生银信招标看板 - 文件系统健康检查报告

**检查时间**: 2026-07-07 12:59:40 CST
**系统**: 恒生银信招标看板
**部署目标**: zhouhq0571/tender-dashboard (gh-pages分支)
**域名**: hstender.cn
**声称版本**: v77 | **声称项目数**: 56

## 执行摘要

| 指标 | 值 |
|------|-----|
| 实际版本 | v77 |
| 实际项目数 | 56 |
| 总文件数 | 687 |
| 总目录数 | 244 |
| 总大小 | 18.47 MB |
| archive大小 | 5.96 MB |
| 备份目录数 | 14 |

## 问题汇总

- 🔴 **CRITICAL**: 1 项
- 🟡 **WARNING**: 3 项
- 🔵 **INFO**: 2 项
- ✅ **通过**: 11 项

---

## 详细问题列表

### 🔴 CRITICAL 级别 (1项)

**1. [安全事故] 今日发生版本回退事件(v77→v48)**
- 详情: 2026-07-07 12:00-12:30发生了严重的版本回退事件：手动git push origin gh-pages将本地停留在v48的gh-pages分支推送到远程，覆盖了v77。虽然已恢复，但暴露严重操作风险。
- **修复建议**: 1.立即删除本地gh-pages分支(git branch -D gh-pages); 2.确认deploy.sh中已包含分支保护; 3.建立部署操作规范文档

### 🟡 WARNING 级别 (3项)

**1. [备份管理] 最近7天无完整备份目录**
- 详情: backup/子目录中无最近7天内的完整备份
- **修复建议**: 检查备份机制是否正常执行

**2. [文件系统清理] 中间文件过多**
- 详情: 根目录存在16个中间/临时文件: step0_2_result.json, step1_2_result.json, qianlima_search_result.json, stage_abc_results.json, merged_results.json, stage_abc_results.json, qianlima_search_result.json, updated_data.json, merged_data.json, tianyancha_bank.csv...
- **修复建议**: 清理已完成的中间结果文件，或建立统一的temp/目录

**3. [版本控制] 未跟踪文件过多**
- 详情: git状态显示有44个未跟踪/修改文件
- **修复建议**: 清理不需要版本控制的文件，或添加到.gitignore

### 🔵 INFO 级别 (2项)

**1. [文件系统清理] .DS_Store文件**
- 详情: 发现4个.DS_Store文件: ./.DS_Store, ./archive/.DS_Store, ./backup/.DS_Store, ./backup/20260612_113746/.DS_Store
- **修复建议**: 执行: find . -name '.DS_Store' -delete && echo '.DS_Store' >> .gitignore

**2. [归档检查] archive目录存在重复文件**
- 详情: 发现8组重复文件:
  tender_data_v5.xlsx == tender_data_v4.xlsx
  tender_data_v5.xlsx == tender_data_v3.xlsx
  tender_dashboard_v10.html == 恒生银信招标资讯每日速递（2026年6月9日）-bak.html
  tender_dashboard_v9.html == 恒生银信招标需求每日速递（2026年6月9日）v9.html
  tender_dashboard_v11.html == 恒生银信招标资讯每日速递（2026年6月9日）v11.html
  tender_dashboard_v11.html == 恒生银信招标资讯每日速递（2026年6月9日）.html
  tender_dashboard_v14.html == 恒生银信招标资讯每日速递（2026年6月10日）v14.html
  tender_data_v5.xlsx == tender_data_v6.xlsx
- **修复建议**: 清理重复归档文件，保留最新版本

## 通过的检查项

- ✅ [数据完整性] index.html JSON解析: 版本=v77, 日期=2026年07月07日 中午, 项目数=56
- ✅ [数据一致性] 版本号匹配: index.html版本v77与系统声称一致
- ✅ [数据一致性] 项目数量匹配: 56个项目与声明一致
- ✅ [数据时效性] 日期匹配: 日期2026年07月07日与当前日期一致
- ✅ [备份管理] 根目录备份数量: backup/根目录有7个备份，数量合理
- ✅ [文件完整性] 空文件检查: 未发现空文件
- ✅ [磁盘使用] archive大小: archive占用6.0MB
- ✅ [部署配置] CNAME配置: CNAME文件内容正确: hstender.cn
- ✅ [部署脚本] deploy.sh结构: 脚本包含错误退出和分支配置
- ✅ [部署脚本] 分支保护: deploy.sh包含分支保护逻辑
- ✅ [运维工具] health_check.py: 健康检查脚本存在

---

## 紧急修复清单（按优先级排序）

### P0 - 立即执行

1. **删除本地gh-pages分支**（防止再次误推送导致回退）
   ```bash
   git branch -D gh-pages
   ```

2. **清理.DS_Store文件**
   ```bash
   find . -name '.DS_Store' -delete
   echo '.DS_Store' >> .gitignore
   ```

### P1 - 今日内完成

3. **清理archive中重复文件**（节省约1-2MB）
   - tender_data_v3/v4/v5/v6.xlsx 内容相同，保留一个即可
   - tender_dashboard_v10 == 恒生银信招标资讯每日速递（2026年6月9日）-bak.html
   - tender_dashboard_v11 == 恒生银信招标资讯每日速递（2026年6月9日）.html
   - tender_dashboard_v14 == 恒生银信招标资讯每日速递（2026年6月10日）v14.html

4. **整理根目录中间文件**
   ```bash
   mkdir -p temp
   mv step*_result.json stage_*.json merged_*.json updated_data.json qianlima_*.json temp/
   mv tianyancha_*.csv temp/
   ```

### P2 - 本周内完成

5. **建立.gitignore**，排除以下文件：
   ```
   .DS_Store
   *.tmp
   temp/
   ```

6. **检查备份机制**：最近7天backup/子目录无完整备份，确认定时备份脚本是否正常

---

## 文件系统统计

| 区域 | 文件数 | 大小 | 说明 |
|------|--------|------|------|
| 根目录 | ~50 | ~3MB | 主要工作文件 |
| archive/ | 91 | 6.0MB | 历史归档 |
| backup/ | 61 | ~3MB | 日常备份 |
| .git/ | - | 4.8MB | 版本控制 |

---
*报告由系统健康检查专家自动生成*