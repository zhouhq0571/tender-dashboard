#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信源产出记账脚本（招标看板版，2026-09-01 借鉴周报 source_stats.py 机制）
用法: python3 source_stats.py <月份标签，如 2026-09>
功能:
  1. 从 index.html 内嵌 tender-data JSON 读取当前看板项目
  2. 与上月快照 diff，统计本月【新增纳入项目】按信源分布（快照存 monitor/snapshot_YYYY-MM.json）
  3. 把结果追加到 补充信源清单.md 的「产出日志」末尾
  4. 告警：S/A 级信源本月零产出时提示复核分层（升降级裁决由月度复盘执行）
  5. 同时输出指纹监测器 hits/runs 命中率统计（来自 monitor/source_fingerprints.json）
"""
import json, re, os, sys
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bidding-daily/
INDEX_HTML = os.path.join(BASE, 'index.html')
SOURCES_MD = os.path.join(BASE, '补充信源清单.md')
FP_PATH = os.path.join(BASE, 'monitor', 'source_fingerprints.json')
SNAP_DIR = os.path.join(BASE, 'monitor')

# 分层清单（2026-09-01 初版，月度复盘按产出日志裁决升降级）
S_TIER = ['千里马招标网', '中招联合招标采购平台', '阳光采购服务平台', '移动支付网',
          '甘肃经济信息网', '宁波国际投资咨询', '银行科技研究社（公众号）', '微信公众号（智探AI应用）']
A_TIER = ['苏州农商官网', '黄河农商银行官网', '广西北部湾银行采购公告', '四川采购网',
          '九江银行招标采购', '中国招标投标公共服务平台', '湖南银行官网']
# 其余清单内来源默认 B 级（备查/定向核查）

DOMAIN_MAP = {
    'qianlima.com': '千里马招标网',
    '365trade.com.cn': '中招联合招标采购平台',
    'ygcgfw.com': '阳光采购服务平台',
    'mpaypass.com.cn': '移动支付网',
    'gsei.com.cn': '甘肃经济信息网',
    'nbgodo.com': '宁波国际投资咨询',
    'szrcb.com': '苏州农商官网',
    'bankyellowriver.com': '黄河农商银行官网',
    'bankofbbg.com': '广西北部湾银行采购公告',
    'sc.chinamae.com': '四川采购网',
    'jycbank.com': '九江银行招标采购',
    'ctbpsp.com': '中国招标投标公共服务平台',
    'hunan-bank.com': '湖南银行官网',
    'mp.weixin.qq.com': '微信公众号',
}


def norm_source(p):
    """项目 source 字段归一到信源名称；source 缺失时按 url 域名推断；
    带括号的变体（如 千里马招标网（天津银行招标公告））归并到主名"""
    s = (p.get('source') or '').strip()
    url = p.get('url') or ''
    # 2026-09-30：先过看板别名表（千里马订阅/（微信公众号）等），与写入口径单一
    try:
        import os, sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config import normalize_source
        s = normalize_source(s)
    except Exception:
        pass
    # 变体归并
    for main in ['千里马招标网', '宁波国际投资咨询']:
        if s.startswith(main):
            s = main
            break
    if s in ('', '用户搜索', 'web搜索', '(无)'):
        s = ''
    for dom, name in DOMAIN_MAP.items():
        if dom in url:
            # 微信公众号进一步细分
            if name == '微信公众号' and '银行科技研究社' in s:
                return '银行科技研究社（公众号）'
            if name == '微信公众号' and '智探' in s:
                return '微信公众号（智探AI应用）'
            return name if not s else s
    return s or '(未知)'


def load_projects():
    html = open(INDEX_HTML, encoding='utf-8').read()
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
    if not m:
        m = re.search(r'<script type=application/json id=tender-data>(.*?)</script>', html, re.S)
    data = json.loads(m.group(1))
    return data.get('version', '?'), data.get('projects', [])


def pkey(p):
    return f"{p.get('company','')}|{(p.get('project') or '')[:20]}"


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m')
    ver, projects = load_projects()
    cur = {pkey(p): p for p in projects}

    # 与上月快照 diff 得到本月新增
    snaps = sorted(f for f in os.listdir(SNAP_DIR) if f.startswith('snapshot_'))
    prev = {}
    if snaps:
        prev = {pkey(p): p for p in json.load(open(os.path.join(SNAP_DIR, snaps[-1]), encoding='utf-8'))}
    added = [p for k, p in cur.items() if k not in prev]

    # 保存本月快照
    snap_path = os.path.join(SNAP_DIR, f'snapshot_{label}.json')
    json.dump(projects, open(snap_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    n = len(projects)
    all_src = Counter(norm_source(p) for p in projects)
    add_src = Counter(norm_source(p) for p in added)
    all_str = '、'.join(f'{k} {v}（{v/n*100:.1f}%）' for k, v in all_src.most_common())
    add_str = '、'.join(f'{k} {v}' for k, v in add_src.most_common()) or '无新增'

    # 指纹监测器命中率
    fp_note = ''
    if os.path.exists(FP_PATH):
        fp = json.load(open(FP_PATH, encoding='utf-8'))
        parts = [f"{k} 命中{v.get('hits',0)}/{v.get('runs',0)}次[{v.get('last_status','?')}]"
                 for k, v in fp.items()]
        fp_note = '\n- 指纹监测器：' + '；'.join(parts)

    entry = (f"\n### {label} 月（看板 {ver}，在板 {n} 项，本月新增纳入 {len(added)} 项）\n"
             f"- 在板项目信源分布：{all_str}\n"
             f"- 本月新增纳入信源分布：{add_str}{fp_note}\n")

    md = open(SOURCES_MD, encoding='utf-8').read()
    if f'### {label} 月' in md:
        print(f'⚠️ {label} 已记账，跳过重复追加（仅刷新快照）')
    else:
        if '## 产出日志' not in md:
            open(SOURCES_MD, 'a', encoding='utf-8').write(
                '\n---\n\n## 产出日志（tools/source_stats.py 每月1日复盘时自动追加）\n')
        open(SOURCES_MD, 'a', encoding='utf-8').write(entry)
        print(f'✅ 已追加产出日志到 补充信源清单.md')

    # 零产出告警（按本月新增 + 在板双重口径）
    text = ' '.join(list(all_src.keys()) + list(add_src.keys()))
    zero_s = [s for s in S_TIER if s not in text and s != '千里马招标网']
    zero_a = [s for s in A_TIER if s not in text]
    if zero_s:
        print(f'⚠️ S级零产出（月度复盘需裁决是否降级）: {", ".join(zero_s)}')
    if zero_a:
        print(f'ℹ️ A级本月零产出（连续两月即降级B）: {", ".join(zero_a)}')
    print(f'在板 {n} 项（{ver}），本月新增 {len(added)} 项')
    print(f'新增分布: {add_str}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
