# -*- coding: utf-8 -*-
"""恒生银信招标看板 每日数据海报 2026-07-19 (v105)"""
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 1400
DEEP = (15, 42, 74)      # #0f2a4a
DEEP2 = (23, 58, 99)
GOLD = (184, 134, 11)    # #b8860b
RED = (196, 30, 58)      # #c41e3a
WHITE = (255, 255, 255)
LIGHT = (210, 220, 232)
CARD = (255, 255, 255)
INK = (30, 40, 55)
GRAY = (110, 120, 135)

FB = "/Users/zhouhq/Library/Application Support/kimi-desktop/daimon-share/daimon/runtime/python/fonts/NotoSansCJKsc-Bold.otf"
FR = "/Users/zhouhq/Library/Application Support/kimi-desktop/daimon-share/daimon/runtime/python/fonts/NotoSansCJKsc-Regular.otf"
def fb(s): return ImageFont.truetype(FB, s)
def fr(s): return ImageFont.truetype(FR, s)

img = Image.new("RGB", (W, H), DEEP)
d = ImageDraw.Draw(img)

# 顶部标题区
d.rectangle([0, 0, W, 176], fill=DEEP)
d.rectangle([0, 176, W, 180], fill=GOLD)
d.text((50, 36), "恒生银信 · 招标资讯每日速递", font=fb(38), fill=WHITE)
d.text((50, 96), "银行 | 信托 | 理财子 · IT建设 / 信创 / 大模型 / 运维 / 人力外包", font=fr(19), fill=LIGHT)
d.text((50, 130), "2026年7月19日 星期六 · 看板版本 v105", font=fr(20), fill=GOLD)

# 三大核心指标
y0 = 198
metrics = [("55", "有效招标项目", GOLD), ("24", "建议投标项目", (240, 200, 90)), ("2", "今日截止项目", (255, 120, 130))]
bw, gap = 230, 25
x = 50
for num, label, color in metrics:
    d.rounded_rectangle([x, y0, x + bw, y0 + 132], radius=14, fill=DEEP2, outline=color, width=3)
    tw = d.textlength(num, font=fb(58))
    d.text((x + (bw - tw) / 2, y0 + 14), num, font=fb(58), fill=color)
    lw = d.textlength(label, font=fr(21))
    d.text((x + (bw - lw) / 2, y0 + 92), label, font=fr(21), fill=LIGHT)
    x += bw + gap

# 今日截止提醒
y1 = 352
d.rounded_rectangle([50, y1, 750, y1 + 114], radius=14, fill=(90, 22, 40), outline=RED, width=3)
d.text((75, y1 + 12), "今日截止（7月19日）· 2 个项目", font=fb(24), fill=(255, 210, 215))
d.text((75, y1 + 50), "· 华能信托  估值系统上交所新竞价新综业改造项目（建议投标）", font=fr(19), fill=WHITE)
d.text((75, y1 + 78), "· 华能信托  金证TA系统运维服务项目", font=fr(19), fill=WHITE)

# 重点项目推荐
y2 = 492
d.text((50, y2), "本周重点项目推荐", font=fb(28), fill=GOLD)
d.rectangle([50, y2 + 42, 126, y2 + 46], fill=GOLD)

cards = [
    ("光大理财", "投资交易系统2026年升级项目（三次招标）", "605.76万元", "7月24日截止"),
    ("浙商银行", "国产化资产托管系统建设及个性化功能迁移改造项目", "预算未披露", "7月24日截止"),
    ("山西信托", "客户关系管理系统（CRM）建设项目", "预算未披露", "7月28日截止"),
]
cy = y2 + 58
for comp, name, budget, ddl in cards:
    d.rounded_rectangle([50, cy, 750, cy + 136], radius=12, fill=CARD)
    d.rectangle([50, cy, 58, cy + 136], fill=GOLD)
    d.text((78, cy + 14), comp, font=fb(23), fill=DEEP)
    badge = "强烈建议投标"
    bw2 = d.textlength(badge, font=fb(17))
    d.rounded_rectangle([750 - 26 - bw2 - 22, cy + 16, 750 - 26, cy + 46], radius=8, fill=RED)
    d.text((750 - 26 - bw2 - 11, cy + 20), badge, font=fb(17), fill=WHITE)
    d.text((78, cy + 52), name, font=fr(21), fill=INK)
    d.text((78, cy + 92), f"预算：{budget}", font=fr(19), fill=GRAY)
    dw = d.textlength(ddl, font=fb(19))
    d.text((750 - 26 - dw, cy + 92), ddl, font=fb(19), fill=RED)
    cy += 148

# 临期提醒
y3 = cy + 13
d.rounded_rectangle([50, y3, 750, y3 + 96], radius=12, fill=DEEP2, outline=GOLD, width=2)
d.text((75, y3 + 8), "临近截止提醒", font=fb(22), fill=GOLD)
d.text((75, y3 + 42), "7月21日（后天）共 9 个项目截止：中信信托征信信创、外贸信托开放平台信创、", font=fr(18), fill=LIGHT)
d.text((75, y3 + 65), "四川农商大模型算力、徽商银行智能分析平台等，请提前安排投标文件。", font=fr(18), fill=LIGHT)

# 今日看板动态
y4 = y3 + 120
d.text((50, y4), "今日看板动态", font=fb(24), fill=GOLD)
items = [
    "· 删除已过期项目 3 个（光大理财估值核算、青银理财资产系统维护等）",
    "· 标记已截止 2 个（华能信托反洗钱维保、风控百融运维）",
    "· 清理冗余标签 7 处，修正采购方式 / 区域字段 3 处",
    "· 全网四阶段增量搜索完成，无新增候选项目",
]
iy = y4 + 38
for it in items:
    d.text((60, iy), it, font=fr(19), fill=LIGHT)
    iy += 30

# 底部
d.rectangle([0, H - 60, W, H], fill=(10, 30, 54))
t1 = "恒生电子 · 银行信托事业群"
w1 = d.textlength(t1, font=fr(19))
d.text(((W - w1) / 2, H - 44), t1, font=fr(19), fill=LIGHT)

img.save("/Users/zhouhq/Documents/kimi/workspace/tender_poster_20260719.png")
print("saved, bottom content y =", iy)
