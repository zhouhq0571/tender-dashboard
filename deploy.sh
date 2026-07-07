#!/bin/bash
# ============================================================

# 协作第一性原理：凡是能固化的规则，就不让您手动重复；
# 凡是能自动执行的，就不让您惦记；
# 凡是能预防的，就不让您事后补救。

# 恒生银信招标看板 - 强制部署脚本
# 用途：唯一允许的部署方式。禁止手动执行 git 命令。
# ============================================================

set -e

# ---------- 固化配置（不可修改） ----------
REPO_DIR="/Users/zhouhq/Documents/kimi/workspace/bidding-daily"
REPO_NAME="tender-dashboard"
GITHUB_USER="zhouhq0571"
DEPLOY_BRANCH="gh-pages"
BACKUP_BRANCH="main"
DOMAIN="hstender.cn"
GITHUB_PAGES_URL="https://${GITHUB_USER}.github.io/${REPO_NAME}/"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error() { echo -e "${RED}❌ ERROR: $1${NC}"; exit 1; }
warn()  { echo -e "${YELLOW}⚠️  WARN: $1${NC}"; }
ok()    { echo -e "${GREEN}✅ $1${NC}"; }
info()  { echo -e "📝 $1"; }

# ---------- 步骤 1：前置检查 ----------
info "========== 招标看板强制部署开始 =========="
info ""

# 检查目录存在
if [ ! -d "$REPO_DIR" ]; then
    error "仓库目录不存在: ${REPO_DIR}"
fi

cd "$REPO_DIR"

# 检查 index.html 存在
if [ ! -f "index.html" ]; then
    error "index.html 不存在于 ${REPO_DIR}"
fi

# 检查 git 仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    error "当前目录不是 git 仓库: ${REPO_DIR}"
fi

# ★★★ 分支保护：必须在 main 分支上执行，防止误推送到 gh-pages ★★★
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "${BACKUP_BRANCH}" ]; then
    error "deploy.sh 必须在 ${BACKUP_BRANCH} 分支上执行！当前分支: ${CURRENT_BRANCH}
如需手动推送，请使用: git push origin ${BACKUP_BRANCH}:${DEPLOY_BRANCH} --force"
fi

# 删除可能残留的本地 gh-pages 分支，防止后续操作误用（安全，仅删除本地分支）
git branch -D ${DEPLOY_BRANCH} 2>/dev/null || true

# 检查远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$REMOTE_URL" != *"${GITHUB_USER}/${REPO_NAME}"* ]]; then
    error "远程仓库不正确。期望: ${GITHUB_USER}/${REPO_NAME}, 实际: ${REMOTE_URL}"
fi

ok "前置检查通过: 仓库=${REPO_NAME}, 分支=${CURRENT_BRANCH}, 远程=${REMOTE_URL}"

# ---------- 步骤 2：自动更新封面/封底时间（一劳永逸机制） ----------
info ""
info "步骤 2: 自动更新封面/封底时间..."

# 从系统获取当前时间和时段
HOUR=$(date '+%H')
YEAR=$(date '+%Y')
MONTH=$(date '+%m')
DAY=$(date '+%d')
DATE_STR="${YEAR}年${MONTH}月${DAY}日"

# 判断时段
if [ "$HOUR" -ge 0 ] && [ "$HOUR" -lt 6 ]; then
    TIME_PERIOD="凌晨"
elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 12 ]; then
    TIME_PERIOD="上午"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 14 ]; then
    TIME_PERIOD="中午"
elif [ "$HOUR" -ge 14 ] && [ "$HOUR" -lt 18 ]; then
    TIME_PERIOD="下午"
else
    TIME_PERIOD="傍晚"
fi

info "  系统时间: ${DATE_STR} ${TIME_PERIOD} (${HOUR}:00)"

# 更新 JSON 中的 date 和 timePeriod
python3 -c "
import json, re, sys
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
match = re.search(r'<script type=\"application/json\" id=\"tender-data\">(.*?)</script>', html, re.DOTALL)
if not match:
    sys.exit(1)
data = json.loads(match.group(1))
old_date = data.get('date', '')
old_time = data.get('timePeriod', '')
new_date = '${DATE_STR}'
new_time = '${TIME_PERIOD}'
if old_date != new_date or old_time != new_time:
    data['date'] = new_date
    data['timePeriod'] = new_time
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html.replace(match.group(1), new_json)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Time updated: {old_date} {old_time} -> {new_date} {new_time}')
else:
    print(f'Time already correct: {new_date} ${new_time}')
" || error "Python 时间更新失败"

# 更新静态封面/封底时间（双重保障，即使 JS 覆盖也有静态文本正确）
python3 -c "
import re, sys
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
old_pattern = r'数据更新时间：[^<]+?'
# 替换封面
cover_match = re.search(r'(id=\"cover-update-time\">)([^<]+)', html)
if cover_match:
    old_cover = cover_match.group(2)
    new_cover = '数据更新时间：${DATE_STR} ${TIME_PERIOD}'
    if old_cover != new_cover:
        html = html.replace(old_cover, new_cover, 1)
        print(f'Cover updated: {old_cover} -> {new_cover}')
# 替换封底
footer_match = re.search(r'(id=\"footer-update-time\">)([^<]+)', html)
if footer_match:
    old_footer = footer_match.group(2)
    new_footer = '${DATE_STR} ${TIME_PERIOD}'
    if old_footer != new_footer:
        html = html.replace(old_footer, new_footer, 1)
        print(f'Footer updated: {old_footer} -> {new_footer}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
" || error "Python 时间替换失败"

ok "时间更新完成: ${DATE_STR} ${TIME_PERIOD}"

# ---------- 步骤 3：读取并验证 index.html 内容 ----------
info ""
info "步骤 3: 验证 index.html 内容..."

# 检查 JSON 中项目数量
# ★★★ 修复：用 Python 从 HTML 中提取 JSON 精确计数，避免 grep 误匹配 JS 代码中的 "company" 引用 ★★★
PROJECT_COUNT=$(python3 -c "
import json, re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()
match = re.search(r'<script type=\"application/json\" id=\"tender-data\">(.*?)</script>', html, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    print(len(data.get('projects', [])))
else:
    print(0)
" 2>/dev/null || echo 0)
if [ "$PROJECT_COUNT" -eq 0 ]; then
    error "index.html 中没有找到项目数据"
fi

# 检查版本号
VERSION=$(grep -o '"version": "[^"]*"' index.html | head -1 | sed 's/"version": "//;s/"$//')
if [ -z "$VERSION" ]; then
    error "index.html 中没有找到 version 字段"
fi

# 检查日期
DATE=$(grep -o '"date": "[^"]*"' index.html | head -1 | sed 's/"date": "//;s/"$//')
if [ -z "$DATE" ]; then
    error "index.html 中没有找到 date 字段"
fi

# 检查时间词
TIME_PERIOD=$(grep -o '"timePeriod": "[^"]*"' index.html | head -1 | sed 's/"timePeriod": "//;s/"$//')
if [ -z "$TIME_PERIOD" ]; then
    warn "index.html 中没有找到 timePeriod 字段"
fi

ok "index.html 验证通过: ${PROJECT_COUNT} 个项目, 版本=${VERSION}, 日期=${DATE} ${TIME_PERIOD}"

# ---------- 步骤 4：检查封面/封底时间一致性 ----------
info ""
info "步骤 4: 检查封面/封底时间一致性..."

COVER_TIME=$(grep -o 'id="cover-update-time">[^<]*' index.html | sed 's/id="cover-update-time">数据更新时间：//;s/<\/div//g')
FOOTER_TIME=$(grep -o 'id="footer-update-time">[^<]*' index.html | sed 's/id="footer-update-time">//;s/<\/span//g')

if [ "$COVER_TIME" != "$FOOTER_TIME" ]; then
    error "封面时间[${COVER_TIME}] 与 封底时间[${FOOTER_TIME}] 不一致! 必须修正后再部署。"
fi

ok "封面/封底时间一致: ${COVER_TIME}"

# ---------- 步骤 5：提交到本地 ----------
info ""
info "步骤 5: 提交到本地 git..."

git add index.html

# 检查是否有变更
if git diff --cached --quiet; then
    warn "index.html 没有变更，跳过提交和部署"
    exit 0
fi

git commit -m "${VERSION}: ${DATE} ${TIME_PERIOD} 更新 (${PROJECT_COUNT} 个项目)"
ok "本地提交完成: ${VERSION}"

# ---------- 步骤 6：推送到远程（关键！） ----------
info ""
info "步骤 6: 推送到远程仓库..."
info "  部署分支: ${DEPLOY_BRANCH} (GitHub Pages 服务分支)"
info "  备份分支: ${BACKUP_BRANCH}"

# 强制推送到 gh-pages（GitHub Pages 实际服务分支）
# ★★★ 明确从 main 分支推送，不使用 HEAD，防止分支漂移导致版本回退 ★★★
git push origin ${BACKUP_BRANCH}:${DEPLOY_BRANCH} --force || error "推送到 ${DEPLOY_BRANCH} 失败"
ok "推送到 ${DEPLOY_BRANCH} 成功"

# 也推送到 main（备份）
git push origin ${BACKUP_BRANCH}:${BACKUP_BRANCH} || warn "推送到 ${BACKUP_BRANCH} 失败（非致命）"

# ---------- 步骤 7：等待 GitHub Pages 构建 ----------
info ""
info "步骤 7: 等待 GitHub Pages 构建 (30 秒)..."
sleep 30

# ---------- 步骤 8：验证 GitHub Pages 直接地址 ----------
info ""
info "步骤 8: 验证 GitHub Pages 直接地址 (${GITHUB_PAGES_URL})..."

RETRY=0
MAX_RETRY=5
while [ $RETRY -lt $MAX_RETRY ]; do
    GHP_VERSION=$(curl -s -L "${GITHUB_PAGES_URL}" | grep -o '"version": "[^"]*"' | head -1 | sed 's/"version": "//;s/"$//')
    GHP_COUNT=$(curl -s -L "${GITHUB_PAGES_URL}" | grep -o '"company"' | wc -l | tr -d ' ')
    
    if [ "$GHP_VERSION" = "$VERSION" ] && [ "$GHP_COUNT" -eq "$PROJECT_COUNT" ]; then
        ok "GitHub Pages 验证通过: ${GHP_VERSION}, ${GHP_COUNT} 个项目"
        break
    fi
    
    RETRY=$((RETRY + 1))
    if [ $RETRY -lt $MAX_RETRY ]; then
        warn "GitHub Pages 尚未同步 (期望: ${VERSION}/${PROJECT_COUNT}, 实际: ${GHP_VERSION:-unknown}/${GHP_COUNT:-0}), ${RETRY}/${MAX_RETRY} 重试..."
        sleep 30
    else
        error "GitHub Pages 同步失败! 期望 ${VERSION}/${PROJECT_COUNT}, 实际 ${GHP_VERSION:-unknown}/${GHP_COUNT:-0}"
    fi
done

# ---------- 步骤 9：验证自定义域名 ----------
info ""
info "步骤 9: 验证自定义域名 (${DOMAIN})..."

RETRY=0
while [ $RETRY -lt $MAX_RETRY ]; do
    DOMAIN_VERSION=$(curl -s -L "https://${DOMAIN}/" | grep -o '"version": "[^"]*"' | head -1 | sed 's/"version": "//;s/"$//')
    DOMAIN_COUNT=$(curl -s -L "https://${DOMAIN}/" | grep -o '"company"' | wc -l | tr -d ' ')
    
    if [ "$DOMAIN_VERSION" = "$VERSION" ] && [ "$DOMAIN_COUNT" -eq "$PROJECT_COUNT" ]; then
        ok "自定义域名验证通过: ${DOMAIN_VERSION}, ${DOMAIN_COUNT} 个项目"
        break
    fi
    
    RETRY=$((RETRY + 1))
    if [ $RETRY -lt $MAX_RETRY ]; then
        warn "CDN 尚未同步 (期望: ${VERSION}/${PROJECT_COUNT}, 实际: ${DOMAIN_VERSION:-unknown}/${DOMAIN_COUNT:-0}), ${RETRY}/${MAX_RETRY} 重试..."
        sleep 60
    else
        warn "CDN 同步可能延迟，但 GitHub Pages 源站已确认正确。"
        warn "用户可稍后访问 https://${DOMAIN}/ 查看最新内容。"
    fi
done

# ---------- 完成 ----------
info ""
info "========== 部署完成 =========="
ok "版本: ${VERSION}"
ok "项目数: ${PROJECT_COUNT}"
ok "日期: ${DATE} ${TIME_PERIOD}"
ok "访问地址: https://${DOMAIN}/"
info ""

exit 0
