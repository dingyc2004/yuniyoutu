const C = {
  bg: "#F4F7F2",
  ink: "#10231F",
  muted: "#69766F",
  green: "#1F8A68",
  deepGreen: "#0E5A49",
  river: "#2C7BB6",
  riverDark: "#154B7A",
  orange: "#F2A541",
  paleGreen: "#E4F2EA",
  paleBlue: "#E4EEF6",
  cream: "#FFF9EE",
  white: "#FFFFFF",
  line: "#D8E2DA",
  dark: "#17342D",
};

function rect(ctx, slide, x, y, w, h, fill, line = "none", radius = "roundRect") {
  return ctx.addShape(slide, {
    x, y, w, h,
    geometry: radius,
    fill,
    line: line === "none" ? ctx.line("#00000000", 0) : ctx.line(line, 1),
  });
}

function text(ctx, slide, t, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: t,
    x, y, w, h,
    fontSize: opts.size ?? 24,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? "Microsoft YaHei",
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "#00000000",
    line: ctx.line("#00000000", 0),
    insets: opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
  });
}

function line(ctx, slide, x1, y1, x2, y2, color, width = 2) {
  const shape = ctx.addShape(slide, {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    w: Math.abs(x2 - x1) || width,
    h: Math.abs(y2 - y1) || width,
    geometry: "rect",
    fill: color,
    line: ctx.line("#00000000", 0),
  });
  return shape;
}

async function icon(ctx, slide, name, x, y, size, color = C.ink) {
  return ctx.addLucideIcon(slide, {
    icon: name,
    x, y, w: size, h: size,
    color,
    strokeWidth: 2.1,
  });
}

function pill(ctx, slide, label, x, y, w, color, fill) {
  rect(ctx, slide, x, y, w, 28, fill, "none");
  text(ctx, slide, label, x, y + 5, w, 16, { size: 13, color, bold: true, align: "center" });
}

function phoneFrame(ctx, slide, x, y, w, h, title, accent) {
  rect(ctx, slide, x - 12, y - 12, w + 24, h + 24, "#C8D6CD", "none", "roundRect");
  rect(ctx, slide, x, y, w, h, C.white, "#D9E4DD", "roundRect");
  rect(ctx, slide, x + 72, y + 12, w - 144, 8, "#C9D5CE", "none", "roundRect");
  text(ctx, slide, title, x + 26, y + 34, w - 52, 28, { size: 20, bold: true });
  rect(ctx, slide, x + 24, y + 70, w - 48, 3, accent, "none", "rect");
}

async function recordPhone(ctx, slide, x, y, w, h) {
  phoneFrame(ctx, slide, x, y, w, h, "记录", C.green);
  rect(ctx, slide, x + 24, y + 92, w - 48, 116, C.paleGreen, "none");
  text(ctx, slide, "本次垂钓计时", x + 42, y + 111, 150, 24, { size: 18, bold: true, color: C.deepGreen });
  text(ctx, slide, "01:46:32", x + 42, y + 141, 116, 30, { size: 25, bold: true, color: C.ink });
  rect(ctx, slide, x + w - 94, y + 119, 54, 54, C.green, "none");
  await icon(ctx, slide, "Timer", x + w - 78, y + 132, 22, C.white);
  text(ctx, slide, "结束", x + w - 89, y + 158, 44, 12, { size: 9, color: C.white, bold: true, align: "center" });

  const rows = [
    ["MapPin", "定位钓点", "东湖听涛野钓点"],
    ["CloudSun", "现场天气", "多云 24 C"],
    ["ImagePlus", "图文段落", "鱼情 / 水情 / 照片"],
  ];
  rows.forEach((r, i) => {
    const yy = y + 228 + i * 58;
    rect(ctx, slide, x + 24, yy, w - 48, 46, i === 1 ? "#F7FBF8" : "#FFFFFF", "#E1EAE3");
    icon(ctx, slide, r[0], x + 42, yy + 12, 22, C.green);
    text(ctx, slide, r[1], x + 76, yy + 9, 86, 15, { size: 12, color: C.muted });
    text(ctx, slide, r[2], x + 76, yy + 25, 170, 15, { size: 13, bold: true, color: C.ink });
  });

  rect(ctx, slide, x + 24, y + h - 108, w - 48, 72, C.cream, "#E6D8BD");
  text(ctx, slide, "收竿汇总", x + 42, y + h - 92, 82, 18, { size: 15, bold: true, color: "#8A5A12" });
  text(ctx, slide, "鱼获数量、重量、鱼种、钓法、饵料和备注统一保存为历史记录。", x + 42, y + h - 68, w - 84, 36, { size: 12, color: C.muted });
}

async function publishPhone(ctx, slide, x, y, w, h) {
  phoneFrame(ctx, slide, x, y, w, h, "发布", C.river);
  rect(ctx, slide, x + 24, y + 92, 124, 34, C.paleBlue, "none");
  rect(ctx, slide, x + 30, y + 98, 54, 22, C.river, "none");
  text(ctx, slide, "图文", x + 30, y + 103, 54, 11, { size: 11, color: C.white, bold: true, align: "center" });
  text(ctx, slide, "视频", x + 91, y + 103, 42, 11, { size: 11, color: C.riverDark, bold: true, align: "center" });

  rect(ctx, slide, x + 24, y + 144, w - 48, 86, "#DCEFF4", "none");
  await icon(ctx, slide, "Images", x + 44, y + 166, 28, C.river);
  text(ctx, slide, "3 张图片", x + 82, y + 158, 82, 16, { size: 12, color: C.riverDark, bold: true });
  text(ctx, slide, "今天这尾鲫鱼状态不错", x + 82, y + 179, w - 128, 24, { size: 17, bold: true, color: C.ink });

  rect(ctx, slide, x + 24, y + 250, w - 48, 90, C.white, "#D9E4DD");
  text(ctx, slide, "从记录快速填充", x + 42, y + 266, 130, 16, { size: 14, bold: true });
  pill(ctx, slide, "历史记录 4 条", x + w - 116, y + 260, 74, C.deepGreen, C.paleGreen);
  rect(ctx, slide, x + 42, y + 294, w - 84, 28, "#F4F8F5", "none");
  text(ctx, slide, "东湖听涛 · 鲫鱼 · 0.8斤", x + 54, y + 302, w - 108, 12, { size: 11, color: C.ink, bold: true });

  const fields = [
    ["标题", "东湖听涛的鲫鱼鱼获"],
    ["正文", "上午鱼口更稳，收竿前补了一尾..."],
    ["鱼获信息", "鲫鱼 / 28cm / 0.8斤"],
  ];
  fields.forEach((r, i) => {
    const yy = y + 358 + i * 35;
    text(ctx, slide, r[0], x + 28, yy, 62, 14, { size: 11, color: C.muted });
    rect(ctx, slide, x + 92, yy - 4, w - 116, 24, "#F8FAF8", "#E1E8E2");
    text(ctx, slide, r[1], x + 104, yy + 3, w - 140, 12, { size: 11, color: C.ink });
  });
  rect(ctx, slide, x + 92, y + h - 79, w - 116, 23, "#F8FAF8", "#E1E8E2");
  text(ctx, slide, "公开", x + 104, y + h - 73, w - 140, 10, { size: 10.5, color: C.ink });
  text(ctx, slide, "可见范围", x + 28, y + h - 75, 62, 14, { size: 10.5, color: C.muted });
  rect(ctx, slide, x + 62, y + h - 44, w - 124, 28, C.river, "none");
  text(ctx, slide, "发布到社区", x + 62, y + h - 37, w - 124, 12, { size: 12, color: C.white, bold: true, align: "center" });
}

async function flowNode(ctx, slide, x, y, iconName, title, note, color) {
  rect(ctx, slide, x, y, 176, 82, C.white, "#DCE5DE");
  rect(ctx, slide, x + 14, y + 17, 38, 38, color, "none");
  await icon(ctx, slide, iconName, x + 23, y + 26, 20, C.white);
  text(ctx, slide, title, x + 64, y + 18, 94, 18, { size: 15, bold: true });
  text(ctx, slide, note, x + 64, y + 42, 92, 26, { size: 11, color: C.muted });
}

export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();

  rect(ctx, slide, 0, 0, ctx.W, ctx.H, C.bg, "none", "rect");
  rect(ctx, slide, 0, 0, ctx.W, 720, "#EEF5F0", "none", "rect");
  rect(ctx, slide, 850, -60, 360, 160, "#DCEBF1", "none");
  rect(ctx, slide, 1040, 610, 260, 120, "#E9F1E4", "none");

  pill(ctx, slide, "鱼你有图 · 功能原型介绍", 56, 34, 170, C.deepGreen, C.paleGreen);
  text(ctx, slide, "记录沉淀钓程，发布激活社区", 56, 78, 520, 48, { size: 36, bold: true, color: C.ink });
  text(ctx, slide, "将一次垂钓从现场计时、定位、图文备注沉淀为个人历史记录，再一键转化为图文或短视频帖子，形成“个人复盘 + 社交分享”的内容闭环。", 58, 133, 720, 42, { size: 17, color: C.muted });

  await recordPhone(ctx, slide, 70, 218, 250, 430);
  await publishPhone(ctx, slide, 956, 218, 250, 430);

  text(ctx, slide, "记录页面", 82, 188, 150, 22, { size: 20, bold: true, color: C.deepGreen });
  text(ctx, slide, "把现场信息结构化保存", 176, 190, 170, 16, { size: 13, color: C.muted });
  text(ctx, slide, "社区发布", 968, 188, 150, 22, { size: 20, bold: true, color: C.riverDark });
  text(ctx, slide, "把记录转成可传播内容", 1062, 190, 170, 16, { size: 13, color: C.muted });

  line(ctx, slide, 354, 432, 909, 432, "#BFD1C5", 3);
  await flowNode(ctx, slide, 382, 316, "Timer", "1. 现场记录", "计时、定位、天气同步", C.green);
  await flowNode(ctx, slide, 552, 408, "NotebookPen", "2. 收竿汇总", "鱼获、钓法、照片说明", C.orange);
  await flowNode(ctx, slide, 724, 316, "Share2", "3. 一键发布", "复用记录生成帖子", C.river);
  await icon(ctx, slide, "ArrowRight", 521, 348, 26, C.muted);
  await icon(ctx, slide, "ArrowRight", 692, 440, 26, C.muted);

  rect(ctx, slide, 382, 536, 510, 112, C.dark, "none");
  text(ctx, slide, "核心功能价值", 406, 558, 138, 22, { size: 18, color: C.white, bold: true });
  const values = [
    ["降低记录成本", "自动带入时间、定位和天气，减少手动补录。"],
    ["保留复盘线索", "分段图文记录鱼情、水情、钓法和结果。"],
    ["促进社区生产", "从个人记录直接生成图文/视频帖子，提高分享意愿。"],
  ];
  values.forEach((v, i) => {
    const xx = 406 + i * 154;
    text(ctx, slide, v[0], xx, 591, 130, 16, { size: 13, color: "#AEE0C7", bold: true });
    text(ctx, slide, v[1], xx, 612, 132, 28, { size: 10.5, color: "#D9E7DF" });
  });

  text(ctx, slide, "首页承接：我的记录入口展示历史记录数量；社区承接：发布完成后进入推荐/同城信息流。", 58, 676, 820, 18, { size: 12, color: C.muted });
  text(ctx, slide, "Source: frontend/components/RecordView.vue, PublishView.vue, CommunityView.vue, HomeView.vue", 908, 676, 300, 18, { size: 9, color: "#8A958E", align: "right" });

  return slide;
}
