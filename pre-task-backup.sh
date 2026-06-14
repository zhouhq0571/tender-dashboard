#!/bin/bash
# ============================================================
# 恒生银信招标看板 - 定时任务前自动备份脚本
# 功能：在定时任务执行前，自动备份当前所有关键文件
# ============================================================

set -e

RESEARCH_DIR="/Users/zhouhq/Documents/kimi/workspace/research"
BACKUP_DIR="${RESEARCH_DIR}/backup"
LOG_FILE="${RESEARCH_DIR}/backup_log.txt"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 创建备份目录
BACKUP_TIME=$(date '+%Y%m%d_%H%M%S')
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_TIME}"
mkdir -p "$BACKUP_PATH"

log "========== 定时任务前自动备份开始 =========="
log "备份目录: ${BACKUP_PATH}"

# 备份关键文件
FILES_TO_BACKUP=(
    "index.html"
    "projects_data.json"
    "CNAME"
    "README.md"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "${RESEARCH_DIR}/${file}" ]; then
        cp "${RESEARCH_DIR}/${file}" "${BACKUP_PATH}/"
        log "已备份: ${file}"
    else
        log "警告: 文件不存在，跳过: ${file}"
    fi
done

# 备份最新的 tender_dashboard_*.html
LATEST_DASHBOARD=$(ls -1 "${RESEARCH_DIR}"/tender_dashboard_*.html 2>/dev/null | sort -r | head -1)
if [ -n "$LATEST_DASHBOARD" ]; then
    cp "$LATEST_DASHBOARD" "${BACKUP_PATH}/"
    log "已备份: $(basename "$LATEST_DASHBOARD")"
fi

# 备份 github-pages-deploy 目录
if [ -d "${RESEARCH_DIR}/github-pages-deploy" ]; then
    cp -r "${RESEARCH_DIR}/github-pages-deploy" "${BACKUP_PATH}/"
    log "已备份: github-pages-deploy/"
fi

# 清理旧备份（保留最近30个）
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{8}_[0-9]{6}$' | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 30 ]; then
    OLD_BACKUPS=$(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{8}_[0-9]{6}$' | sort | head -n -30)
    for old in $OLD_BACKUPS; do
        rm -rf "${BACKUP_DIR}/${old}"
        log "已清理旧备份: ${old}"
    done
fi

log "备份完成，共备份 $(ls -1 "${BACKUP_PATH}" | wc -l | tr -d ' ') 个文件/目录"
log "========== 定时任务前自动备份完成 =========="

# 输出备份路径（供后续步骤使用）
echo "$BACKUP_PATH"
