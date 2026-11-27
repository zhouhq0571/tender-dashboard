#!/usr/bin/env python3
"""decide.html 手机视口回归：核验 11-27 上午三项手机端修复在门禁重构后仍然成立。"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
URL = "file://" + str(BIDDING / "decide.html")
PWD = (BIDDING / ".decide_pwd").read_text().strip()
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 390, "height": 844},   # iPhone 14 Pro 竖屏
                              user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                              is_mobile=True, has_touch=True, device_scale_factor=3)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL)
    page.fill("#gName", "周老师")
    page.fill("#gPwd", PWD)
    page.click("#gLogin")
    page.wait_for_timeout(1500)
    assert page.locator("#app").is_visible(), "登录后 app 未显示"

    # ① 列冻结：项目列（sticky）在横向滚动后仍可见
    tbl = page.locator("table").first
    sticky_css = tbl.locator("th, td").first.evaluate(
        "el => getComputedStyle(el).position")
    assert sticky_css == "sticky", f"① 首列未冻结（position={sticky_css}）"
    tbl.evaluate("el => el.parentElement.scrollLeft = 600")
    page.wait_for_timeout(300)
    first_cell_text = tbl.locator("td").first.inner_text()
    assert first_cell_text.strip(), "① 滚动后首列内容不可见"
    print("① 项目列冻结：滚动后首列仍可见 ✓（", first_cell_text.strip()[:16], "…）")

    # ② 表格最小宽度 880px（横向滚动前提）：滚动容器内部可横向滚动
    tbl_html = tbl.inner_html()
    cont = page.evaluate("""() => {
      let el = document.querySelector('table');
      while (el && el !== document.body) {
        const o = getComputedStyle(el).overflowX;
        if (o === 'auto' || o === 'scroll') return {sw: el.scrollWidth, cw: el.clientWidth};
        el = el.parentElement;
      }
      return null;
    }""")
    assert cont and cont["sw"] > cont["cw"], f"② 滚动容器无横向溢出：{cont}"
    print(f"② 横向滚动可用：容器 scrollWidth={cont['sw']}px > clientWidth={cont['cw']}px ✓")

    # ③ 横屏决策按钮存在且点击不报错（headless 下 fullscreen/orientation.lock 可能不可用，代码应静默回落）
    btn = page.locator("#rot")
    assert btn.count() > 0, "③ 未找到「横屏决策」按钮"
    btn.click()
    page.wait_for_timeout(800)
    print("③ 「🔄 横屏决策」按钮点击无异常 ✓（headless 下 fullscreen/lock 回落属预期）")

    # ④ 竖屏下页面无坏溢出：文档宽度不超视口（容器内滚动，文档不横向滚动）
    doc_w = page.evaluate("document.documentElement.scrollWidth")
    vp_w = page.evaluate("document.documentElement.clientWidth")
    assert doc_w <= vp_w + 1, f"④ 文档级坏溢出：scrollWidth={doc_w} > {vp_w}"
    print(f"④ 竖屏布局：文档宽度 {doc_w}px = 视口 {vp_w}px，无坏溢出 ✓")

    browser.close()

assert not errors, f"JS 运行时错误: {errors}"
print("⑤ pageerror=0 ✓")
print("ALL PASS (mobile viewport)")
