# 鱼你有图 Backend

当前后端是无依赖 Node.js API。已接入高德 Web 服务代理：`/api/pois` 会读取项目根目录的 `高德key.txt` 或环境变量 `AMAP_KEY`，优先请求高德 POI；`/api/weather` 会请求高德天气。高德不可达或无结果时自动回落到示例数据。

DeepSeek 现阶段仍是 mock 返回，后续可按同样方式放在后端代理，避免前端暴露密钥。

## 运行

```bash
node server.js
```

默认端口：`3001`

## API

- `GET /api/health`
- `GET /api/pois?city=420100`
- `GET /api/pois?lng=114.3055&lat=30.5928&radius=8000`
- `GET /api/weather?city=420100`
- `GET /api/feed`
- `GET /api/tutorials`
- `GET /api/recommendations`
- `POST /api/catches`
- `POST /api/ai/fishing-advice`

## 高德接入说明

- 当前支持两种 Key 来源：`AMAP_KEY` 环境变量优先，其次读取 `../高德key.txt`。
- 前端只调用业务 API，例如 `/api/pois`、`/api/weather`、`/api/recommendations`。
- 后端负责代理高德 Web 服务、清洗 POI、合并平台自有垂钓字段，不把 Key 返回给前端。
