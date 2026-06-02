const fs = require("fs");
const path = require("path");
const http = require("http");
const { URL } = require("url");

const PORT = Number(process.env.PORT || 3001);
const AMAP_BASE = "https://restapi.amap.com";
const AMAP_KEY_PATH = path.join(__dirname, "..", "高德key.txt");

const seedData = {
  pois: [
    {
      id: "poi_001",
      name: "东湖听涛野钓点",
      type: "野钓",
      distance: "2.4km",
      score: 89,
      fish: ["鲫鱼", "翘嘴", "鳊鱼"],
      tags: ["免费", "近7天有鱼获", "适合台钓"],
      reason: "近 7 天有 18 条鱼获，风力 2 级，上午窗口较好。",
      risk: "部分岸线较滑，夜钓需结伴。",
      x: 66,
      y: 38
    },
    {
      id: "poi_002",
      name: "青山江滩路亚点",
      type: "野钓",
      distance: "6.8km",
      score: 82,
      fish: ["翘嘴", "鳜鱼"],
      tags: ["路亚", "停车方便", "晚口较好"],
      reason: "缓流区近期翘嘴活跃，傍晚更适合搜索。",
      risk: "临水护栏低，注意安全。",
      x: 28,
      y: 55
    },
    {
      id: "poi_003",
      name: "南湖练竿塘",
      type: "钓场",
      distance: "9.1km",
      score: 76,
      fish: ["鲫鱼", "鲤鱼", "草鱼"],
      tags: ["收费", "新手友好", "可夜钓"],
      reason: "设施完整，适合新手练习调漂和抛竿。",
      risk: "周末人多，建议提前预约。",
      x: 74,
      y: 72
    }
  ],
  weather: {
    source: "seed",
    live: {
      city: "武汉市",
      adcode: "420100",
      weather: "晴",
      temperature: "26",
      winddirection: "东南风",
      windpower: "2",
      humidity: "58",
      reporttime: new Date().toISOString()
    },
    forecast: [
      { date: "今天", dayweather: "晴", nightweather: "多云", daytemp: "29", nighttemp: "22", daywind: "东南风", daypower: "2" },
      { date: "明天", dayweather: "多云", nightweather: "阵雨", daytemp: "28", nighttemp: "23", daywind: "东风", daypower: "2" },
      { date: "后天", dayweather: "晴", nightweather: "晴", daytemp: "30", nighttemp: "24", daywind: "东南风", daypower: "2" }
    ]
  },
  feed: [
    {
      id: "post_001",
      format: "图文",
      author: "江风路亚",
      avatar: "J",
      title: "傍晚窗口 40 分钟，翘嘴连中 6 尾",
      excerpt: "青山江滩今天风小，亮片入水后第三竿就中。建议站在缓流边缘，收线不要太快。",
      meta: "青山江滩 · 路亚 · 亮片 · 24℃",
      tags: ["#路亚", "#翘嘴", "#武汉钓点"],
      likes: 128,
      comments: 36,
      saves: 42,
      coverTone: "blue"
    },
    {
      id: "post_002",
      format: "视频",
      author: "不空军的阿明",
      avatar: "A",
      title: "东湖早口鲫鱼不错，腥香拉饵更稳",
      excerpt: "这条视频记录了从找底、调漂到上鱼的完整流程，新手可以直接照着试一遍。",
      meta: "东湖听涛 · 台钓 · 鲫鱼 12 尾",
      tags: ["#台钓", "#新手", "#鲫鱼"],
      likes: 96,
      comments: 18,
      saves: 31,
      coverTone: "green"
    },
    {
      id: "post_003",
      format: "图文",
      author: "空军也要发",
      avatar: "K",
      title: "空军也值得发：今天不是没鱼，是选点错了",
      excerpt: "把这次空军记录下来，下一次就不会再犯同样的错。岸边太陡、风向不对、鱼口窗口太短。",
      meta: "南湖 · 复盘 · 空军记录",
      tags: ["#空军复盘", "#选点", "#经验"],
      likes: 74,
      comments: 24,
      saves: 19,
      coverTone: "amber"
    },
    {
      id: "post_004",
      format: "视频",
      author: "钓场探路官",
      avatar: "T",
      title: "新手第一条鱼：看调漂和抄网配合就够了",
      excerpt: "这条短视频把入门最容易卡住的两个动作拆开讲，适合第一次带装备出门的人。",
      meta: "南湖练竿塘 · 入门视频",
      tags: ["#教程", "#视频", "#入门"],
      likes: 211,
      comments: 51,
      saves: 88,
      coverTone: "purple"
    }
  ],
  tutorials: [
    {
      id: "t_001",
      type: "图文",
      title: "新手第一天：怎么判断一个点能不能钓",
      level: "入门",
      duration: "6 分钟",
      summary: "从禁钓规则、岸线安全、鱼获热度和停车补给四个维度判断。",
      tags: ["#新手", "#合规", "#找点"],
      coverTone: "blue"
    },
    {
      id: "t_002",
      type: "视频",
      title: "路亚翘嘴：清晨和傍晚怎么选标点",
      level: "进阶",
      duration: "9 分钟",
      summary: "看风向、缓流、明暗交界和小鱼活动，优先搜索水面窗口。",
      tags: ["#路亚", "#翘嘴", "#实战"],
      coverTone: "green"
    },
    {
      id: "t_003",
      type: "图文",
      title: "台钓调漂最小闭环",
      level: "入门",
      duration: "8 分钟",
      summary: "用一套简单步骤完成找底、调目、钓目和复盘。",
      tags: ["#台钓", "#调漂", "#图文"],
      coverTone: "amber"
    },
    {
      id: "t_004",
      type: "视频",
      title: "夜钓出门前要准备什么",
      level: "安全",
      duration: "5 分钟",
      summary: "照明、防滑、救生、补给和回程路线一次讲清。",
      tags: ["#夜钓", "#安全", "#装备"],
      coverTone: "purple"
    }
  ]
};

const amapKey = readAmapKey();

function readAmapKey() {
  if (process.env.AMAP_KEY) return process.env.AMAP_KEY.trim();
  try {
    return fs.readFileSync(AMAP_KEY_PATH, "utf8").trim();
  } catch {
    return "";
  }
}

function sendJson(res, status, payload) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
  });
  res.end(JSON.stringify(payload));
}

function readBody(req) {
  return new Promise((resolve) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch {
        resolve({});
      }
    });
  });
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function parseNumber(value, fallback) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function buildUrl(base, pathname, params) {
  const url = new URL(pathname, base);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url;
}

async function amapGet(pathname, params) {
  if (!amapKey) throw new Error("missing key");
  const url = buildUrl(AMAP_BASE, pathname, { ...params, key: amapKey, output: "JSON" });
  const response = await fetch(url);
  const json = await response.json();
  if (!response.ok) throw new Error(`http ${response.status}`);
  if (json.status === "0") throw new Error(json.info || "amap error");
  return json;
}

function mapPoiType(name = "", typecode = "") {
  const text = `${name} ${typecode}`.toLowerCase();
  if (/(渔具|鱼具|饵料|鱼饵)/.test(text)) return "渔具店";
  if (/(码头|防波堤|海边|海钓|港口|礁)/.test(text)) return "海钓";
  if (/(塘|场|池|黑坑)/.test(text)) return "钓场";
  if (/(河|湖|库|江|溪|湾|滩)/.test(text)) return "野钓";
  return "钓点";
}

function synthesizePoi(poi, index) {
  const [lng = 0, lat = 0] = String(poi.location || "0,0").split(",").map((value) => Number(value));
  const x = clamp(15 + ((lng * 1000) % 70), 12, 88);
  const y = clamp(20 + ((lat * 1000) % 55), 12, 82);
  const score = clamp(70 + Math.round((poi.distance ? Math.max(0, 40 - Number(poi.distance) / 100) : 12)) - index * 2, 54, 98);
  return {
    id: poi.id || `amap_${index}`,
    name: poi.name || "未命名钓点",
    type: mapPoiType(poi.name, poi.typecode || poi.type),
    distance: poi.distance ? `${Math.round(Number(poi.distance) / 100) / 10}km` : `${Math.max(1, index + 1)}km`,
    score,
    fish: ["鲫鱼", "翘嘴", "鲤鱼"].slice(0, 2 + (index % 2)),
    tags: [
      poi.address ? "高德POI" : "平台整理",
      poi.distance ? `距您 ${Math.round(Number(poi.distance))}m` : "附近可达",
      "待补充鱼情"
    ],
    reason: poi.address ? `来自高德 POI，地址：${poi.address}` : "来自高德检索结果，后续可叠加平台鱼情数据。",
    risk: "需结合现场规则、禁钓信息和实际水情判断。",
    x,
    y,
    address: poi.address || "",
    raw: poi
  };
}

async function fetchPois(query) {
  const lng = query.lng || query.longitude;
  const lat = query.lat || query.latitude;
  const keyword = query.keyword || query.keywords || "钓场|水库|鱼塘|河流|湖泊|码头|防波堤|渔具店";
  const radius = query.radius || 8000;

  try {
    if (lng && lat) {
      const json = await amapGet("/v5/place/around", {
        location: `${lng},${lat}`,
        radius,
        keywords: keyword,
        page_size: 8,
        page_num: 1
      });
      const items = json.pois?.poi || json.pois || json.data?.pois || [];
      if (Array.isArray(items) && items.length) {
        return { source: "amap", data: items.map(synthesizePoi) };
      }
    } else {
      const json = await amapGet("/v5/place/text", {
        keywords: keyword,
        city: query.city || "420100",
        page_size: 8,
        page_num: 1
      });
      const items = json.pois?.poi || json.pois || json.data?.pois || [];
      if (Array.isArray(items) && items.length) {
        return { source: "amap", data: items.map(synthesizePoi) };
      }
    }
  } catch (error) {
    console.error("AMap POI fetch failed:", error.message);
  }

  return { source: "seed", data: seedData.pois };
}

async function fetchWeather(query) {
  try {
    let city = query.city || "";
    if (!city && query.lng && query.lat) {
      const regeo = await amapGet("/v3/geocode/regeo", {
        location: `${query.lng},${query.lat}`,
        radius: 1000,
        extensions: "base"
      });
      city = regeo.regeocode?.addressComponent?.adcode || "";
    }
    if (!city) city = "420100";
    const json = await amapGet("/v3/weather/weatherInfo", {
      city,
      extensions: query.extensions || "base"
    });
    const live = json.lives?.[0] || json.data?.lives?.[0] || null;
    const forecast = json.forecasts?.[0]?.casts || json.data?.forecasts?.[0]?.casts || [];
    return {
      source: "amap",
      live,
      forecast
    };
  } catch (error) {
    console.error("AMap weather fetch failed:", error.message);
    return seedData.weather;
  }
}

function scorePois(pois, weather, query) {
  const wind = weather?.live?.windpower ? parseNumber(weather.live.windpower, 2) : 2;
  const temperature = weather?.live?.temperature ? parseNumber(weather.live.temperature, 26) : 26;
  const target = String(query.target || query.keyword || "").trim();
  return pois
    .map((poi, index) => {
      let score = poi.score || 70;
      if (weather?.live?.weather && /晴|多云/.test(weather.live.weather)) score += 3;
      if (wind <= 3) score += 4;
      if (temperature >= 20 && temperature <= 30) score += 3;
      if (/(路亚|翘嘴|鳜鱼)/.test(`${target} ${poi.name} ${poi.tags.join(" ")}`)) score += 3;
      score -= index;
      return {
        poi_id: poi.id,
        name: poi.name,
        score: clamp(score, 1, 100),
        reason: poi.reason,
        risk: poi.risk,
        distance: poi.distance,
        tags: poi.tags,
        weather: weather?.live || null
      };
    })
    .sort((a, b) => b.score - a.score);
}

function sendSeed(res, key, payload) {
  sendJson(res, 200, { source: "seed", data: payload[key] || payload });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const query = Object.fromEntries(url.searchParams.entries());

  if (req.method === "OPTIONS") {
    sendJson(res, 204, {});
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/health") {
    sendJson(res, 200, { ok: true, service: "yuni-api", amap_key_loaded: Boolean(amapKey) });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/pois") {
    const pois = await fetchPois(query);
    sendJson(res, 200, pois);
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/weather") {
    const weather = await fetchWeather(query);
    sendJson(res, 200, { data: weather });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/feed") {
    sendJson(res, 200, { source: "seed", data: seedData.feed });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/tutorials") {
    sendJson(res, 200, { source: "seed", data: seedData.tutorials });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/recommendations") {
    const poisPayload = await fetchPois(query);
    const weather = await fetchWeather(query);
    sendJson(res, 200, {
      data: {
        weather,
        items: scorePois(poisPayload.data, weather, query)
      }
    });
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/catches") {
    const body = await readBody(req);
    sendJson(res, 201, {
      data: {
        id: `post_${Date.now()}`,
        ...body,
        created_at: new Date().toISOString()
      }
    });
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/ai/fishing-advice") {
    const body = await readBody(req);
    const pois = Array.isArray(body.candidate_pois) ? body.candidate_pois : seedData.pois;
    sendJson(res, 200, {
      data: {
        summary: "今天优先选择近 10 公里、有近期鱼获且无禁钓风险的钓点。",
        top_recommendations: pois.slice(0, 2).map((poi) => ({
          poi_id: poi.id || poi.poi_id,
          reason: poi.reason || "示例推荐理由",
          risk: poi.risk || "请结合现场规则判断。"
        })),
        tips: ["优先清晨或傍晚出钓", "野钓点不要公开精确坐标", "临水位置注意防滑"]
      }
    });
    return;
  }

  sendJson(res, 404, { error: "Not found" });
});

server.listen(PORT, () => {
  console.log(`Yuni API listening on http://localhost:${PORT}`);
});
