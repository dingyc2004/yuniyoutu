# 鱼你有图

鱼类识别科普与钓点推荐应用。前端 Vue3 + Vite，后端 Node.js 无依赖 HTTP 服务，地图基于高德 JS API v2.0。

## 快速开始

```bash
# 终端1：启动后端
cd backend
node server.js

# 终端2：启动前端
cd frontend
npm install
npm run dev
```

后端端口 `3001`，前端 `5173`（Vite 已配置 `/api` 代理到后端）。

## 项目结构

```
├── backend/
│   ├── server.js          # Node HTTP 服务，代理高德 API + seed 数据
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.vue        # 主组件：Tab 导航、详情弹窗、数据加载
│   │   ├── main.js        # Vue 入口
│   │   ├── styles.css     # 全局样式
│   │   ├── components/
│   │   │   ├── MapPanel.vue      # 地图面板：卫星图、钓点标记、路线规划
│   │   │   ├── PoiCard.vue       # 钓点卡片：点击定位/导航/详情
│   │   │   ├── CommunityView.vue # 社区鱼获动态
│   │   │   ├── PublishView.vue   # 发布页
│   │   │   ├── TutorialsView.vue # 教程页
│   │   │   └── MineView.vue      # 个人页
│   │   ├── data/
│   │   │   └── seedData.js       # 示例数据（兜底用）
│   │   └── services/
│   │       └── api.js            # API 请求封装
│   ├── vite.config.js
│   └── package.json
├── 高德key.txt            # 高德 Web 服务 Key（前端 JS API 共用）
├── 高德security.txt       # 高德 JS API 安全密钥（可选）
└── package.json           # 根目录脚本
```

## 功能

- 卫星地图 + 路网注记（高德 JS API v2.0）
- 钓点搜索与推荐，marker 点选弹出详情
- POI 卡片点击跳转地图定位
- 路线规划：驾车/步行/公交三种方式，起点"武汉大学信息学部南二门"
- 钓点详情弹窗（推荐理由、安全提示、鱼种、标签）
- 社区鱼获动态、教程、发布、个人主页

## 高德配置

1. 在[高德开放平台](https://console.amap.com)创建应用，获取 Key
2. 将 Key 写入项目根目录 `高德key.txt`
3. 确保 Key 已开通以下服务：Web服务 API、Web端 JS API（含 WebGL 地图可选）
4. 如有 JS API 安全密钥，写入 `高德security.txt` 或设置环境变量 `AMAP_SECURITY_CODE`
