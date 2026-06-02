const API_BASE = "http://localhost:3001";

const fallbackData = {
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

const state = {
  tab: "map",
  subFeed: "推荐",
  lessonFilter: "全部",
  pois: fallbackData.pois,
  feed: fallbackData.feed,
  tutorials: fallbackData.tutorials,
  weather: fallbackData.weather,
  filter: "全部"
};

const titles = {
  map: "附近钓点",
  community: "鱼获社区",
  publish: "记一竿",
  tutorials: "钓鱼教程",
  mine: "我的战绩"
};

const screen = document.querySelector("#screen");
const title = document.querySelector("#screen-title");

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function loadApi(path, key) {
  try {
    const response = await fetch(`${API_BASE}${path}`, { signal: AbortSignal.timeout(1200) });
    if (!response.ok) throw new Error("bad response");
    const payload = await response.json();
    state[key] = payload.data;
  } catch {
    state[key] = fallbackData[key];
  }
}

function toneClass(tone = "blue") {
  return `tone-${tone}`;
}

function render() {
  title.textContent = titles[state.tab];
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === state.tab);
  });

  if (state.tab === "map") renderMap();
  if (state.tab === "community") renderCommunity();
  if (state.tab === "publish") renderPublish();
  if (state.tab === "tutorials") renderTutorials();
  if (state.tab === "mine") renderMine();
}

function weatherSummary() {
  const live = state.weather?.live;
  if (!live) return "天气信息暂不可用";
  return `${live.weather} · ${live.temperature}℃ · ${live.winddirection || "风向未知"} ${live.windpower || ""}级`;
}

function renderMap() {
  const filters = ["全部", "野钓", "钓场", "路亚", "免费", "夜钓"];
  const shown = state.filter === "全部"
    ? state.pois
    : state.pois.filter((poi) => poi.type === state.filter || poi.tags.includes(state.filter));

  screen.innerHTML = `
    <section class="map-card">
      <div class="river"></div>
      <div class="map-search">⌕ 搜索水库、河流、钓场、鱼种</div>
      <div class="weather-pill">${escapeHtml(weatherSummary())}</div>
      ${state.pois.map((poi, index) => `
        <button class="pin ${poi.type === "钓场" ? "paid" : ""}" data-poi="${poi.id}" style="left:${poi.x}%;top:${poi.y}%">
          <span>${index + 1}</span>
        </button>
      `).join("")}
      <div class="recommend-strip">
        <strong>今日推荐：${escapeHtml(state.pois[0]?.name || "暂无钓点")}</strong>
        <p>${escapeHtml(state.pois[0]?.reason || "暂无推荐理由")}</p>
      </div>
    </section>
    <div class="chips">
      ${filters.map((filter) => `<button class="chip ${state.filter === filter ? "active" : ""}" data-filter="${filter}">${filter}</button>`).join("")}
    </div>
    <section class="section">
      <div class="section-head">
        <h2>附近可去</h2>
        <span class="meta">${escapeHtml(weatherSummary())}</span>
      </div>
      <div class="poi-list">
        ${shown.map(renderPoiCard).join("")}
      </div>
    </section>
  `;
}

function renderPoiCard(poi) {
  return `
    <article class="card poi-card">
      <div class="poi-head">
        <div>
          <h3>${escapeHtml(poi.name)}</h3>
          <p class="meta">${escapeHtml(poi.type)} · ${escapeHtml(poi.distance)} · ${escapeHtml((poi.fish || []).join(" / "))}</p>
        </div>
        <span class="score">${escapeHtml(poi.score)}</span>
      </div>
      <p class="meta">${escapeHtml(poi.reason)}</p>
      <div class="chips">
        ${(poi.tags || []).map((tag) => `<span class="badge">${escapeHtml(tag)}</span>`).join("")}
      </div>
      <div class="actions">
        <button class="btn" data-action="nav" data-name="${escapeHtml(poi.name)}">导航</button>
        <button class="btn secondary" data-action="detail" data-name="${escapeHtml(poi.name)}">详情</button>
      </div>
    </article>
  `;
}

function renderCommunity() {
  const filters = ["推荐", "关注", "同城", "空军", "热门"];
  const shown = state.subFeed === "推荐"
    ? state.feed
    : state.feed
      .filter((item) => {
        const text = `${item.title} ${item.excerpt} ${item.meta} ${(item.tags || []).join(" ")}`;
        if (state.subFeed === "关注") return ["post_001", "post_002"].includes(item.id);
        if (state.subFeed === "同城") return /武汉|东湖|青山|南湖/.test(text);
        if (state.subFeed === "热门") return item.likes >= 100;
        return text.includes(state.subFeed);
      })
      .sort((a, b) => b.likes - a.likes);

  screen.innerHTML = `
    <section class="community-hero card">
      <div>
        <p class="eyebrow">XIAOHONGSHU STYLE</p>
        <h2>图文晒鱼获，视频讲过程</h2>
        <p class="meta">社区不只是发结果，也能发复盘、探点、教程和空军记录。</p>
      </div>
      <div class="community-hero-stats">
        <div><strong>328</strong><span>今日笔记</span></div>
        <div><strong>46</strong><span>视频教程</span></div>
      </div>
    </section>
    <div class="segmented">
      ${filters.map((filter) => `<button class="${state.subFeed === filter ? "active" : ""}" data-feed="${filter}">${filter}</button>`).join("")}
    </div>
    <section class="feed">
      ${shown.map(renderFeedCard).join("")}
    </section>
  `;
}

function coverGradient(tone) {
  const map = {
    blue: "linear-gradient(135deg, #214f79, #63c3d6)",
    green: "linear-gradient(135deg, #1f7a58, #9dd35d)",
    amber: "linear-gradient(135deg, #b26f1f, #f0b840)",
    purple: "linear-gradient(135deg, #4d2f8f, #a978ff)"
  };
  return map[tone] || map.blue;
}

function renderFeedCard(post) {
  return `
    <article class="card note-card">
      <div class="note-cover ${toneClass(post.coverTone)}" style="background:${coverGradient(post.coverTone)};">
        <span class="note-format">${escapeHtml(post.format)}</span>
        <span class="note-score">热度 ${post.likes}</span>
      </div>
      <div class="note-body">
        <div class="author-row">
          <div class="avatar">${escapeHtml(post.avatar)}</div>
          <div>
            <strong>${escapeHtml(post.author)}</strong>
            <p class="meta">${escapeHtml(post.meta)}</p>
          </div>
          <button class="follow-btn" type="button">关注</button>
        </div>
        <h3 class="note-title">${escapeHtml(post.title)}</h3>
        <p class="note-excerpt">${escapeHtml(post.excerpt)}</p>
        <div class="chips note-tags">
          ${(post.tags || []).map((tag) => `<span class="badge">${escapeHtml(tag)}</span>`).join("")}
        </div>
        <div class="note-actions">
          <button class="icon-action" data-action="like" data-name="${escapeHtml(post.title)}">❤ ${post.likes}</button>
          <button class="icon-action" data-action="comment" data-name="${escapeHtml(post.title)}">✎ ${post.comments}</button>
          <button class="icon-action" data-action="save" data-name="${escapeHtml(post.title)}">☆ ${post.saves}</button>
          <button class="share-action" data-action="share" data-name="${escapeHtml(post.title)}">分享</button>
        </div>
      </div>
    </article>
  `;
}

function renderPublish() {
  screen.innerHTML = `
    <section class="card poi-card">
      <div class="upload-box">
        <div>
          <strong>上传鱼获照片或空军现场</strong>
          <p class="meta">示例原型：自动绑定天气、时间和钓点</p>
        </div>
      </div>
      <form class="form" id="catch-form">
        <div class="field">
          <label for="catch-type">记录类型</label>
          <select id="catch-type">
            <option>鱼获</option>
            <option>空军</option>
            <option>探点</option>
          </select>
        </div>
        <div class="field">
          <label for="poi">钓点</label>
          <select id="poi">${state.pois.map((poi) => `<option>${escapeHtml(poi.name)}</option>`).join("")}</select>
        </div>
        <div class="field">
          <label for="fish">鱼种</label>
          <input id="fish" value="鲫鱼、翘嘴" />
        </div>
        <div class="field">
          <label for="method">钓法</label>
          <select id="method">
            <option>台钓</option>
            <option>路亚</option>
            <option>海钓</option>
            <option>夜钓</option>
          </select>
        </div>
        <div class="field">
          <label for="privacy">位置隐私</label>
          <select id="privacy">
            <option>模糊公开 1km</option>
            <option>精确公开</option>
            <option>仅互关可见</option>
            <option>完全隐藏</option>
          </select>
        </div>
        <div class="field">
          <label for="note">心得</label>
          <textarea id="note">上午口更稳，风小的时候漂相明显。</textarea>
        </div>
        <button class="btn" type="submit">生成鱼获战绩卡</button>
      </form>
    </section>
  `;
}

function renderTutorials() {
  const filters = ["全部", "图文", "视频", "入门", "进阶"];
  const shown = state.lessonFilter === "全部"
    ? state.tutorials
    : state.tutorials.filter((item) => item.type === state.lessonFilter || item.level === state.lessonFilter);

  screen.innerHTML = `
    <section class="card tutorial-hero">
      <div>
        <p class="eyebrow">LEARN</p>
        <h2>图文能讲步骤，视频能看动作</h2>
        <p class="meta">教程页把新手路径拆成图文和视频两种形态，方便用户按场景选择。</p>
      </div>
      <div class="tutorial-path">
        <span>能不能钓</span>
        <span>怎么找点</span>
        <span>怎么复盘</span>
      </div>
    </section>
    <div class="segmented">
      ${filters.map((filter) => `<button class="${state.lessonFilter === filter ? "active" : ""}" data-lesson="${filter}">${filter}</button>`).join("")}
    </div>
    <section class="lesson-list">
      ${shown.map(renderLessonCard).join("")}
    </section>
  `;
}

function renderLessonCard(lesson) {
  const badge = lesson.type === "视频" ? "▶ 视频" : "图文";
  return `
    <article class="card lesson-card">
      <div class="lesson-cover ${toneClass(lesson.coverTone)}" style="background:${coverGradient(lesson.coverTone)};">
        <span class="note-format">${badge}</span>
        <span class="note-score">${escapeHtml(lesson.level)}</span>
      </div>
      <div class="note-body">
        <div class="row">
          <span class="badge">${escapeHtml(lesson.duration)}</span>
          <span class="meta">${escapeHtml(lesson.type)}</span>
        </div>
        <h3 class="note-title">${escapeHtml(lesson.title)}</h3>
        <p class="note-excerpt">${escapeHtml(lesson.summary)}</p>
        <div class="chips note-tags">
          ${(lesson.tags || []).map((tag) => `<span class="badge">${escapeHtml(tag)}</span>`).join("")}
        </div>
        <div class="actions">
          <button class="btn secondary">收藏</button>
          <button class="btn">开始学习</button>
        </div>
      </div>
    </article>
  `;
}

function renderMine() {
  screen.innerHTML = `
    <section class="card profile-panel">
      <div class="row">
        <div>
          <h2>武汉钓友 008</h2>
          <p class="meta">偏好：野钓、路亚、清晨窗口</p>
        </div>
        <span class="badge">探点官</span>
      </div>
      <div class="stat-grid">
        <div class="stat"><strong>18</strong><span class="meta">出钓</span></div>
        <div class="stat"><strong>6</strong><span class="meta">钓点</span></div>
        <div class="stat"><strong>3.2斤</strong><span class="meta">最大单尾</span></div>
      </div>
    </section>
    <section class="section poi-list">
      <article class="card poi-card">
        <h3>本月报告</h3>
        <p class="meta">你在气温 20-26℃、风力 1-3 级时鱼获率最高。东湖听涛和青山江滩是你的高频点。</p>
        <button class="btn">生成会员报告</button>
      </article>
      <article class="card poi-card">
        <h3>我的收藏</h3>
        <p class="meta">收藏钓点 4 个，教程 7 篇，鱼获帖 12 条。</p>
      </article>
    </section>
  `;
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 1800);
}

document.addEventListener("click", (event) => {
  const tab = event.target.closest(".tab");
  if (tab) {
    state.tab = tab.dataset.tab;
    render();
    return;
  }

  const filter = event.target.closest("[data-filter]");
  if (filter) {
    state.filter = filter.dataset.filter;
    render();
    return;
  }

  const feedFilter = event.target.closest("[data-feed]");
  if (feedFilter) {
    state.subFeed = feedFilter.dataset.feed;
    render();
    return;
  }

  const lessonFilter = event.target.closest("[data-lesson]");
  if (lessonFilter) {
    state.lessonFilter = lessonFilter.dataset.lesson;
    render();
    return;
  }

  const action = event.target.closest("[data-action]");
  if (action) {
    showToast(`${action.dataset.name}：示例原型已记录操作`);
    return;
  }

  const pin = event.target.closest("[data-poi]");
  if (pin) {
    const poi = state.pois.find((item) => item.id === pin.dataset.poi);
    if (poi) showToast(`${poi.name} · 推荐分 ${poi.score}`);
  }
});

document.addEventListener("submit", (event) => {
  if (event.target.id === "catch-form") {
    event.preventDefault();
    showToast("已生成鱼获战绩卡，位置按隐私设置展示");
  }
});

document.querySelector("#locate-btn").addEventListener("click", () => {
  showToast("已使用示例定位：武汉市洪山区");
});

async function init() {
  await Promise.all([
    loadApi("/api/pois?city=420100", "pois"),
    loadApi("/api/feed", "feed"),
    loadApi("/api/tutorials", "tutorials"),
    loadApi("/api/weather?city=420100", "weather")
  ]);
  render();
}

init();
