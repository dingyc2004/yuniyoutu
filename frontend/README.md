# 鱼你有图 Frontend

Vue 3 + Vite 移动端原型。地图页使用高德 JS API，支持矢量底图和影像图层切换；社区、发布、教程、我的页面使用示例数据驱动。

## 运行

```bash
npm install
npm run dev
```

开发服务默认端口：`5173`。

需要同时启动后端：

```bash
cd ../backend
node server.js
```

## 高德地图

- 前端通过 `/api/amap/config` 获取项目根目录 `高德key.txt` 中的 key，再动态加载高德 JS API。
- 如果有 JS API 安全密钥，可放在项目根目录 `高德security.txt`，或设置环境变量 `AMAP_SECURITY_CODE`。
- `/api/pois`、`/api/weather` 仍由后端代理高德 Web 服务；高德不可达时回退到 `src/data/seedData.js`。
