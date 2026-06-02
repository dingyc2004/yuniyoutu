# 鱼你有图 Frontend

Vue 3 + Vite 移动端原型。地图使用高德 JS API v2.0，默认卫星图 + 路网注记。

## 运行

```bash
npm install
npm run dev
```

开发服务端口 `5173`，Vite 已配置 `/api` 代理到后端 `localhost:3001`。

## 主要功能

- **地图**：卫星底图 + TileLayer.RoadNet 注记、钓点 marker、点击弹窗、路线规划（驾车/步行/公交）
- **钓点卡片**：点击跳转地图定位、"导航"按钮规划路线、"详情"按钮弹出详情弹窗
- **社区**：鱼获动态流
- **教程**：钓鱼教程列表
- **发布**：鱼获记录
- **我的**：个人战绩

## 高德地图

- 前端通过 `/api/amap/config` 获取 Key，动态加载高德 JS API
- 路线规划通过 `AMap.plugin()` 动态加载 Driving/Walking/Transfer/Geocoder
- API 不可达时回退到 `src/data/seedData.js` 示例数据
