#!/bin/bash
# 招标看板一键推送脚本（新仓库版）
# 使用说明：
# 1. 在 GitHub 上创建新仓库（名称任意，如 tender-dashboard）
# 2. 修改下面的 NEW_REPO_NAME 变量
# 3. 运行: bash push.sh

set -e

# ============================================
# 请修改这里：新仓库名称（GitHub上创建的名称）
NEW_REPO_NAME="tender-dashboard"
# ============================================

echo "=== 招标看板推送脚本（新仓库版）==="
echo "当前时间: $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 进入目录
cd /Users/zhouhq/Documents/kimi/workspace/bidding-daily

echo ""
echo "=== 步骤1: 检查当前状态 ==="
git log --oneline -1
git branch -v

echo ""
echo "=== 步骤2: 切换远程URL到新仓库 ==="
# 先移除旧远程（如果存在）
git remote remove origin 2>/dev/null || true
# 添加新远程（带token，推送后移除）
git remote add origin https://ghp_KKONsXg9c8UA5cnJUUhgb7t8bDShI0fyTus@github.com/zhouhq0571/${NEW_REPO_NAME}.git
git remote -v

echo ""
echo "=== 步骤3: 配置HTTP/1.1协议 ==="
git config --global http.version HTTP/1.1
git config --global http.lowSpeedLimit 1000
git config --global http.lowSpeedTime 300
echo "HTTP/1.1已配置"

echo ""
echo "=== 步骤4: 推送 gh-pages 分支 ==="
if git push -u origin gh-pages; then
    echo "✅ gh-pages 推送成功"
else
    echo "❌ gh-pages 推送失败"
    echo "请尝试以下方案："
    echo "  1. 断开恒生电子WiFi/VPN"
    echo "  2. 连接手机热点"
    echo "  3. 重新运行 bash push.sh"
    exit 1
fi

echo ""
echo "=== 步骤5: 推送 main 分支 ==="
if git push -u origin main; then
    echo "✅ main 推送成功"
else
    echo "⚠️ main 推送失败（gh-pages已成功，main可以稍后推送）"
fi

echo ""
echo "=== 步骤6: 移除token（安全清理） ==="
git remote set-url origin https://github.com/zhouhq0571/${NEW_REPO_NAME}.git
git config --global --unset http.version 2>/dev/null || true
git config --global --unset http.lowSpeedLimit 2>/dev/null || true
git config --global --unset http.lowSpeedTime 2>/dev/null || true
echo "远程URL已恢复为安全状态"

echo ""
echo "=== 验证远程URL ==="
git remote -v

echo ""
echo "=== 推送完成 ==="
echo "新仓库: https://github.com/zhouhq0571/${NEW_REPO_NAME}"
echo ""
echo "下一步（手动设置GitHub Pages）："
echo "1. 访问 https://github.com/zhouhq0571/${NEW_REPO_NAME}/settings/pages"
echo "2. Source 选择 'Deploy from a branch'"
echo "3. Branch 选择 'gh-pages' → '/ (root)' → 点击 Save"
echo "4. 如果有自定义域名，在 Custom domain 填入 hstender.cn → 点击 Save"
echo "5. 等待 5-10 分钟，访问 https://hstender.cn 验证"
