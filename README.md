# 鱼你有图

"鱼你有图"是面向钓鱼爱好者的垂钓 GIS 社交平台。它把地图找点、POI 详情、规则推荐、鱼获发布、社区展示和教程学习放在同一个链路里，目标是让用户更快判断"去哪钓、能不能钓、现在适不适合钓"。

## 技术栈

- 前端：Vue3 + Vite + Element Plus + 高德 JS API
- 后端：FastAPI + Pydantic + httpx
- 环境：conda (base 环境) + `requirements.txt`

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
│   ├── tests/
│   ├── requirements.txt
│   ├── server.py
│   └── README.md
├── data/
│   ├── *.json           (数据集合)
│   └── *.schema.json    (JSON Schema)
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

## 快速开始

### 1. 启动后端

```bash
conda activate base
cd backend
pip install -r requirements.txt
python server.py
```

或直接：

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，后端默认运行在 `http://127.0.0.1:8000`。

### 3. 运行测试

```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

## 环境变量

项目根目录使用 `.env`，模板见 `.env.example`。

```env
AMAP_WEB_SERVICE_KEY=
AMAP_SECURITY_CODE=
DEEPSEEK_API_KEY=
APP_ENV=development
```

## 后端接口说明

### 核心接口

- `GET /api/health`
- `GET /api/amap/config`

### 钓鱼记录

- `GET /api/records` — 查询记录（支持 user_id）
- `POST /api/records` — 创建记录
- `GET /api/records/{record_id}` — 获取记录详情
- `PATCH /api/records/{record_id}` — 更新记录
- `DELETE /api/records/{record_id}` — 删除记录

### 用户与会员

- `GET /api/users/{user_id}` — 获取用户资料
- `GET /api/users/{user_id}/membership` — 获取会员状态
- `GET /api/users/{user_id}/profile-summary` — 获取个人档案汇总
- `GET /api/users/{user_id}/reports` — 获取报告历史
- `POST /api/users/{user_id}/reports` — 生成新报告
- `GET /api/reports/{report_id}` — 获取单个报告

### 社区帖子

- `GET /api/posts` — 查询帖子（支持 channel, city, method, species）
- `GET /api/feed` — 信息流
- `POST /api/posts` — 发布帖子
- `GET /api/posts/{post_id}` — 获取帖子详情

### 社区互动

- `POST /api/posts/{post_id}/comments` — 添加评论
- `GET /api/posts/{post_id}/comments` — 查看评论
- `POST /api/posts/{post_id}/reactions` — 点赞/收藏切换
- `POST /api/users/{user_id}/follow` — 关注用户
- `DELETE /api/users/{user_id}/follow` — 取消关注

### 活动与群聊

- `GET /api/events` — 活动列表
- `POST /api/events` — 创建活动
- `POST /api/events/{event_id}/register` — 报名活动
- `POST /api/events/{event_id}/checkin` — 签到
- `GET /api/groups` — 群组列表
- `GET /api/groups/{group_id}/messages` — 获取消息
- `POST /api/groups/{group_id}/messages` — 发送消息

### 其他

- `GET /api/pois` — POI 搜索
- `POST /api/recommendations` — 推荐
- `GET /api/weather/current` — 天气
- `GET /api/tutorials` — 教程
- `POST /api/ai/fishing-advice` — AI 建议

返回值统一以 `data` 为主，便于前端对接和后续扩展。

## 数据持久化

所有数据存储在 `data/` 目录的 JSON 文件中。新增记录和帖子后，后端会原子写入 JSON 文件，服务重启后数据不会丢失。每个集合都有对应的 `.schema.json` 描述文件。

### 数据集合

| 集合 | 用途 |
| --- | --- |
| `records` | 出钓记录 |
| `posts` | 社区帖子 |
| `users` | 用户资料 |
| `memberships` | 单级会员状态 |
| `report_snapshots` | 报告历史快照 |
| `comments` | 帖子评论 |
| `reactions` | 点赞/收藏 |
| `follows` | 关注关系 |
| `events` | 社群活动 |
| `event_registrations` | 活动报名 |
| `groups` | 群组 |
| `group_members` | 群成员 |
| `messages` | 群消息 |
| `learning_progress` | 教程学习进度 |
| `equipment` | 装备信息 |
| `pois` | 钓点 POI |
| `fish_species` | 鱼种百科 |
| `tutorials` | 教程 |
| `weather_snapshots` | 天气快照 |

## 会员体系

采用单级会员制度，状态为 `active`/`inactive`/`expired`：
- 会员：完整档案、报告生成与分享
- 非会员：完整记录和社区功能，报告能力受限

## 位置隐私

帖子发布时支持独立的**内容权限**和**位置精度**设置：
- 内容权限：公开、朋友、私密
- 位置精度：精确位置、水域模糊、仅城市、完全隐藏

后端返回公开帖子前自动执行位置脱敏。

## 当前完成情况

- 已完成 Vue3 + Vite 前端基础
- 已完成 FastAPI 后端骨架
- 已完成 JSON 数据持久化（重启不丢失）
- 已完成记录页鱼获完整输入（鱼种、条数、重量、钓法、饵料、最大单尾、空军标记）
- 已完成用户资料与单级会员
- 已完成报告服务（偏好分析 vs 效率分析分离）
- 已完成社区互动（评论、点赞、关注）后端
- 已完成活动、群聊基础后端
- 已完成位置脱敏逻辑
- 已完成后端 pytest 测试

## 小组协作规范

1. 先对齐设计书，再改代码
2. 接口字段先兼容后收敛，不要一次性大改
3. 第三方密钥不写死在仓库
4. 前端和后端改动尽量分批提交，方便联调
5. 每次合并前先确认地图页、详情页、发布页和社区页的闭环没有断
