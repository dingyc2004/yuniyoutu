# 鱼你有图 Backend

当前后端已切换为 FastAPI。MVP 阶段先跑通接口骨架、规则推荐和内容发布闭环，数据库暂不引入，全部先用 seed data 和内存数据承接。

## 环境

建议使用 conda：

```bash
conda create -n yuniyoutu-backend python=3.11
conda activate yuniyoutu-backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 目录

- `app/main.py`：FastAPI 入口，挂载 router 和 CORS
- `app/api/`：接口路由
- `app/core/config.py`：环境变量读取
- `app/schemas/`：请求和响应模型
- `app/services/`：规则推荐、POI、天气、AI 解释和第三方封装
- `app/data/seed_data.py`：MVP 示例数据

## 可用接口

- `GET /api/health`
- `GET /api/amap/config`
- `GET /api/pois`
- `GET /api/pois/{poi_id}`
- `GET /api/posts`
- `GET /api/feed`
- `POST /api/posts`
- `POST /api/catches`
- `POST /api/recommendations`
- `POST /api/ai/fishing-advice`
- `GET /api/weather/current`
- `GET /api/weather`
- `GET /api/tutorials`

## 接入说明

- 高德 Web 服务 Key 通过 `AMAP_WEB_SERVICE_KEY` 读取，JS API 所需安全码通过 `AMAP_SECURITY_CODE` 读取。
- DeepSeek Key 通过 `DEEPSEEK_API_KEY` 读取。当前 AI 接口默认仍以 mock 返回为主，只在生产配置下预留真实调用结构。
- 后端暂不引入数据库，帖子和推荐结果先走 seed data 与内存态，后续再接持久化层。
- 旧版 `server.js` 作为 legacy 保留，不作为当前主入口。
