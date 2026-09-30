# -*- coding: utf-8 -*-
"""招标看板补偿守门条件：仅当「工作日 09:30-12:00 且本地看板日期不是今天」时才唤醒补偿 agent。

其余时间（含看板已更新的正常日子）返回 False，零 agent token。
"""
import re
from datetime import datetime
from pathlib import Path

INDEX_HTML = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html")


def should_fire(ctx):
    now = datetime.now()  # 运行环境时区为 Asia/Shanghai
    if now.weekday() >= 5:  # 周六日不补偿
        return False
    minutes = now.hour * 60 + now.minute
    if not (9 * 60 + 30 <= minutes < 12 * 60):  # 只在 09:30~12:00 窗口内
        return False
    try:
        html = INDEX_HTML.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'"date"\s*:\s*"([^"]+)"', html)
        if not m:
            return True  # 读不到日期视为异常，放行让 agent 处理
        board_date = m.group(1).strip()
        today = {now.strftime("%Y-%m-%d"), now.strftime("%Y/%m/%d")}
        return board_date not in today
    except Exception:
        return True  # 文件异常时放行，由 agent 排查
