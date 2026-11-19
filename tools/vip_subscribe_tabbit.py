#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vip_subscribe_tabbit.py — 千里马VIP订阅通道·真实浏览器版（2026-11-11 立规）

背景：headless 登录同账号高频触发滑块风控（Captcha 遮罩拦截一切交互）；周老师人工登录
实测正常。本通道改用 Tabbit 驱动的真实浏览器（自带登录态、真实指纹），滑块是唯一
需要人的一步——出现时桌面通知请周老师顺手滑一下（等待窗口内），其余全自动；
未过或超时则返回 captcha 状态，由 sweep 记录并回退 headless 冷备（自带断路器）。

用法: python3 vip_subscribe_tabbit.py [页数]
输出: monitor/subscribe_items_tabbit_<ts>.json + 一行状态（OK n / CAPTCHA / ERR ...）
"""
import json, os, subprocess, sys, time
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MON = os.path.join(BASE, 'monitor')
TABBIT = os.path.expanduser('~/.local/bin/tabbit-cli')
TASK = 'vip-subscribe'

JS_PROGRAM = r'''
const pages = parseInt(globalThis.__pages || '2');
globalThis.__user = 'chaxun032322';
globalThis.__pass = 'Chaxun!2026';
const out = {items: [], captcha: false, steps: []};
await page.goto('https://vip.qianlima.com/subscribe-center/subscribe-info', {waitUntil: 'domcontentloaded'});
await page.waitForTimeout(5000);
// captcha 检测（可见遮罩才算，DOM 常驻不算）
const capCheck = () => page.evaluate(() => {
  const c = document.querySelector('div.Captcha');
  if (!c) return false;
  const cs = getComputedStyle(c);
  return cs.display !== 'none' && cs.visibility !== 'hidden';
});
// 2026-11-13：VIP 会话约 24h 过期。自动破解登录流程易触发风控且维护成本高，
// 定案：检测到过期待人工一次点击登录（浏览器已打开订阅页，通常密码已存），
// python 侧桌面通知+120s 等待窗+重试一次；超时则跳过（其余8通道保底）。
const loggedOut = await page.evaluate(() => document.body.innerText.includes('登录状态超时') || document.body.innerText.includes('免费注册'));
if (loggedOut) { out.needLogin = true; return out; }
// 进入"银信标讯"订阅器
try {
  const clicked = await page.evaluate(() => {
    const els = [...document.querySelectorAll('div,span,li,a')].filter(
      e => e.childElementCount === 0 && e.textContent.trim() === '银信标讯');
    if (!els.length) return false;
    els[0].scrollIntoView();
    els[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));
    return true;
  });
  out.steps.push('click订阅器:' + clicked);
  await page.waitForTimeout(5000);
} catch (e) { out.steps.push('click订阅器失败:' + String(e).slice(0, 60)); }
if (await capCheck()) { out.captcha = true; return out; }
for (let pg = 1; pg <= pages; pg++) {
  const items = await page.evaluate(() => {
    const res = [];
    document.querySelectorAll('a[href*="bid-"]').forEach(a => {
      const t = (a.innerText || a.textContent || '').trim().replace(/\s+/g, ' ');
      if (t.length > 6) {
        const row = a.closest('li,tr,div[class*="item"],div[class*="list"]') || a.parentElement;
        res.push({title: t.slice(0, 90), url: a.href.split('?')[0],
                  row: (row ? row.innerText : '').replace(/\s+/g, ' ').slice(0, 200)});
      }
    });
    const seen = new Set();
    return res.filter(o => !seen.has(o.url) && seen.add(o.url));
  });
  items.forEach(it => it.page = pg);
  out.items.push(...items);
  out.steps.push('page' + pg + ':' + items.length);
  if (pg < pages) {
    try {
      const hasNext = await page.evaluate(() => {
        const b = document.querySelector('button.btn-next');
        if (!b || b.disabled) return false;
        b.dispatchEvent(new MouseEvent('click', {bubbles: true}));
        return true;
      });
      if (!hasNext) { out.steps.push('无下一页'); break; }
      await page.waitForTimeout(4000);
      if (await capCheck()) { out.captcha = true; break; }
    } catch (e) { out.steps.push('翻页失败:' + String(e).slice(0, 40)); break; }
  }
}
await page.close();
return out;
'''


def run_js(pages, timeout_s):
    req = f'run-{datetime.now():%H%M%S}'
    js = f"globalThis.__pages='{pages}';\n" + JS_PROGRAM
    try:
        r = subprocess.run([TABBIT, 'nodejs', '--task', TASK, '--request-id', req,
                            '--timeout-ms', str(timeout_s * 1000)],
                           input=js, capture_output=True, text=True, timeout=timeout_s + 30)
        if r.returncode != 0:
            return None, f'tabbit rc{r.returncode}: {(r.stderr or r.stdout)[-120:]}'
        line = (r.stdout or '').strip().splitlines()[-1]
        d = json.loads(line)
        res = d.get('result', {})
        val = res.get('value')
        if val is None and res.get('resourceId'):
            # 大结果走 resource 通道（tabbit inline 上限）
            rr = subprocess.run([TABBIT, 'resource', '--task', TASK,
                                 '--resource', res['resourceId'],
                                 '--offset', '0', '--max-bytes', '65536'],
                                capture_output=True, text=True, timeout=60)
            try:
                rd = json.loads((rr.stdout or '').strip().splitlines()[-1])
                val = rd.get('value') or rd.get('content') or rd
            except Exception:
                return None, f'resource read failed: {(rr.stdout or rr.stderr)[-100:]}'
        if isinstance(val, dict):
            return val, None
        if isinstance(val, str):
            try:
                val = json.loads(val)
                if isinstance(val, dict):
                    return val, None
            except Exception:
                pass
        return None, f'unexpected: {str(val)[:100]}'
    except subprocess.TimeoutExpired:
        return None, 'tabbit timeout'
    except Exception as e:
        return None, f'{type(e).__name__}: {str(e)[:100]}'


def main():
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    res, err = run_js(pages, 120)
    if err:
        print(f'ERR {err}')
        return 1
    if res.get('needLogin') or res.get('captcha'):
        what = '登录态过期，请点击浏览器完成一次登录' if res.get('needLogin') else '出现滑块，请滑动验证'
        subprocess.run(['osascript', '-e',
                        f'display notification "千里马VIP{what}（120秒内，浏览器已打开页面）" '
                        'with title "银信标讯看板" sound name "Glass"'],
                       check=False, timeout=10)
        time.sleep(120)
        res, err = run_js(pages, 150)
        if err:
            print(f'ERR {err}')
            return 1
        if res.get('needLogin') or res.get('captcha'):
            print('LOGIN_WINDOW 人工窗口超时，本通道跳过（其余8通道保底）')
            return 2
    items = res.get('items', [])
    # 复用 headless 版的分级判定
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ql_subscribe_fetch import classify
    kept = []
    dropped = []
    for it in items:
        classify(it)
        if it.get('verdict') == 'keep':
            kept.append(it)
        else:
            dropped.append({'title': it.get('title', '')[:60], 'verdict': it.get('verdict'), 'date': it.get('date', '')})
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out = os.path.join(MON, f'subscribe_items_tabbit_{run_at}.json')
    json.dump({'run_at': run_at, 'via': 'tabbit', 'steps': res.get('steps'),
               'total': len(items), 'keep': kept, 'dropped': dropped}, open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'OK {len(kept)}/{len(items)} -> {os.path.basename(out)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
