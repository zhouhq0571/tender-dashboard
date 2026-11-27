#!/usr/bin/env python3
"""decide.html 免密跨部署回归测试（11-27 blob v2 确定性 DEK）。"""
import sys, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
URL = "file://" + str(BIDDING / "decide.html")
PWD = (BIDDING / ".decide_pwd").read_text().strip()
WRONG = PWD + "x"

errors = []

def open_page(ctx):
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL)
    return page

def app_visible(page):
    return page.locator("#app").is_visible(timeout=8000)

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context()

    # ① 冷启动必须见密码框 → 正确密码登录 → app 显示
    page = open_page(ctx)
    assert page.locator("#gPwd").is_visible(), "① 冷启动未见密码框"
    page.fill("#gName", "周老师")
    page.fill("#gPwd", PWD)
    page.click("#gLogin")
    page.wait_for_timeout(1500)
    try:
        assert app_visible(page), "① 正确密码登录后 app 未显示"
    except AssertionError:
        print("gErr:", page.locator("#gErr").inner_text() if page.locator("#gErr").count() else "(无)")
        print("pageerrors:", errors)
        print("grace:", page.evaluate("localStorage.getItem('decide_gate_grace_v1')"))
        raise
    print("① 正确密码登录 → app 显示 ✓")

    # ② 同 context 新页重载 → 免密直进
    page2 = open_page(ctx)
    assert app_visible(page2), "② 30 分钟免密未直进"
    print("② 同会话重载 → 免密直进 ✓")
    page2.close(); page.close()

    # ③ 模拟重部署：重建（新 iv/新 blob），同 context 再重载 → 必须仍然免密（本 bug 回归测试）
    r = subprocess.run([sys.executable, str(BIDDING / "build_decide_page.py")],
                       capture_output=True, text=True, check=True)
    assert "GATED" in r.stdout
    page3 = open_page(ctx)
    assert app_visible(page3), "③ 重部署后免密失效（回归）"
    print("③ 重建（重部署）后同会话重载 → 免密仍直进 ✓")
    page3.close()

    # ④ 负例：错误密码必须被拒；且不得污染免密钥匙
    page4 = open_page(ctx)
    ctx.clear_cookies()
    page4.goto(URL)
    page4.evaluate("localStorage.removeItem('decide_gate_grace_v1')")
    page4.reload()
    page4.fill("#gName", "周老师")
    page4.fill("#gPwd", WRONG)
    page4.click("#gLogin")
    page4.wait_for_timeout(500)
    assert page4.locator("#gPwd").is_visible(), "④ 错误密码未被拒"
    assert "不正确" in page4.locator("#gErr").inner_text(), "④ 未提示密码错误"
    print("④ 错误密码 → 拒绝并提示 ✓")
    page4.close()
    browser.close()

assert not errors, f"JS 运行时错误: {errors}"
print("⑤ pageerror=0 ✓")
print("ALL PASS")
