#!/bin/bash
# ============================================================
# 恒生银信招标看板 - 部署验证脚本
# 功能：部署后自动验证网站内容是否正确
# ============================================================

set -e

RESEARCH_DIR="/Users/zhouhq/Documents/kimi/workspace/research"
VERIFY_LOG="${RESEARCH_DIR}/verify_log.txt"
URL="https://hstender.cn"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$VERIFY_LOG"
}

log "========== 部署验证开始 =========="

ERRORS=0
WARNINGS=0

# 1. 检查网站可访问性
echo "1. 检查网站可访问性..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ 网站可访问 (HTTP 200)"
    log "网站可访问 (HTTP 200)"
else
    echo "   ❌ 网站不可访问 (HTTP $HTTP_CODE)"
    log "网站不可访问 (HTTP $HTTP_CODE)"
    ERRORS=$((ERRORS + 1))
fi

# 2. 检查日期是否为今天
echo "2. 检查日期是否为今天..."
TODAY=$(date '+%Y年%m月%d日')
TODAY_ALT=$(date '+%Y年%-m月%-d日')  # 不带前导零的备用格式
PAGE_CONTENT=$(curl -s "$URL" 2>/dev/null || echo "")

if echo "$PAGE_CONTENT" | grep -q "${TODAY}" || echo "$PAGE_CONTENT" | grep -q "${TODAY_ALT}"; then
    echo "   ✅ 日期为今天 (${TODAY})"
    log "日期验证通过: ${TODAY}"
else
    echo "   ❌ 日期不是今天"
    log "日期验证失败: 期望 ${TODAY}"
    ERRORS=$((ERRORS + 1))
fi

# 3. 检查招标方式是否有禁止值
echo "3. 检查招标方式禁止值..."
FORBIDDEN_METHODS=("公告（待确认）" "待确认" "未知" "其他")
METHOD_ERROR=false
for method in "${FORBIDDEN_METHODS[@]}"; do
    if echo "$PAGE_CONTENT" | grep -q "\"method\": \"${method}\""; then
        echo "   ❌ 发现禁止值: ${method}"
        log "发现禁止招标方式: ${method}"
        METHOD_ERROR=true
        ERRORS=$((ERRORS + 1))
    fi
done
if [ "$METHOD_ERROR" = false ]; then
    echo "   ✅ 招标方式无禁止值"
    log "招标方式验证通过"
fi

# 4. 检查标签是否有明显违规
echo "4. 检查标签违规..."
TAG_ERRORS=0

# 检查信托/理财子公司项目是否标记了"金融市场/资金/同业"
if echo "$PAGE_CONTENT" | grep -B 5 '"company": "[^"]*信托"' | grep -q '"金融市场/资金/同业"'; then
    echo "   ⚠️ 信托公司项目标记了'金融市场/资金/同业'"
    log "标签违规: 信托公司项目标记金融市场/资金/同业"
    TAG_ERRORS=$((TAG_ERRORS + 1))
fi
if echo "$PAGE_CONTENT" | grep -B 5 '"company": "[^"]*理财"' | grep -q '"金融市场/资金/同业"'; then
    echo "   ⚠️ 理财子公司项目标记了'金融市场/资金/同业'"
    log "标签违规: 理财子公司项目标记金融市场/资金/同业"
    TAG_ERRORS=$((TAG_ERRORS + 1))
fi

# 检查是否有"人力外包入围"（已废弃的标签）
if echo "$PAGE_CONTENT" | grep -q '"人力外包入围"'; then
    echo "   ⚠️ 发现废弃标签'人力外包入围'，应为'人力外包'"
    log "标签违规: 发现废弃标签人力外包入围"
    TAG_ERRORS=$((TAG_ERRORS + 1))
fi

if [ "$TAG_ERRORS" -eq 0 ]; then
    echo "   ✅ 标签无明显违规"
    log "标签验证通过"
else
    ERRORS=$((ERRORS + TAG_ERRORS))
fi

# 5. 检查项目数量是否合理
echo "5. 检查项目数量..."
PROJECT_COUNT=$(echo "$PAGE_CONTENT" | grep -o '"company"' | wc -l | tr -d ' ')
if [ "$PROJECT_COUNT" -ge 0 ] && [ "$PROJECT_COUNT" -le 100 ]; then
    echo "   ✅ 项目数量合理 (${PROJECT_COUNT}个)"
    log "项目数量验证通过: ${PROJECT_COUNT}"
else
    echo "   ❌ 项目数量异常 (${PROJECT_COUNT}个)"
    log "项目数量异常: ${PROJECT_COUNT}"
    ERRORS=$((ERRORS + 1))
fi

# 6. 检查备份是否存在
echo "6. 检查备份..."
BACKUP_DIR="${RESEARCH_DIR}/backup"
if [ -d "$BACKUP_DIR" ] && [ "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    LATEST_BACKUP=$(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{8}_[0-9]{6}$' | sort -r | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "   ✅ 备份存在 (最新: ${LATEST_BACKUP})"
        log "备份验证通过: ${LATEST_BACKUP}"
    else
        echo "   ⚠️ 备份目录存在但无有效备份"
        log "备份警告: 无有效备份"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ❌ 备份不存在"
    log "备份验证失败"
    ERRORS=$((ERRORS + 1))
fi

# 7. 检查公司名映射
echo "7. 检查公司名映射..."
if echo "$PAGE_CONTENT" | grep -q '"company": "中国信托登记"'; then
    echo "   ⚠️ 发现未映射的公司名'中国信托登记'，应为'中信登'"
    log "公司名映射违规: 中国信托登记"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ 公司名映射正确"
    log "公司名映射验证通过"
fi

# 8. 检查封面封底时间是否一致
echo "8. 检查封面封底时间一致性..."
COVER_TIME=$(echo "$PAGE_CONTENT" | grep -o '数据更新时间：[^<]*' | head -1)
FOOTER_TIME=$(echo "$PAGE_CONTENT" | grep -o '数据更新时间：[^<]*' | tail -1)
if [ "$COVER_TIME" = "$FOOTER_TIME" ]; then
    echo "   ✅ 封面封底时间一致"
    log "时间一致性验证通过"
else
    echo "   ⚠️ 封面封底时间不一致"
    log "时间一致性警告: 封面[${COVER_TIME}] vs 封底[${FOOTER_TIME}]"
    WARNINGS=$((WARNINGS + 1))
fi

# 总结
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "✅ 验证全部通过 (0错误, 0警告)"
    log "验证全部通过"
    RESULT="PASS"
elif [ "$ERRORS" -eq 0 ]; then
    echo "⚠️ 验证通过但有警告 (${WARNINGS}个警告)"
    log "验证通过但有警告: ${WARNINGS}"
    RESULT="WARN"
else
    echo "❌ 验证失败 (${ERRORS}个错误, ${WARNINGS}个警告)"
    log "验证失败: ${ERRORS}错误, ${WARNINGS}警告"
    RESULT="FAIL"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log "========== 部署验证结束 [${RESULT}] =========="

# 返回结果码
if [ "$RESULT" = "PASS" ]; then
    exit 0
elif [ "$RESULT" = "WARN" ]; then
    exit 1
else
    exit 2
fi
