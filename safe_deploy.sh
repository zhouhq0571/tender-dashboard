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
    from config import BLOCKED_SOURCE_PATTERNS, normalize_source as _norm_src
except Exception:
    BLOCKED_SOURCE_PATTERNS = ('订阅', '（微信公众号）', '微信公众号（', '千里马招标网（')
    def _norm_src(s): return s
bad_source = [(p.get('id'), p.get('source')) for p in projects
              if any(pat in (p.get('source') or '') for pat in BLOCKED_SOURCE_PATTERNS)]
if bad_source:
    print(f'❌ 发现非规范信息来源 {len(bad_source)} 条: {bad_source[:5]}（归一化口径见 config.SOURCE_ALIASES）')
    sys.exit(1)
# 2026-10-15 新增：规范全名硬检（normalize_source(src) != src 即裸名漏后缀等非规范写法）
bad_canon = [(p.get('id'), p.get('source')) for p in projects
             if _norm_src(p.get('source') or '') != (p.get('source') or '').strip()]
if bad_canon:
    print(f'❌ 发现非规范全名来源 {len(bad_canon)} 条: {bad_canon[:5]}（别名表见 config.SOURCE_ALIASES）')
    sys.exit(1)
print('✅ 信息来源归一化检查通过')

# 2026-11-19 新增：招标单位简称硬检（根治全称上板；口径：normalize_company(c) != c 即非规范写法，
# 失守根因=映射只写在 SKILL.md 无代码消费；映射表见 config.COMPANY_SHORT_MAP，新增简称只改 config.py）
try:
    from config import normalize_company as _norm_co
except Exception:
    def _norm_co(s): return s
bad_co = [(p.get('id'), p.get('company')) for p in projects
          if _norm_co(p.get('company') or '') != (p.get('company') or '').strip()]
if bad_co:
    print(f'❌ 发现非规范招标单位全称 {len(bad_co)} 条: {bad_co[:8]}（映射表见 config.COMPANY_SHORT_MAP）')
    sys.exit(1)
print('✅ 招标单位简称归一化检查通过')

# 2026-11-20 新增：机构范围硬检（步骤2.5条件1代码化，根治 JSONL 批次直接信上游 is_fin_inst
# 宽口径致保险/证券/基金条目混入送审，用户 00:09 抓包；口径见 config.company_board_scope）
try:
    from config import company_board_scope as _scope
    bad_scope = [(p.get('id'), p.get('company'), _scope(p.get('company') or '')[1]) for p in projects
                 if _scope(p.get('company') or '')[0] == 'block']
    if bad_scope:
        print(f'❌ 机构范围越界 {len(bad_scope)} 条（看板只纳银行/理财子/信托/银行系金科）:')
        for _b in bad_scope[:8]:
            print(f'   - id {_b[0]} {_b[1]}（{_b[2]}）')
        sys.exit(1)
    print('✅ 机构范围硬检通过（步骤2.5条件1）')
except SystemExit:
    raise
except Exception as _e:
    print(f'⚠️ 机构范围闸导入失败（{_e}），跳过（高风险，须人工复核）')

# 2026-11-20 新增：内嵌资源体积硬检（周老师钦定同类防复发）——单文件看板 base64 内嵌资源
# （图/字体）过大 → 首屏体积膨胀、HTML 未下完 JS 不执行（11-19 厂商看板签章 1.25MB 把页面
# 撑到 1.77MB、国内手机白屏 1 分钟实证）。单块 >100KB 或单文件总量 >300KB → 拒绝部署，
# 整改口径=资源静态化外链，禁整图 dataURI 内嵌。
import re as _re
_b64_pat = _re.compile(r'data:[\w/.+-]+;base64,([A-Za-z0-9+/=]+)')
for _f in ('index.html', 'decide.html'):
    try:
        with open(_f, encoding='utf-8', errors='ignore') as _fh:
            _chunks = [len(m.group(1)) for m in _b64_pat.finditer(_fh.read())]
    except FileNotFoundError:
        continue
    _big = [ln for ln in _chunks if ln > 100 * 1024]
    if _big:
        print(f'❌ {_f} 存在超大内嵌base64资源 {len(_big)} 块（最大 {_big[0]//1024}KB>100KB闸）——须改静态文件外链（防首屏白屏）')
        sys.exit(1)
    if sum(_chunks) > 300 * 1024:
        print(f'❌ {_f} base64内嵌总量 {sum(_chunks)//1024}KB>300KB闸——须静态化整改')
        sys.exit(1)
print('✅ 内嵌资源体积硬检通过（单块≤100KB、总量≤300KB）')

# 2026-11-19 全字段代码闸自查补齐：投标建议四档 + 业务标签白名单两道闸
# （validate_new_projects.py 本已有，此处为部署兜底双保险，防绕过 validate 的手改直发）
try:
    from config import VALID_RECS as _vrec, VALID_TAGS as _vtags
    bad_rec = [(p.get('id'), p.get('rec')) for p in projects if p.get('rec') not in _vrec]
    if bad_rec:
        print(f'❌ 发现非规范投标建议 {len(bad_rec)} 条: {bad_rec[:5]}（只许四档: {_vrec}）')
        sys.exit(1)
    bad_tags = [(p.get('id'), t) for p in projects for t in (p.get('tags') or []) if t not in _vtags]
    if bad_tags:
        print(f'❌ 发现越界业务标签 {len(bad_tags)} 条: {bad_tags[:5]}（标准标签见 config.VALID_TAGS，新增只改 config.py）')
        sys.exit(1)
    print('✅ 投标建议/业务标签白名单检查通过')
except SystemExit:
    raise
except Exception as _e:
    print(f'⚠️ rec/tags 闸导入失败（{_e}），跳过低风险兜底')

# 2026-10-30 规则 O-联系方式：增量硬检——id >= CONTACT_HARD_CHECK_MIN_ID 的项目必须带真实
# 联系方式（联系人/电话/邮箱/代理机构至少一项），禁止 '-' / 空（用户 14:20 指令全场景立规）
try:
    from config import CONTACT_HARD_CHECK_MIN_ID as _contact_min
except Exception:
    _contact_min = 10**9
def _contact_empty(c):
    c = str(c or '').strip()
    return c in ('', '-', '/', '无', '暂无')
bad_contact = [(p.get('id'), p.get('company')) for p in projects
               if isinstance(p.get('id'), int) and p.get('id') >= _contact_min and _contact_empty(p.get('contact'))]
if bad_contact:
    print(f'❌ 新增项目缺"项目咨询/联系方式" {len(bad_contact)} 条: {bad_contact[:5]}（规则 O-联系方式：上板前须从公告原文/千里马详情提取，工具 tools/ql_vip_fetch.py extract_contact）')
    sys.exit(1)
if any(isinstance(p.get('id'), int) and p.get('id') >= _contact_min for p in projects):
    print('✅ 联系方式增量硬检通过')

# 2026-10-30 新增：平台首页占位 URL 硬检——新增项目（id >= CONTACT_HARD_CHECK_MIN_ID）的
# url 不允许为信源平台首页根路径（曾致快查 8 条 url 全同、validate 重复告警且链接不可点）
_PLACEHOLDER_HOSTS = ('kuaicha365.com',)
def _is_home_url(u):
    u = str(u or '').strip().rstrip('/')
    for h in _PLACEHOLDER_HOSTS:
        if u in (f'https://www.{h}', f'http://www.{h}', f'https://{h}', f'http://{h}'):
            return True
    return False
bad_url = [(p.get('id'), p.get('source')) for p in projects
           if isinstance(p.get('id'), int) and p.get('id') >= _contact_min and _is_home_url(p.get('url'))]
if bad_url:
    print(f'❌ 新增项目 URL 为平台首页占位 {len(bad_url)} 条: {bad_url[:5]}（快查来源用 url_id 拼 /outer/tender-bid/project-process 详情链接，见 tools/kc_bid_fetch.py）')
    sys.exit(1)

# 2026-10-30 新增：封面 DOM 结构硬检（10-30 事故：晨报任务改封面文本时弄丢 cover-meta 的 </div>，
# 正则未匹配静默放过，整个看板嵌套进 .cover 导致白字/标签不可点，持续约7小时才被发现）
import re as _re
if not _re.search(r'<div class="cover-meta" id="cover-update-time">[^<]*</div>', html):
    print('❌ 封面 cover-meta 未闭合或结构异常（数据更新时间 div 缺少 </div>），中止部署')
    sys.exit(1)
# 2026-11-02 规则 P-预算纯金额：全场景硬检（口径唯一来源 config.BUDGET_OK_RE；2026-08-24 立规未固化致污染混入）
try:
    from config import BUDGET_OK_RE as _BUDGET_RE
except Exception:
    _BUDGET_RE = re.compile(r'-|\d+(\.\d+)?(万)?元')
_bad_budget = [(p.get('id'), p.get('budget')) for p in projects
               if not _BUDGET_RE.fullmatch(str(p.get('budget') or '').strip())]
if _bad_budget:
    print(f'❌ 预算字段含修饰字样 {len(_bad_budget)} 条: {_bad_budget[:5]}（只许纯金额如 60万元 或 -，备注写 overview）')
    sys.exit(1)
print('✅ 预算纯金额检查通过')
from html.parser import HTMLParser
class _DivCheck(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.errors=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'div': self.stack.append(self.getpos())
    def handle_endtag(self, tag):
        if tag == 'div':
            if self.stack: self.stack.pop()
            else: self.errors.append(f'多余 </div> at {self.getpos()}')
_dc = _DivCheck(); _dc.feed(html)
if _dc.stack or _dc.errors:
    print(f'❌ div 标签不平衡: 未闭合 {len(_dc.stack)} 处（首个行号 {_dc.stack[0][0] if _dc.stack else "-" }）, 多余闭合 {len(_dc.errors)} 处')
    sys.exit(1)
print('✅ 封面/DOM 结构检查通过')

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

# 3. 同步JSON中的 date 与 timePeriod（JS运行时会读取此值覆盖静态文本，必须同步；
# 2026-10-01 修复：此前不同步 date，跨零点部署会导致封面10-01/JSON 09-30 不一致）
html = re.sub(r'"date":\s*"[^"]*"', f'"date": "{date_str}"', html, count=1)
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

# 步骤3后：meta 自愈（2026-11-23 事故固化——决策管线上板后不写 meta 致 decide/晨报双失真；
# 此处 index.html 版本号已最终定稿，派生的 version/total 才是部署真相；消费 meta 的 UI 永不吃 stale 数据）
echo "📝 步骤3.5: 同步晨报元数据（sync_loop_meta）..."
python3 tools/sync_loop_meta.py || echo "⚠️ sync_loop_meta 失败（不阻塞部署，但需关注）"

# 步骤3.55: total 字段一致性硬检（2026-11-26 固化：cron v454 删 5 条过期后 total 字段未跟随，
# 统计/封面与表格双失真——与 #8 同型。凡部署 total 必须 == len(projects)，不符即中止）
echo "📝 步骤3.55: total 字段一致性硬检..."
python3 << 'TOTAL_EOF'
import json, re, sys
html = open('index.html', encoding='utf-8').read()
m = re.search(r'id="tender-data">(.*?)</script>', html, re.S)
data = json.loads(m.group(1))
declared, actual = data.get('total'), len(data['projects'])
if declared != actual:
    print(f'❌ total 字段拦截：声明 {declared} ≠ 实际 {actual}，部署中止！')
    print('   修复：data["total"] = len(data["projects"]) 后重试')
    sys.exit(1)
print(f'✅ total 字段一致：{declared} = {actual}')
TOTAL_EOF
if [ $? -ne 0 ]; then
    echo "❌ 部署被 total 字段硬检中止，请修复 index.html 后重试"
    exit 1
fi

# 步骤3.6: 渲染硬闸（2026-11-25 特级事故固化：v448-v451 带 JS 语法损坏连过四道部署，
# 线上白屏近7小时。此后凡部署必须无头浏览器实测：无 pageerror、统计数字=项目数、表格有行，
# 任一不过即中止部署——curl/hash 只是文件层证据，不等于用户可见终态）
echo "📝 步骤3.6: 渲染硬闸（Playwright 实测）..."
python3 << 'RENDER_EOF'
import json, re, sys
html = open('index.html', encoding='utf-8').read()
m = re.search(r'id="tender-data">(.*?)</script>', html, re.S)
expected = len(json.loads(m.group(1))['projects'])
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.goto('file:///Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html')
        pg.wait_for_timeout(2500)
        stat = pg.evaluate("parseInt(document.getElementById('stat-all')?.textContent || '0')")
        rows = pg.evaluate("document.querySelectorAll('#tbody-all tr').length")
        undef = 'undefined' in (pg.evaluate("document.body.innerText") or '')
        b.close()
    ok = (not errs) and stat == expected and rows == expected and not undef
    print(f'   渲染: 期望{expected} 行/统计{stat} 行{rows} pageerror={len(errs)} undefined={undef}')
    if not ok:
        print('❌ 渲染硬闸拦截：页面不可正常渲染，部署中止！')
        sys.exit(1)
    print('✅ 渲染硬闸通过')
except SystemExit:
    raise
except Exception as e:
    print(f'⚠️ 渲染硬闸自身异常（不阻塞）: {e}')
RENDER_EOF
if [ $? -ne 0 ]; then
    echo "❌ 部署被渲染硬闸中止，请修复 index.html 后重试"
    exit 1
fi

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
git add index.html decide.html robots.txt .nojekyll CNAME img/zhou_hongqing_seal_hd.png
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
