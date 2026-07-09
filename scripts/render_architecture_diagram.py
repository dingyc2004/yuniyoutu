from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_CN = ROOT / "docs" / "技术架构示意图.png"
OUT_ASCII = ROOT / "docs" / "yuni-architecture.png"

W, H = 1600, 900


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc") if bold else Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


F_TITLE = font(38, True)
F_SUB = font(16)
F_LAYER = font(22, True)
F_TAG = font(14, True)
F_PILL = font(15, True)
F_NOTE = font(13)
F_SIDE_TITLE = font(18, True)
F_SIDE = font(13)
F_SMALL = font(12)


def rounded(draw: ImageDraw.ImageDraw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill):
    x1, y1, x2, y2 = xy
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 1), text, font=fnt, fill=fill)


def pill(draw, x, y, w, h, label, strong=False):
    rounded(
        draw,
        (x, y, x + w, y + h),
        10,
        "#ffffff" if strong else "#fbfdff",
        "#7fa4bf" if strong else "#b7ccd9",
        2 if strong else 1,
    )
    text_center(draw, (x, y, x + w, y + h), label, F_PILL, "#2d5368")


def draw_arrow(draw, x1, y1, x2, y2, color="#54718a", width=3):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if y2 >= y1:
        pts = [(x2, y2), (x2 - 7, y2 - 12), (x2 + 7, y2 - 12)]
    else:
        pts = [(x2, y2), (x2 - 7, y2 + 12), (x2 + 7, y2 + 12)]
    draw.polygon(pts, fill=color)


def draw_layer(draw, x, y, w, h, title, tag_color, note, fill, pills):
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x + 4, y + 10, x + w + 4, y + h + 10), radius=18, fill=(32, 70, 90, 24))
    base.alpha_composite(shadow)
    rounded(draw, (x, y, x + w, y + h), 18, fill, "#7fa4bf", 2)
    rounded(draw, (x + 22, y + 24, x + 118, y + 56), 16, tag_color)
    text_center(draw, (x + 22, y + 24, x + 118, y + 56), title, F_TAG, "#ffffff")
    draw.text((x + 140, y + 31), note, font=F_NOTE, fill="#6a7d89")
    for item in pills:
        pill(draw, *item)


def side_card(draw, x, y, w, h, title, lines, fill="#ffffff", outline="#b9ccd8", warning=False):
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x + 4, y + 9, x + w + 4, y + h + 9), radius=18, fill=(32, 70, 90, 22))
    base.alpha_composite(shadow)
    rounded(draw, (x, y, x + w, y + h), 18, fill, outline, 2)
    draw.text((x + 26, y + 28), title, font=F_SIDE_TITLE, fill="#95621a" if warning else "#244c63")
    line_fill = "#7b623c" if warning else "#5d717d"
    for i, line in enumerate(lines):
        draw.text((x + 26, y + 68 + i * 27), line, font=F_SIDE, fill=line_fill)


base = Image.new("RGBA", (W, H), "#f6fbff")
draw = ImageDraw.Draw(base)

# Soft background blocks
for y in range(H):
    ratio = y / H
    r = int(245 + ratio * 8)
    g = int(251 - ratio * 3)
    b = int(255 - ratio * 15)
    draw.line((0, y, W, y), fill=(r, g, b, 255))
draw.ellipse((36, 20, 220, 204), fill=(223, 242, 255, 125))
draw.ellipse((1320, 20, 1476, 176), fill=(223, 244, 232, 110))
draw.ellipse((1320, 640, 1580, 900), fill=(255, 232, 189, 95))

draw.text((80, 50), "图3-3 鱼你有图技术架构示意图", font=F_TITLE, fill="#163b57")
draw.text(
    (80, 93),
    "当前实现版：移动端 Web Demo + FastAPI 接口 + 领域服务 + JSON 集合持久化，外接地图、天气与 AI 能力",
    font=F_SUB,
    fill="#6d7f8d",
)

draw_layer(
    draw,
    70,
    130,
    1120,
    142,
    "应用展示层",
    "#1f6f8b",
    "Vue3 + Vite + Element Plus，面向手机浏览器的产品 Demo",
    "#edf8ff",
    [
        (115, 205, 162, 38, "首页地图 / POI", True),
        (293, 205, 162, 38, "开竿记录", False),
        (471, 205, 162, 38, "社区发布", False),
        (649, 205, 162, 38, "教程学习", False),
        (827, 205, 162, 38, "活动装备", False),
        (1005, 205, 142, 38, "我的报告", False),
    ],
)

draw_layer(
    draw,
    70,
    315,
    1120,
    156,
    "API 接入层",
    "#26796e",
    "FastAPI app.main 统一挂载路由，CORS 配置，返回 data/meta 结构",
    "#edf9f5",
    [
        (115, 390, 184, 36, "records 记录", False),
        (315, 390, 184, 36, "posts/feed 社区", False),
        (515, 390, 184, 36, "poi/weather 地图", False),
        (715, 390, 184, 36, "events/groups 活动", False),
        (915, 390, 184, 36, "users/reports 用户", False),
        (215, 432, 184, 36, "tutorials 教程", False),
        (415, 432, 184, 36, "orders 装备订单", False),
        (615, 432, 184, 36, "community 社交", False),
        (815, 432, 184, 36, "recommend / ai", False),
    ],
)

draw_layer(
    draw,
    70,
    515,
    1120,
    156,
    "领域服务层",
    "#bf7a2a",
    "负责持久化、位置脱敏、统计报告、推荐逻辑和第三方接口适配",
    "#fff7e8",
    [
        (115, 590, 200, 36, "record_service", False),
        (331, 590, 200, 36, "post_service / 脱敏", False),
        (547, 590, 200, 36, "report_service", False),
        (763, 590, 200, 36, "poi / recommend", False),
        (979, 590, 168, 36, "user_service", False),
        (223, 632, 200, 36, "weather / amap", False),
        (439, 632, 200, 36, "events / orders", False),
        (655, 632, 200, 36, "chat / social", False),
        (871, 632, 200, 36, "learning_progress", False),
    ],
)

draw_layer(
    draw,
    70,
    715,
    1120,
    118,
    "数据持久层",
    "#6a5aa8",
    "根目录 data/*.json 模拟 NoSQL 集合，每个集合配套 *.schema.json 字段描述",
    "#f7f2ff",
    [
        (115, 790, 212, 34, "records / posts / users", False),
        (343, 790, 212, 34, "pois / weather / fish", False),
        (571, 790, 212, 34, "events / groups / messages", False),
        (799, 790, 212, 34, "comments / reactions / follows", False),
        (1027, 790, 120, 34, "orders", False),
    ],
)

draw_arrow(draw, 630, 273, 630, 312)
draw_arrow(draw, 630, 472, 630, 512)
draw_arrow(draw, 630, 672, 630, 712)

side_card(
    draw,
    1230,
    130,
    300,
    170,
    "外部与设备能力",
    ["• 高德 JS API / Web Service", "• 浏览器定位与地图选点", "• DeepSeek / AI 建议（可选）"],
)
side_card(
    draw,
    1230,
    332,
    300,
    166,
    "前端状态与降级",
    ["• API 超时后回退 seedData", "• localStorage 保存发布/收藏", "• 高德不可用时展示地图 Demo", "• 会员/非会员演示身份切换"],
)
side_card(
    draw,
    1230,
    530,
    300,
    138,
    "质量保障",
    ["• FastAPI TestClient / pytest", "• 覆盖记录 CRUD、报告、脱敏", "• 覆盖活动、教程进度、订单 Demo"],
)
side_card(
    draw,
    1230,
    700,
    300,
    132,
    "当前边界",
    ["未接入真实登录鉴权、对象存储、", "WebSocket、真实支付、后台审核；", "当前定位为可运行产品 Demo。"],
    fill="#fff2df",
    outline="#e3b874",
    warning=True,
)

draw.line((1190, 215, 1230, 215), fill="#86a4b8", width=2)
draw.polygon([(1230, 215), (1218, 208), (1218, 222)], fill="#86a4b8")
draw.line((1190, 415, 1230, 415), fill="#86a4b8", width=2)
draw.polygon([(1230, 415), (1218, 408), (1218, 422)], fill="#86a4b8")
draw.line((1190, 599, 1230, 599), fill="#86a4b8", width=2)
draw.polygon([(1230, 599), (1218, 592), (1218, 606)], fill="#86a4b8")
draw.line((1190, 766, 1230, 766), fill="#86a4b8", width=2)
draw.polygon([(1230, 766), (1218, 759), (1218, 773)], fill="#86a4b8")

footer = "说明：主链路为“移动端页面 → FastAPI 路由 → 领域服务 → JSON 集合”；地图、天气和 AI 属外部增强能力；支付、上传、鉴权和审核仍为后续正式化方向。"
draw.text((80, 862), footer, font=F_SMALL, fill="#607585")

rgb = Image.new("RGB", base.size, "#ffffff")
rgb.paste(base, mask=base.split()[3])
rgb.save(OUT_CN)
rgb.save(OUT_ASCII)
print(f"wrote {OUT_CN}")
print(f"wrote {OUT_ASCII}")
