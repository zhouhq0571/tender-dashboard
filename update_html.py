#!/usr/bin/env python3
"""
⚠️  DEPRECATED - 本脚本已废弃 ⚠️

本脚本 (update_html.py) 已被弃用，不再维护。

替代方案:
    请使用 deploy.sh 进行部署。deploy.sh 步骤2会自动处理：
    - 从系统获取当前时间和时段
    - 更新 index.html 中的日期、时间、版本信息
    - 验证封面/封底时间一致性
    - 推送到 GitHub Pages

废弃原因:
    1. 本脚本硬编码版本号 (v52→v53) 和日期，已严重过时
    2. 功能已被 deploy.sh 中的自动化逻辑完全取代
    3. deploy.sh 提供更完整的验证和部署流程

保留原因:
    - 历史参考：展示早期手动更新 HTML 的方式
    - 如需类似功能，请参考 deploy.sh 步骤2的 Python 内联代码

最后更新: 2026-07-11
废弃版本: v86-fix5 之后
"""

import sys

print("=" * 60)
print("⚠️  错误: update_html.py 已废弃")
print("=" * 60)
print()
print("本脚本不再可用。请使用以下命令进行部署:")
print("    bash deploy.sh")
print()
print("deploy.sh 会自动:")
print("  ✓ 获取系统当前时间和时段")
print("  ✓ 更新 index.html 中的时间信息")
print("  ✓ 验证数据完整性")
print("  ✓ 推送到 GitHub Pages")
print()
print("如需查看本脚本的历史代码，请查看 git 历史:")
print("    git show 94d0f59:update_html.py")
print("=" * 60)

sys.exit(1)
