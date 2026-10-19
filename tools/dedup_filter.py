# -*- coding: utf-8 -*-
"""跨日去重过滤器：只让"没见过"的条目进入模型上下文，已见条目零 token 剔除。
================================================================
背景：每日搜索的返回里大部分是重复历史条目，直接塞给模型是最大 token 浪费之一。
本工具在脚本层做 hash 去重（md5(规范化url) 优先，无 url 用 md5(标题)），
命中历史库的直接丢弃，只把新条目输出给下游（模型/候选流程）。

用法：
  # 管道输入（json 数组，元素含 url 或 title）
  cat items.json | python3 tools/dedup_filter.py

  # 文件输入（支持多文件合并去重）
  python3 tools/dedup_filter.py monitor/subscribe_items_*.json

  # 只看统计不输出（--stats）
  echo '[...]' | python3 tools/dedup_filter.py --stats

行为：
  - 本次输出的新条目 hash 立即追加到 monitor/seen_hashes.jsonl
  - 已见条目静默丢弃（退出码 0，不报错）
  - 输出 = 新条目的 JSON 数组（保持原字段不变）

历史库：monitor/seen_hashes.jsonl（一行一个 hash，可安全手工删除某行使对应条目"复活"）
首次运行自动创建。建议每日任务在所有搜索源之后、进入候选流程之前统一过一遍。
"""
import sys, os, json, hashlib, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN = os.path.join(BASE, 'monitor', 'seen_hashes.jsonl')

_CJK_ALNUM = re.compile(r'[^0-9a-z\u4e00-\u9fff]+')


def norm_title(s):
    """标题规范化：只留中文+字母+数字，小写。跨渠道同项目比对用。"""
    return _CJK_ALNUM.sub('', (s or '').lower())


def load_board_titles():
    """在板项目标题规范化集合（index.html 无则空集）。2026-10-19 新增：
    跨渠道同项目查重（湖州银行大模型平台经乐采云兜底与在板 id59 重复命中的教训）。"""
    path = os.path.join(BASE, 'index.html')
    titles = set()
    try:
        with open(path, encoding='utf-8') as f:
            m = re.search(r'<script type="application/json" id="tender-data">'
                          r'(.*?)</script>', f.read(), re.S)
        if m:
            for p in json.loads(m.group(1)).get('projects', []):
                t = norm_title(p.get('project', ''))
                if len(t) >= 8:
                    titles.add(t)
    except Exception:
        pass
    return titles


def is_board_dup(title, board_titles):
    """保守判定：规范化后相等或互为子串（均≥10字）才算同项目，防误杀。"""
    t = norm_title(title)
    if len(t) < 10:
        return False
    for bt in board_titles:
        if t == bt or (len(bt) >= 10 and (t in bt or bt in t)):
            return True
    return False


def norm_key(item):
    url = (item.get('url') or item.get('link') or '').strip().lower()
    if url:
        url = url.split('#')[0].rstrip('/')
        # 2026-10-19 修复：泛链接（裸域名无路径，如快查 API 返回的 kuaicha365.com 首页）
        # 对所有条目是同一个 hash，会让第二条起全部被误杀——此类回退用标题哈希
        parts = url.split('://', 1)[-1].split('/', 1)
        path = parts[1] if len(parts) > 1 else ''
        if path:
            return 'u:' + hashlib.md5(url.encode('utf-8')).hexdigest()
    title = ' '.join((item.get('title') or item.get('name') or '').split())
    return 't:' + hashlib.md5(title.encode('utf-8')).hexdigest()


def load_seen():
    if not os.path.exists(SEEN):
        return set()
    seen = set()
    with open(SEEN, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                seen.add(line)
    return seen


def main():
    stats_only = '--stats' in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith('--')]

    raw = ''
    if files:
        items = []
        for fn in files:
            try:
                with open(fn, encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data = data.get('keep') or data.get('items') or data.get('data') or []
                if isinstance(data, list):
                    items.extend(data)
            except Exception as e:
                print(f'# skip {fn}: {e}', file=sys.stderr)
        raw_items = items
    else:
        raw = sys.stdin.read()
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data = data.get('keep') or data.get('items') or data.get('data') or []
            raw_items = data if isinstance(data, list) else []
        except Exception:
            print('# stdin 不是合法 JSON 数组', file=sys.stderr)
            sys.exit(1)

    seen = load_seen()
    board = load_board_titles()
    fresh, dup, board_dup = [], 0, 0
    new_hashes = []
    for it in raw_items:
        if not isinstance(it, dict):
            continue
        k = norm_key(it)
        if k in seen:
            dup += 1
            continue
        if is_board_dup(it.get('title') or it.get('project') or '', board):
            board_dup += 1
            continue
        seen.add(k)
        new_hashes.append(k)
        fresh.append(it)

    if not stats_only:
        print(json.dumps(fresh, ensure_ascii=False))

    if new_hashes:
        os.makedirs(os.path.dirname(SEEN), exist_ok=True)
        with open(SEEN, 'a', encoding='utf-8') as f:
            for k in new_hashes:
                f.write(k + '\n')

    print(f'#dedup: total={len(raw_items)} fresh={len(fresh)} dup={dup} '
          f'board_dup={board_dup} seen_db={len(seen)} board={len(board)}',
          file=sys.stderr)


if __name__ == '__main__':
    main()
