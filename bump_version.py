#!/usr/bin/env python3
"""
版本号机械化递增（2026-09-28 新增，根治版本回退故障）

背景：2026-09-28 凌晨定时任务把 v273 错写为 v271。根因是模型凭会话记忆推断
版本号（记忆中停留在 v270），未从 index.html 实际读取。

本脚本职责：
1. 从 index.html 的 JSON 中读取当前版本号；
2. 与 origin/gh-pages 上的线上版本取最大值 +1（防御本地文件过旧的情况）；
3. 写回 index.html 的 JSON version 字段（<title> 与部署注释由 safe_deploy.sh 步骤3同步）。

用法：
    python3 bump_version.py          # 递增并写回
    python3 bump_version.py --check  # 只打印将要写入的版本号，不写文件

红线：禁止任何任务凭记忆/汇报/元数据推断版本号，一律调用本脚本。
"""
import json, re, subprocess, sys

INDEX = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'


def read_version_from_html(html: str):
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
    if not m:
        raise SystemExit('❌ index.html 中找不到 tender-data JSON')
    return json.loads(m.group(1)).get('version', '')


def remote_version() -> int:
    """取 origin/gh-pages 上的版本号（取不到返回 0）"""
    try:
        subprocess.run(['git', 'fetch', 'origin', 'gh-pages', '--quiet'], cwd='/Users/zhouhq/Documents/kimi/workspace/bidding-daily', timeout=60)
        out = subprocess.run(
            ['git', 'show', 'origin/gh-pages:index.html'],
            cwd='/Users/zhouhq/Documents/kimi/workspace/bidding-daily',
            capture_output=True, timeout=30).stdout.decode('utf-8', 'ignore')
        v = read_version_from_html(out)
        return int(re.search(r'(\d+)', v).group(1)) if v else 0
    except Exception:
        return 0


def main():
    html = open(INDEX, encoding='utf-8').read()
    cur = read_version_from_html(html)
    m = re.search(r'v(\d+)', cur or '')
    if not m:
        raise SystemExit(f'❌ 本地版本号无法解析: {cur!r}')
    local_n = int(m.group(1))
    remote_n = remote_version()
    new_n = max(local_n, remote_n) + 1
    new_v = f'v{new_n}'

    print(f'本地版本: {cur} | 线上版本: v{remote_n} → 新版本: {new_v}')

    if '--check' in sys.argv:
        return

    if new_n <= local_n:
        raise SystemExit(f'❌ 版本号未递增: {new_v} <= {cur}')

    m2 = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.DOTALL)
    d = json.loads(m2.group(2))
    d['version'] = new_v
    html = html[:m2.start(2)] + json.dumps(d, ensure_ascii=False, indent=2) + html[m2.end(2):]
    open(INDEX, 'w', encoding='utf-8').write(html)
    print(f'✅ 已写回 index.html: {cur} → {new_v}')


if __name__ == '__main__':
    main()
