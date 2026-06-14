#!/bin/bash
# ============================================================
# 恒生银信招标看板 - 应急回退脚本
# 功能：从最新备份恢复 index.html 并重新部署
# 触发条件：用户说"回退招标看板"/"恢复招标看板备份"/"hstender.cn 紧急恢复"/"招标看板数据错乱了"/"恢复招标看板"
# ============================================================

set -e

RESEARCH_DIR="/Users/zhouhq/Documents/kimi/workspace/research"
BACKUP_DIR="${RESEARCH_DIR}/backup"
LOG_FILE="${RESEARCH_DIR}/restore_log.txt"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 应急回退开始 =========="

# 1. 检查备份目录
if [ ! -d "$BACKUP_DIR" ]; then
    log "错误：备份目录不存在: $BACKUP_DIR"
    echo "❌ 回退失败：备份目录不存在"
    exit 1
fi

# 2. 找到最新备份
LATEST_BACKUP=$(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{8}_[0-9]{6}$' | sort -r | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    log "错误：没有找到有效的备份目录"
    echo "❌ 回退失败：没有找到有效备份"
    exit 1
fi

LATEST_BACKUP_DIR="${BACKUP_DIR}/${LATEST_BACKUP}"
log "找到最新备份: $LATEST_BACKUP"

# 3. 检查备份文件完整性
if [ ! -f "${LATEST_BACKUP_DIR}/index.html" ]; then
    log "错误：备份中缺少 index.html"
    echo "❌ 回退失败：备份文件不完整"
    exit 1
fi

# 4. 先备份当前状态（防止二次回退时丢失）
CURRENT_BACKUP_TIME=$(date '+%Y%m%d_%H%M%S')
CURRENT_BACKUP_DIR="${BACKUP_DIR}/${CURRENT_BACKUP_TIME}_pre_restore"
mkdir -p "$CURRENT_BACKUP_DIR"
cp "${RESEARCH_DIR}/index.html" "${CURRENT_BACKUP_DIR}/" 2>/dev/null || true
log "已保存当前状态到: ${CURRENT_BACKUP_TIME}_pre_restore"

# 5. 从备份恢复
log "正在从备份恢复 index.html..."
cp "${LATEST_BACKUP_DIR}/index.html" "${RESEARCH_DIR}/index.html"

# 6. 更新封面和封底时间为当前时段
CURRENT_HOUR=$(date '+%H')
if [ "$CURRENT_HOUR" -ge 0 ] && [ "$CURRENT_HOUR" -lt 5 ]; then
    TIME_PERIOD="凌晨"
elif [ "$CURRENT_HOUR" -ge 5 ] && [ "$CURRENT_HOUR" -lt 8 ]; then
    TIME_PERIOD="早上"
elif [ "$CURRENT_HOUR" -ge 8 ] && [ "$CURRENT_HOUR" -lt 11 ]; then
    TIME_PERIOD="上午"
elif [ "$CURRENT_HOUR" -ge 11 ] && [ "$CURRENT_HOUR" -lt 13 ]; then
    TIME_PERIOD="中午"
elif [ "$CURRENT_HOUR" -ge 13 ] && [ "$CURRENT_HOUR" -lt 17 ]; then
    TIME_PERIOD="下午"
elif [ "$CURRENT_HOUR" -ge 17 ] && [ "$CURRENT_HOUR" -lt 19 ]; then
    TIME_PERIOD="傍晚"
else
    TIME_PERIOD="晚上"
fi

TODAY=$(date '+%Y年%m月%d日')
# 更新封面时间
sed -i '' "s/<div class=\"cover-meta\">数据更新时间：.*<\/div>/<div class=\"cover-meta\">数据更新时间：${TODAY} ${TIME_PERIOD}<\/div>/g" "${RESEARCH_DIR}/index.html"
# 更新封底时间
sed -i '' "s/数据更新时间：.*<br\/>/数据更新时间：${TODAY} ${TIME_PERIOD}<br\/>/g" "${RESEARCH_DIR}/index.html"

log "已更新封面封底时间为: ${TODAY} ${TIME_PERIOD}"

# 7. 部署到GitHub Pages
log "正在部署到GitHub Pages..."
cd "$RESEARCH_DIR"

# 尝试git推送
git add index.html
git commit -m "🚨 应急回退: 恢复到备份版本 ${LATEST_BACKUP} ($(date '+%Y-%m-%d %H:%M:%S'))" || true

PUSH_SUCCESS=false
for i in 1 2 3; do
    if git push origin main 2>/dev/null; then
        PUSH_SUCCESS=true
        log "GitHub推送成功（第${i}次尝试）"
        break
    else
        log "GitHub推送失败（第${i}次尝试），等待重试..."
        sleep 10
    fi
done

if [ "$PUSH_SUCCESS" = false ]; then
    log "警告：GitHub推送失败，但本地文件已恢复"
    echo "⚠️ 本地文件已恢复，但GitHub推送失败，请手动推送"
fi

# 8. 统计恢复的项目数量
PROJECT_COUNT=$(grep -o '"company"' "${RESEARCH_DIR}/index.html" | wc -l | tr -d ' ')
log "恢复的项目数量: $PROJECT_COUNT"

# 9. 输出结果
echo ""
echo "✅ 应急回退完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "恢复的备份版本: ${LATEST_BACKUP}"
echo "恢复的项目数量: ${PROJECT_COUNT}"
echo "线上地址: https://hstender.cn"
echo "CDN刷新预计: 1-3分钟"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log "========== 应急回退完成 =========="

# 10. 等待CDN刷新并验证
sleep 30
echo "正在验证线上状态..."
if curl -s https://hstender.cn/ | grep -q "${TODAY}"; then
    echo "✅ 线上验证通过：日期已更新为今天"
    log "线上验证通过"
else
    echo "⚠️ 线上验证未通过，请稍后手动刷新检查"
    log "线上验证未通过"
fi
