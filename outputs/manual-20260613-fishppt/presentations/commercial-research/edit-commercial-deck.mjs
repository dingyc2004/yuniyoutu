import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  ensureArtifactToolWorkspace,
  importArtifactTool,
} from "file:///C:/Users/Dingy/.codex/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/artifact_tool_utils.mjs";

const source = "D:/大学/空信试验班/6大三下/王少华/fishman_project_report_full.pptx";
const root = "D:/大学/空信试验班/6大三下/王少华/鱼你有图demo";
const outputDir = path.join(root, "output");
const previewDir = path.join(root, "outputs/manual-20260613-fishppt/presentations/commercial-research/final-preview");
const layoutDir = path.join(root, "outputs/manual-20260613-fishppt/presentations/commercial-research/final-layout");
const output = path.join(outputDir, "鱼你有图商业计划书.pptx");
process.env.HOME = "C:/Users/Dingy";
const workspace = path.dirname(fileURLToPath(import.meta.url));
await ensureArtifactToolWorkspace(workspace);
const { FileBlob, PresentationFile } = await importArtifactTool(workspace);

const replacements = {
  1: {
    "面向钓鱼爱好者的垂钓 GIS 社交平台": "面向中国钓鱼爱好者的可信垂钓 GIS 决策平台",
    "用地图解决“去哪钓、能不能钓、有没有鱼”，\n用社区解决晒成果、学经验、找同好。":
      "用可信空间决策回答“去哪钓、能不能钓、值不值得去”，\n用真实记录持续优化下一次出钓。",
    "地图找点": "可信找点",
    "精准发现附近钓点": "合规、风险与鱼情一图判断",
    "鱼情推荐": "解释推荐",
    "天气与规则辅助判断": "规则排序，AI 只负责解释",
    "鱼获沉淀": "数据闭环",
    "记录并反哺钓点": "鱼获与空军共同更新可信度",
    "GIS       ·       Community       ·       Recommendation":
      "Compliance GIS       ·       Trusted POI       ·       Data Flywheel"
  },
  2: {
    "市场背景：垂钓需求链路已经形成": "政策背景：鼓励户外消费，强化合规出钓",
    "市场不是“单点工具”，而是内容、位置、出行和分享交叉的完整链路":
      "政策形成双重机会：参与持续扩大，生态与安全规则持续细化",
    "2023 休闲渔业总产值": "2025 户外运动目标",
    "931.47": "3",
    "亿元": "万亿元",
    "2024 休闲渔业产值": "全民健身参与目标",
    "988.60": "38.5",
    "2023 接待人数": "2025 体育产业目标",
    "2.72": "5",
    "亿人次": "万亿元",
    "看内容": "参与增长",
    "找地点": "寻找水域",
    "出钓": "合规判断",
    "晒鱼获": "出钓消费",
    "年轻化": "参与扩大",
    "年轻用户与路亚人群增长": "户外运动与全民健身扩大需求",
    "内容化": "规则细化",
    "短视频、图文驱动出行决策": "禁钓、限钓与安全信息持续变化",
    "社区化": "数字服务",
    "兴趣互动提升留存与活跃": "把规则转为可执行空间决策",
    "市场机会：用户需求链路完整，但现有平台信息分散，缺少垂钓场景的一体化入口。":
      "政策机会：把分散规则、风险与鱼情转化为用户看得懂的空间决策服务。",
    "数据来源：中国休闲渔业发展监测报告（2024）等前期调研资料":
      "来源：中国政府网《户外运动产业发展规划》《全民健身计划》；均为到2025年政策目标"
  },
  3: {
    "用户痛点：出钓前后信息断裂": "问题提出：一次错误决策，浪费整次出钓",
    "基于钓鱼全流程，识别四个高频决策痛点": "钓鱼佬真正损失的不只是空军，更是时间、交通、装备与信任",
    "钓点信息分散，通用地图缺少垂钓语义": "爆点可能过时、收费变化或无法进入",
    "禁渔、限钓、现场规则难提前判断": "规则分散，到场才发现禁钓最挫败",
    "有没有鱼": "值不值得去",
    "鱼情判断依赖经验，天气和历史数据难整合": "数据很多，却缺少可解释的行动结论",
    "如何分享复盘": "如何真实复盘",
    "鱼获内容易流失，缺少可沉淀的数据结构": "鱼获被晒出，空军与风险往往被沉默",
    "核心问题：出钓前决策碎片化，出钓后内容难沉淀。":
      "核心问题：出钓前缺少可信决策，出钓后缺少可复用的正负反馈。"
  },
  4: {
    "竞品与机会：垂钓场景链路整合": "竞品与机会：功能不稀缺，可信决策稀缺",
    "现有平台各有优势，但都难以覆盖完整出钓闭环": "头部产品功能已经很全，我们聚焦最难建立信任的决策层",
    "通用地图": "通用地图",
    "有底图，缺少垂钓语义": "导航强，合规与鱼情语义弱",
    "垂直社区": "钓鱼社区",
    "有氛围，空间表达弱": "内容强，真实负反馈不足",
    "泛内容平台": "钓鱼天气类",
    "有流量，信息难沉淀": "指数强，规则来源解释有限",
    "单点工具": "鱼你有图",
    "查天气/轨迹强，链路不完整": "可信 POI + 正负反馈 + 隐私保护",
    "机会判断：不重造地图、不再做普通论坛，而是把“空间 + 内容 + 推荐”串成出钓决策入口。":
      "核心优势：合规安全是硬门槛，鱼获与空军共同更新钓点可信度。",
    "GIS": "合规",
    "社区": "反馈",
    "推荐": "可信"
  },
  5: {
    "证据链：问题、方法与当前结果一一对应": "市场验证：需求已被验证，细分机会仍待争夺",
    "把评委关心的“为什么可信”压缩成可验证矩阵": "用竞品公开自述与 MVP 证据证明需求，不虚构全国钓鱼人数",
    "问题": "需求信号",
    "方法": "公开证据 / 方法",
    "当前结果": "对鱼你有图的启示",
    "找钓点信息分散": "找点与导航是刚需",
    "垂钓语义 POI": "钓鱼人自述覆盖585城、73125家钓场/店",
    "POI 字段 / 首页卡片": "从“有点”升级为“可信决策点”",
    "天气鱼情靠经验": "精细鱼情判断有付费需求",
    "天气摘要 + 规则推荐": "钓鱼天气自述300万用户信赖",
    "适钓指数 / 推荐接口": "以可解释推荐承接会员价值",
    "禁钓风险难判断": "合规与安全影响信任",
    "合规字段优先提示": "规则来源、有效期与风险等级",
    "risk / is_banned / 扣分": "合规安全作为推荐硬门槛",
    "鱼获帖子难沉淀": "成功内容存在幸存者偏差",
    "结构化标签反哺 POI": "同步记录鱼获、空军与风险",
    "社区流 / 帖子详情": "用正负反馈更新可信度",
    "新手学习无路径": "武汉具备城市试点条件",
    "教程入口与场景联动": "高频水域 + 长江合规场景",
    "教程页 / mock 数据": "先验证单城市模型再复制",
    "原则：所有远景能力均标注边界，当前只强调已跑通的 MVP 证据。":
      "注：竞品数字来自 App Store 厂商公开自述，不作为第三方审计数据。"
  },
  6: {
    "创新过程：从想法到落地": "创新来源：从三个真实矛盾到可信 POI",
    "从真实需求出发，逐步收敛为可开发、可演示、可迭代的 MVP":
      "创新不是为了加 AI，而是解决隐私、合规与真实反馈之间的冲突",
    "想法产生": "分享与隐私",
    "从垂钓用户真实需求出发": "精确钓点默认私有，公开信息模糊化",
    "市场调研": "规则与决策",
    "分析行业规模与竞品格局": "规则转为来源、有效期与风险字段",
    "产品收敛": "晒鱼与真实",
    "从社区收敛为 GIS + 社区 + 推荐": "鱼获与空军共同进入反馈闭环",
    "功能设计": "可信 POI",
    "确定首页、POI、社区、记录模块": "空间、合规、鱼情、风险持续更新",
    "技术选型": "规则优先",
    "Vue + FastAPI + JSON mock + 接口预留": "后端规则排序，AI 只解释结论",
    "MVP 落地": "武汉试点",
    "完成页面、接口与核心闭环演示": "验证用户记录与可信决策价值",
    "后续迭代：数据增长 → 服务增长 → 商业增长": "创新飞轮：记录更完整 → POI 更可信 → 推荐更准确 → 留存与付费增长"
  },
  7: {
    "产品闭环：用数据驱动每一次出钓体验": "数据闭环：每一次出钓，都让下一次决策更准",
    "以 GIS 为入口，连接空间、内容与用户行为": "以可信 POI 为核心，连接规则、空间、记录与推荐",
    "定位：垂钓 GIS\n社交平台": "定位：可信垂钓 GIS\n决策平台",
    "空间入口：发现附近钓点": "可信入口：判断合规、风险与鱼情",
    "内容沉淀：记录经验与鱼获": "真实反馈：鱼获、空军与风险均记录",
    "推荐决策：数据驱动选择": "解释推荐：规则先排序，AI 后解释",
    "核心闭环\n驱动内容与数据双向增长": "可信 POI 闭环\n驱动决策与数据双向增长",
    "地图找点": "种子 POI",
    "天气/鱼情判断": "合规判断",
    "查看 POI 详情": "用户决策",
    "出钓记录": "鱼获/空军",
    "社区发布": "风险反馈",
    "数据反哺 POI": "可信度更新",
    "推荐优化": "推荐更准",
    "从空间发现开始，沉淀真实内容，反哺数据与推荐。":
      "增长不是单纯买量，而是在每个城市建立可复用的可信 POI 网络。"
  },
  8: {
    "首页：地图即首页的出钓决策入口": "具体实现：首页完成一次可信出钓决策",
    "从天气判断 → 地图找点 → 推荐解释 → 详情查看，一站式完成出钓决策":
      "从天气与规则 → 可信找点 → 推荐解释 → 详情确认，降低错误出钓成本",
    "天气判断": "天气与规则",
    "实时天气与适钓指数": "合规门槛 + 实时适钓判断",
    "附近钓点": "可信钓点",
    "专题 POI 地图快速找点": "按可信度与个体偏好发现钓点",
    "今日推荐": "解释推荐",
    "基于天气与时段智能推荐": "展示推荐理由与不推荐原因",
    "钓点详情": "行动确认",
    "查看热度、鱼情与钓友评价": "确认风险、规则、鱼情与路线",
    "天气判断": "规则判断",
    "地图找点": "可信找点",
    "推荐解释": "原因解释",
    "查看详情": "风险确认",
    "出钓决策": "做出决策"
  },
  9: {
    "地图与 POI：从“位置点”到“决策信息点”": "核心创新：可信 POI 是最小商业资产",
    "每个 POI 都承载鱼种、热度、风险、设施和近期鱼获等垂钓语义":
      "普通地图只有坐标；可信 POI 同时承载规则来源、有效期、正负反馈与风险",
    "POI 语义字段": "可信 POI 字段",
    "鱼种：鲫鱼 / 翘嘴 / 鳊鱼": "空间：坐标 / 入口 / 停车 / 岸线",
    "钓法：路亚 / 台钓": "合规：禁限钓 / 来源 / 有效期",
    "热度：近期鱼获与互动": "鱼情：近期鱼获 / 空军 / 适合钓法",
    "风险：禁钓 / 安全提示": "安全：岸线 / 夜钓 / 施工风险",
    "设施：停车 / 补给 / 步道": "可信度：更新时间 / 来源数 / 一致度",
    "天气：风力 / 湿度 / 气压": "环境：天气 / 风力 / 气压 / 水情",
    "不是地图上有点，而是每个点都具备可决策的垂钓语义。":
      "每一次记录，都在更新这个点；历史信息按时间衰减，避免旧爆点长期霸榜。"
  },
  10: {
    "社区：鱼获分享与钓点数据沉淀": "真实反馈：鱼获与空军共同修正钓点画像",
    "帖子不是终点，而是钓点画像和推荐优化的数据入口":
      "社区不只晒成果，更要沉淀失败、风险与规则变化，减少幸存者偏差",
    "帖子详情": "反馈详情",
    "鱼获帖子": "鱼获与空军",
    "图文/视频记录真实鱼获": "成功与失败都形成结构化记录",
    "同城话题": "规则纠错",
    "基于位置聚合同城经验": "社区反馈触发复核，不直接覆盖规则",
    "结构化标签": "时间衰减",
    "鱼种、钓法、时间、天气统一沉淀": "旧信息逐步降权，保持钓点时效",
    "互动关注": "隐私保护",
    "点赞、评论、收藏增强活跃": "精确钓点私有，公开数据聚合化",
    "发布鱼获": "记录鱼获",
    "社区互动": "记录空军",
    "结构化标签": "风险纠错",
    "反哺推荐": "更新可信度",
    "钓点体验": "推荐优化"
  },
  11: {
    "核心功能：补全出钓全流程": "个人主页：沉淀可复用的私人出钓数据资产",
    "首页解决决策，社区沉淀内容，其他模块补全记录、学习和个人资产":
      "用户获得越来越懂自己的出钓助手，平台获得更完整、更可信的正负反馈数据",
    "发布页": "记录沉淀",
    "鱼获 / 空军 / 探点记录": "鱼获、空军、钓点与天气自动归档",
    "图片、鱼种、钓法、位置、隐私": "精确钓点默认私有，可选择模糊分享",
    "记录页": "偏好分析",
    "出钓过程结构化保存": "识别最佳时段、温度、钓法与鱼种",
    "开竿计时、图文板块、收竿汇总": "总出钓、总重量、高频钓点与热力图",
    "教程页": "推荐优化",
    "新手学习路径入口": "个人历史持续提升下一次推荐",
    "鱼种、钓法、装备、场景教程": "明天去哪、几点去、用什么方法",
    "我的页": "会员转化",
    "个人战绩与资产沉淀": "专属报告、规则提醒与私密钓点管理",
    "收藏钓点、我的发布、月度报告": "形成记录习惯与长期迁移成本",
    "闭环补全：发布沉淀内容，记录沉淀过程，教程降低门槛，我的页形成长期资产。":
      "商业意义：记录沉淀提高留存，个人分析、会员报告与规则提醒提供付费理由。"
  },
  12: {
    "技术架构与推荐机制：可控规则优先": "可信机制：合规安全硬门槛，规则排序优先",
    "前端展示、后端规则与 mock 数据共同支撑 MVP 演示":
      "推荐不是黑盒指数：先校验规则与风险，再综合反馈、天气、距离和偏好",
    "推荐分解样例": "推荐分解建议",
    "鱼情分": "合规安全",
    "88": "30%",
    "合规分": "近期反馈",
    "91": "25%",
    "距离分": "天气适配",
    "2.4km": "20%",
    "天气分": "距离便利",
    "风力2级": "15%",
    "设施分": "个体偏好",
    "72": "10%",
    "社交热度": "禁钓命中",
    "78": "不推荐",
    "规则排序在后端，AI 只负责解释与摘要": "合规安全为硬门槛；历史反馈按时间衰减；AI 只解释，不修改排序",
    "系统设计原则：推荐排序由后端规则模型控制，避免大模型直接决定合规与安全判断。":
      "信任护栏：规则保留来源与有效期，社区反馈只能触发复核，不能直接覆盖官方规则。"
  },
  13: {
    "当前成果：完成可演示 MVP，边界清晰": "商业逻辑：以可信决策获得付费，以空间数据扩张",
    "用完成度矩阵说明已完成、部分完成和后续迭代，避免夸大":
      "商业化顺序保护推荐可信度：会员优先，商户其次，匿名化数据服务长期扩张",
    "已完成": "C 端会员",
    "首页 / 地图 / POI 详情": "基础会员 68 元/年",
    "社区流 / 帖子详情": "进阶会员 128 元/年",
    "发布 / 记录 / 教程 / 我的": "个人分析、会员报告",
    "FastAPI 核心接口": "规则提醒、私密钓点",
    "JSON mock 数据与规则推荐": "基础情景：245 万元/年",
    "部分完成": "商户服务",
    "高德地图配置与加载": "认证主页与预约导流",
    "天气服务封装": "活动发布与经营看板",
    "AI 解释接口": "按年服务费或有效预约佣金",
    "前端发布到社区流": "300 家 × 6000 元/年",
    "记录进程内保存": "基础情景：180 万元/年",
    "后续迭代": "数据服务",
    "正式数据库与账号系统": "匿名化热度与风险报告",
    "真实互动关系": "规则触达与活动效果分析",
    "禁渔区数据合作": "面向景区、水域管理与协会",
    "用户新增 POI 审核": "5 个项目 × 20 万元/年",
    "会员 / 商户系统": "基础情景：100 万元/年",
    "接口证据建议：/api/pois  ·  /api/feed  ·  /api/recommendations":
      "基础情景合计：50万MAU × 5%付费率 × 98元 + 商户服务 + 数据项目 = 525万元/年",
    "说明：当前以 mock 数据支撑演示，不等同于正式上线系统。":
      "注：以上为经营情景测算，不是已实现收入；付费推广不得改变合规与安全排序。"
  },
  14: {
    "迭代远景：从 MVP 到垂钓空间数据服务": "增长路径：从武汉试点到城市级垂钓空间服务",
    "先沉淀数据，再扩展服务，最终形成可持续的休闲渔业数字化入口。":
      "不靠单纯买量，而是在每个城市建立可复用、可持续更新的可信 POI 网络",
    "数据增长": "武汉 MVP",
    "用户新增 POI、纠错、鱼获热力、空军负样本": "整理30—50个高频水域，验证可信决策与空军记录价值",
    "服务增长": "城市复制",
    "同城话题、收藏提醒、推荐优化、个人复盘": "复制 POI 标准、规则采集流程与本地种子运营",
    "商业增长": "空间服务",
    "会员报告、钓场主页、预约与榜单": "会员、商户服务与匿名化管理洞察形成收入组合",
    "鱼你有图把一次垂钓出行从找点、判断、记录到分享，沉淀成可复用的空间数据闭环。":
      "每一次出钓都沉淀为可服务用户、商户与管理方的可信空间数据。",
    "当前版本是 MVP：已跑通产品闭环、页面结构、后端接口、推荐规则与 mock 数据。":
      "阶段目标：先验证单城市留存与付费，再沿长江经济带城市复制。"
  }
};

function replaceTextOnSlide(slide, slideNumber, mapping) {
  const report = [];
  for (const element of slide.elements.items) {
    if (!element.text || typeof element.toSnapshot !== "function") continue;
    const current = element.toSnapshot().text;
    if (!current || !Object.prototype.hasOwnProperty.call(mapping, current)) continue;
    const next = mapping[current];
    element.text.set(next);
    report.push({ slide: slideNumber, id: element.id, from: current, to: next });
  }
  return report;
}

function replaceByAid(slide, slideNumber, aid, next, report) {
  const element = slide.elements.items.find((item) => item.toSnapshot?.().aid === aid);
  if (!element?.text) return;
  const current = element.toSnapshot().text;
  if (current === next) return;
  element.text.set(next);
  report.push({ slide: slideNumber, id: element.id, aid, from: current, to: next });
}

function replaceByPrefix(slide, slideNumber, prefix, next, report) {
  const element = slide.elements.items.find((item) => item.toSnapshot?.().text?.startsWith(prefix));
  if (!element?.text) return;
  const current = element.toSnapshot().text;
  if (current === next) return;
  element.text.set(next);
  report.push({ slide: slideNumber, id: element.id, from: current, to: next });
}

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(layoutDir, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const edits = [];
for (let i = 0; i < presentation.slides.count; i += 1) {
  const slide = presentation.slides.getItem(i);
  edits.push(...replaceTextOnSlide(slide, i + 1, replacements[i + 1] || {}));
  if (i + 1 === 1) {
    replaceByAid(
      slide,
      1,
      "sh/36hcrmhk",
      "用可信空间决策回答“去哪钓、能不能钓、值不值得去”，\n用真实记录持续优化下一次出钓。",
      edits,
    );
  }
  if (i + 1 === 2) {
    replaceByAid(slide, 2, "sh/3itgfmlk", "万亿", edits);
    replaceByAid(slide, 2, "sh/eloj2t83", "%", edits);
    replaceByAid(slide, 2, "sh/w7mp0bi9", "万亿", edits);
  }
  if (i + 1 === 7) {
    replaceByAid(slide, 7, "sh/hoza1gvy", "定位：可信垂钓 GIS\n决策平台", edits);
  }
}

for (let i = 0; i < presentation.slides.count; i += 1) {
  const slide = presentation.slides.getItem(i);
  const num = String(i + 1).padStart(2, "0");
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(previewDir, `slide-${num}.png`), Buffer.from(await png.arrayBuffer()));
  const layout = await presentation.export({ slide, format: "layout" });
  await fs.writeFile(path.join(layoutDir, `slide-${num}.layout.json`), await layout.text(), "utf8");
}

const exported = await PresentationFile.exportPptx(presentation);
await exported.save(output);
await fs.writeFile(
  path.join(root, "outputs/manual-20260613-fishppt/presentations/commercial-research/edit-report.json"),
  JSON.stringify({ output, editCount: edits.length, edits }, null, 2),
  "utf8",
);
console.log(JSON.stringify({ output, editCount: edits.length, slideCount: presentation.slides.count }, null, 2));
