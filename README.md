# 鱼你有图

“鱼你有图”是面向钓鱼爱好者的垂钓 GIS 社交平台。它把地图找点、POI 详情、规则推荐、鱼获发布、社区展示和教程学习放在同一个链路里，目标是让用户更快判断“去哪钓、能不能钓、现在适不适合钓”。

## 技术栈

- 前端：Vue3 + Vite + 高德 JS API
- 后端：FastAPI + Pydantic + httpx
- 环境：conda + `requirements.txt`

## 项目结构

```text
project-root/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── data/
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── pois.json
│   ├── pois.schema.json
│   ├── posts.json
│   ├── posts.schema.json
│   ├── tutorials.json
│   ├── tutorials.schema.json
│   ├── weather_snapshots.json
│   └── weather_snapshots.schema.json
├── docs/
│   └── 开发设计书.md
├── .env.example
├── .gitignore
└── README.md
```

## 快速开始

### 1. 启动后端

```bash
conda create -n yuniyoutu-backend python=3.11
conda activate yuniyoutu-backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，后端默认运行在 `http://127.0.0.1:8000`。

## 环境变量

项目根目录使用 `.env`，模板见 `.env.example`。

```env
AMAP_WEB_SERVICE_KEY=
AMAP_SECURITY_CODE=
DEEPSEEK_API_KEY=
APP_ENV=development
```

说明：

- `AMAP_WEB_SERVICE_KEY`：高德 Web 服务 Key，放后端使用
- `AMAP_SECURITY_CODE`：高德 JS API 安全码
- `DEEPSEEK_API_KEY`：DeepSeek Key，当前 AI 接口默认仍是 mock
- `APP_ENV`：开发环境建议 `development`

## 后端接口说明

当前 MVP 阶段接口如下：

- `GET /api/health`
- `GET /api/amap/config`
- `GET /api/pois`
- `GET /api/pois/{poi_id}`
- `GET /api/posts`
- `POST /api/posts`
- `GET /api/feed`
- `POST /api/catches`
- `POST /api/recommendations`
- `POST /api/ai/fishing-advice`
- `GET /api/weather/current`
- `GET /api/weather`
- `GET /api/tutorials`

返回值统一以 `data` 为主，便于前端对接和后续扩展。

## 数据存储说明

当前不引入正式数据库，根目录 `data/` 用 JSON 模拟 NoSQL 集合：

- `pois.json`：垂钓 POI 集合
- `posts.json`：鱼获、空军、探点等帖子集合
- `tutorials.json`：教程集合
- `weather_snapshots.json`：天气快照集合

每个集合都有对应的 `.schema.json` 描述文件，用 JSON Schema 说明字段类型、必填项和业务含义。后端启动后读取这些 JSON 作为初始数据，`POST /api/posts` 当前仍只写入内存态列表，服务重启后新增内容会丢失。

## 前端页面说明

- 地图页：查看附近钓点、搜索、筛选、点选 POI、查看路线
- 钓点详情：查看推荐理由、安全提示、鱼种和标签
- 发布页：发布鱼获、空军和探点记录
- 社区页：展示鱼获流和互动内容
- 教程页：展示新手和进阶教程
- 我的页：当前为基础骨架，后续接个人数据

## 当前完成情况

- 已完成 Vue3 + Vite 前端基础
- 已完成 FastAPI 后端骨架
- 已完成 POI、帖子、推荐、天气、AI 解释的接口骨架
- 已完成 JSON 集合模拟 NoSQL 数据层和内存态发布链路
- 已完成高德 Key、DeepSeek Key 的环境变量方案
- 已完成开发设计书更新
- 旧版 Node 后端已保留为 legacy，不再作为主入口

## 后续开发计划

1. 继续把前端页面逐步切到 FastAPI 的稳定数据结构
2. 接入真实高德 POI 和天气服务
3. 把帖子、收藏、评论和 POI 详情联动做深
4. 引入数据库和用户系统
5. 在规则推荐基础上继续增强 AI 解释和复盘能力

## 小组协作规范

1. 先对齐设计书，再改代码
2. 接口字段先兼容后收敛，不要一次性大改
3. 第三方密钥不写死在仓库
4. 前端和后端改动尽量分批提交，方便联调
5. 每次合并前先确认地图页、详情页、发布页和社区页的闭环没有断
