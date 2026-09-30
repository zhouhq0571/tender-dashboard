#!/bin/bash
set -euo pipefail

echo "📝 ========== 安全部署脚本 =========="
echo ""

REPO="tender-dashboard"
BRANCH="main"
REMOTE="git@github.com:zhouhq0571/tender-dashboard.git"

# 步骤1: 前置检查
echo "📝 步骤1: 前置检查..."
if [ ! -f index.html ]; then
    echo "❌ index.html 不存在"
    exit 1
fi

# 步骤2: 严格验证JSON
echo "📝 步骤2: 严格验证JSON..."
python3 << 'PYTHON_EOF'
import json, re, sys
with open('index.html', 'r') as f:
    html = f.read()

# 提取JSON
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
if not m:
    print('❌ 找不到数据')
    sys.exit(1)

json_str = m.group(1)

# 检查控制字符
for c in json_str:
    if ord(c) < 32 and c not in '\n\r\t':
        print(f'❌ 发现控制字符: ord={ord(c)}')
        sys.exit(1)

# 严格解析
try:
    data = json.loads(json_str)
except json.JSONDecodeError as e:
    print(f'❌ JSON解析失败: {e}')
    sys.exit(1)

# 检查项目数
projects = data.get('projects', [])
if len(projects) == 0:
    print('❌ 项目数为0！')
    sys.exit(1)

print(f'✅ JSON验证通过: {len(projects)}个项目')

# 检查undefined
if 'undefined' in json_str:
    print('❌ 发现undefined值')
    sys.exit(1)

# 检查关键字段
required = ['id', 'company', 'project', 'deadline', 'tags', 'rec']
for i, p in enumerate(projects):
    missing = [f for f in required if f not in p]
    if missing:
        print(f'❌ 项目{i+1}缺少字段: {missing}')
        sys.exit(1)

# 2026-09-30 新增：招标方式白名单硬检（与 config.py VALID_METHODS 一致，部署兜底闸）
import os
sys.path.insert(0, os.getcwd())
try:
    from config import VALID_METHODS
except Exception:
    VALID_METHODS = {'公开招标', '邀请招标', '竞争性谈判', '竞争性磋商', '单一来源采购',
                     '询价采购', '框架协议', '供应商征集', '比选采购', '其他'}
bad_method = [(p.get('id'), p.get('method')) for p in projects if p.get('method') not in VALID_METHODS]
if bad_method:
    print(f'❌ 发现非标准招标方式 {len(bad_method)} 条: {bad_method[:5]}（映射口径见 SKILL.md 步骤2.7）')
    sys.exit(1)
print('✅ 招标方式白名单检查通过')

# 2026-09-30 新增：信息来源归一化硬检（同一信源只许一种写法，如 千里马订阅→千里马招标网）
try:
    from config import BLOCKED_SOURCE_PATTERNS
except Exception:
    BLOCKED_SOURCE_PATTERNS = ('订阅', '（微信公众号）', '微信公众号（', '千里马招标网（')
bad_source = [(p.get('id'), p.get('source')) for p in projects
              if any(pat in (p.get('source') or '') for pat in BLOCKED_SOURCE_PATTERNS)]
if bad_source:
    print(f'❌ 发现非规范信息来源 {len(bad_source)} 条: {bad_source[:5]}（归一化口径见 config.SOURCE_ALIASES）')
    sys.exit(1)
print('✅ 信息来源归一化检查通过')

print('✅ 所有字段检查通过')
PYTHON_EOF

if [ $? -ne 0 ]; then
    echo "❌ 验证失败，中止部署"
    exit 1
fi

# 步骤3: 更新封面/封底/JSON时间 + <title>版本号
echo "📝 步骤3: 更新封面/封底/JSON时间..."
python3 << 'PYTHON_EOF'
import re, datetime
with open('index.html', 'r') as f:
    html = f.read()

now = datetime.datetime.now()
date_str = now.strftime('%Y年%m月%d日')
period_map = {
    (0, 6): '凌晨', (6, 9): '早上', (9, 12): '上午',
    (12, 14): '中午', (14, 18): '下午', (18, 20): '傍晚',
    (20, 24): '晚上'
}
hour = now.hour
for (start, end), period in period_map.items():
    if start <= hour < end:
        time_period = period
        break
else:
    time_period = '晚上'

full_str = f'{date_str} {time_period}'

# 1. 更新封面静态时间（匹配实际HTML结构 id="cover-update-time"）
html = re.sub(
    r'<div class="cover-meta" id="cover-update-time">.*?</div>',
    f'<div class="cover-meta" id="cover-update-time">数据更新时间：{full_str}</div>',
    html
)

# 2. 更新封底静态时间（匹配实际HTML结构 id="footer-update-time"）
html = re.sub(
    r'<span id="footer-update-time">.*?</span>',
    f'<span id="footer-update-time">{full_str}</span>',
    html
)

# 3. 同步JSON中的 timePeriod（JS运行时会读取此值覆盖静态文本，必须同步）
html = re.sub(r'"timePeriod":\s*"[^"]*"', f'"timePeriod": "{time_period}"', html)

# 4. 同步 <title> 版本号与日期（根治"JSON已更新但标题版本号过期"问题）
mj = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
if mj:
    import json as _json
    _d = _json.loads(mj.group(1))
    _ver = _d.get('version', '')
    _dt = _d.get('date', date_str)
    if _ver:
        html = re.sub(
            r'<title>.*?</title>',
            f'<title>恒生银信招标资讯每日速递 | {_dt}（更新）{_ver}</title>',
            html, flags=re.DOTALL
        )
        # 同步页尾部署注释
        _ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html = re.sub(r'<!-- Deployed v\d+ at [^>]*-->', f'<!-- Deployed {_ver} at {_ts} -->', html)

with open('index.html', 'w') as f:
    f.write(html)

print(f'✅ 时间更新: {full_str}')
PYTHON_EOF

# 步骤4: 提取版本号
echo "📝 步骤4: 提取版本号..."
VERSION=$(python3 -c "
import re
with open('index.html', 'r') as f:
    html = f.read()
m = re.search(r'\"version\"\s*:\s*\"([^\"]+)\"', html)
print(m.group(1) if m else 'unknown')
")

PROJECTS=$(python3 -c "
import json, re
with open('index.html', 'r') as f:
    html = f.read()
m = re.search(r'<script type=\"application/json\" id=\"tender-data\">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))
print(len(data.get('projects', [])))
")

echo "✅ 版本: $VERSION, 项目数: $PROJECTS"

# 步骤4.5: 版本号单调递增守卫（2026-09-28 新增，根治 v273→v271 回退故障）
# 回退保护：待部署版本必须大于线上（origin/gh-pages）当前版本，否则中止
echo "📝 步骤4.5: 版本号单调递增检查..."
REMOTE_VER=$(git fetch origin gh-pages --quiet 2>/dev/null && git show origin/gh-pages:index.html 2>/dev/null | python3 -c "
import re, sys
m = re.search(r'\"version\"\s*:\s*\"v(\d+)\"', sys.stdin.read())
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
NEW_VER_NUM=$(echo "$VERSION" | sed -n 's/^v\([0-9]*\)$/\1/p')
if [ -n "$REMOTE_VER" ] && [ -n "$NEW_VER_NUM" ]; then
    if [ "$NEW_VER_NUM" -le "$REMOTE_VER" ]; then
        echo "❌ 版本号回退拦截: 待部署 $VERSION <= 线上 v$REMOTE_VER"
        echo "   必须用 python3 bump_version.py 从 index.html 实际版本机械递增，禁止凭记忆推断版本号"
        exit 44
    fi
    echo "✅ 版本单调递增: v$REMOTE_VER (线上) → $VERSION (待部署)"
else
    echo "⚠️ 无法读取线上版本（网络或分支异常），跳过单调检查并继续（首次部署属正常）"
fi

# 步骤5: 提交到本地git
echo "📝 步骤5: 提交到本地git..."
git add index.html .nojekyll CNAME
# 2026-09-29 复盘改进：latest_meta.json 与执行汇报纳入每日提交，支持逐日回溯审计（文件缺失不阻断部署）
git add reports/latest_meta.json "reports/最新执行汇报.md" 2>/dev/null || true
git commit -m "$VERSION: $(date +'%Y年%m月%d日 %H:%M') 更新 ($PROJECTS 个项目)" || true

# 步骤6: 推送到远程
echo "📝 步骤6: 推送到远程..."
git push origin $BRANCH:gh-pages --force
git push origin $BRANCH
PUSHED_SHA=$(git rev-parse HEAD)
echo "✅ 已推送: $PUSHED_SHA"

# 步骤7: 验证 GitHub Pages 构建已触发
# 2026-09-29 修正：匿名调用 api.github.com 在共享出口 IP 下经常 403 限流，
# 限流/异常时不再误报 exit 42，降级为"以步骤8线上版本为权威判据"；
# 仅当 API 明确返回"最新部署 ≠ 本次推送 SHA"（拿到真实数据但构建未触发）才判失败。
echo "📝 步骤7: 等待 GitHub Pages 构建触发..."
API_SILENT=0
DEPLOY_TRIGGERED=0
for i in $(seq 1 12); do
    sleep 15
    RAW_RESP=$(curl -s "https://api.github.com/repos/zhouhq0571/tender-dashboard/deployments?environment=github-pages&per_page=1")
    if echo "$RAW_RESP" | grep -qi "rate limit exceeded"; then
        API_SILENT=1
        echo "  GitHub API 匿名限流（第 $((i*15)) 秒），部署记录不可见，改以线上版本为权威判据"
        break
    fi
    LATEST_DEPLOY=$(echo "$RAW_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d[0]['sha'] if d else '')
except Exception:
    print('')
" 2>/dev/null || echo "")
    if [ -n "$LATEST_DEPLOY" ]; then
        if [ "$LATEST_DEPLOY" = "$PUSHED_SHA" ]; then
            DEPLOY_TRIGGERED=1
            echo "✅ Pages 构建已触发 ($((i*15))秒)"
            break
        fi
        echo "  等待中... ($((i*15))秒, 最新部署 ${LATEST_DEPLOY:0:8} 仍非本次 $PUSHED_SHA)"
    else
        API_SILENT=1
        echo "  部署记录为空或 API 无响应（第 $((i*15)) 秒），改以线上版本为权威判据"
        break
    fi
done

if [ "$DEPLOY_TRIGGERED" != "1" ] && [ "$API_SILENT" != "1" ]; then
    echo ""
    echo "⚠️ ========== 警告：Pages 构建未触发 =========="
    echo "GitHub API 确认最新部署不是本次提交，构建服务确实未响应。"
    echo "这通常是 GitHub 服务端故障，请检查: https://www.githubstatus.com/"
    curl -s "https://www.githubstatus.com/api/v2/summary.json" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print('GitHub 当前状态:', d['status']['description'])
    for c in d.get('components', []):
        if c['name'] in ('Pages', 'Actions', 'API Requests') and c['status'] != 'operational':
            print(f\"  - {c['name']}: {c['status']}\")
except Exception:
    pass
" 2>/dev/null || true
    echo ""
    echo "恢复后需要重新触发: 再次运行本脚本，或执行"
    echo "  git commit --allow-empty -m 'retrigger pages' && git push origin main:gh-pages --force"
    echo "❗ 切勿向用户汇报'部署成功'！"
    exit 42
fi
if [ "$DEPLOY_TRIGGERED" != "1" ]; then
    echo "⚠️ 部署记录不可见（限流/空响应），跳过 API 判据，以下一步线上版本核验为准"
fi

# 步骤8: 验证线上内容已更新（绕过 CDN 缓存）
echo "📝 步骤8: 验证线上内容..."
LIVE_OK=0
for i in $(seq 1 20); do
    sleep 15
    LIVE_VERSION=$(curl -sL "https://hstender.cn/?nocache=$(date +%s)" | python3 -c "
import re, sys
m = re.search(r'\"version\"\s*:\s*\"([^\"]+)\"', sys.stdin.read())
print(m.group(1) if m else '')
" 2>/dev/null || echo "")
    if [ "$LIVE_VERSION" = "$VERSION" ]; then
        LIVE_OK=1
        echo "✅ 线上已更新为 $VERSION ($((i*15))秒)"
        break
    fi
    echo "  等待线上更新... ($((i*15))秒, 当前线上: ${LIVE_VERSION:-未知})"
done

echo ""
if [ "$LIVE_OK" = "1" ]; then
    echo "✅ ========== 部署完成并已验证 =========="
    echo "版本: $VERSION"
    echo "项目数: $PROJECTS"
    echo "线上验证: https://hstender.cn/ 已显示 $VERSION"
else
    echo "⚠️ ========== Pages 已构建但线上未更新 =========="
    echo "可能是 CDN 缓存延迟，请稍后手动验证 https://hstender.cn/"
    echo "❗ 向用户汇报时必须说明此状态，不得直接宣称成功！"
    exit 43
fi
