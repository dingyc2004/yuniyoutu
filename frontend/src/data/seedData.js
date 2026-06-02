export const seedData = {
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
      address: "武汉市武昌区东湖听涛景区附近",
      location: "114.3691,30.5567",
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
      address: "武汉市青山区江滩公园附近",
      location: "114.4154,30.6278",
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
      address: "武汉市洪山区南湖附近",
      location: "114.3316,30.4885",
      x: 74,
      y: 72
    }
  ],
  weather: {
    source: "seed",
    live: {
      city: "武汉市",
      adcode: "420100",
      weather: "多云",
      temperature: "28",
      winddirection: "西南",
      windpower: "3",
      humidity: "58",
      reporttime: new Date().toISOString()
    },
    forecast: [
      { date: "今天", dayweather: "多云", nightweather: "多云", daytemp: "29", nighttemp: "22", daywind: "西南", daypower: "3" },
      { date: "明天", dayweather: "多云", nightweather: "阵雨", daytemp: "28", nighttemp: "23", daywind: "东", daypower: "2" },
      { date: "后天", dayweather: "晴", nightweather: "晴", daytemp: "30", nighttemp: "24", daywind: "东南", daypower: "2" }
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
