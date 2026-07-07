# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

"鱼你有图" — 面向钓鱼爱好者的垂钓 GIS 社交平台。帮助用户判断"去哪钓、能不能钓、现在适不适合钓"。

## 开发命令

```bash
# 后端（必须先激活 conda 环境）
conda activate fish
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端
cd frontend
npm install
npm run dev           # http://localhost:5173，Vite 代理 /api → 127.0.0.1:8000
npm run build         # 生产构建

# 测试（仅后端有测试）
cd backend
pip install pytest httpx
pytest tests/ -v
```

## 技术架构

```
前端 (Vue 3 + Vite + Element Plus + 高德 JS API)
  → /api → Vite proxy → 后端 (FastAPI + Pydantic 2)
      → services/ (业务逻辑)
          → data/json_store.py (JSON 文件原子读写)
              → 根目录 data/*.json (23 个集合，每个配 .schema.json)
```

- **后端三层**: `api/routes_*.py`（路由）→ `services/*_service.py`（业务逻辑）→ `data/json_store.py`（持久化）
- **数据层**: 根目录 `data/` 下 JSON 文件模拟 NoSQL。`json_store.py` 提供 `load_collection` / `save_collection` / `update_collection`，写入时用临时文件 + 原子替换
- **配置**: `backend/app/core/config.py` 从根目录 `.env` 读取（高德 Key、DeepSeek Key 等），通过 `@lru_cache` 单例
- **前端无路由**: `App.vue` 通过 tab 切换组件，无 vue-router。API 调用集中在 `frontend/src/services/api.js`

## 关键约定（来自 AGENTS.md）

- **conda 环境名**: `fish`
- **不用 Docker**
- **新增/删除/升级 Python 依赖必须同步更新 `backend/requirements.txt`**
- **不要将高德 Key、DeepSeek Key 写入代码或提交**
- **新增 data/ 集合必须同步创建 `.schema.json`**
- **前端视觉改动前先阅读 `.codex/skill/taste-skill/SKILL.md`**

## 当前状态与优先级

项目当前是**界面完整的单用户演示 Demo**，核心数据链路尚未完全贯通。修改优先级按 4 条路线推进：

1. **路线 1（数据持久化 + 记录链路）**: 记录页填写真实鱼获 → 保存 → 重启不丢失
2. **路线 2（用户 + 会员 + 报告）**: 移除硬编码用户和多级会员 → 单级会员 → 偏好/效率分离报告
3. **路线 3（社区 + 位置隐私）**: 帖子关联 record_id → 位置脱敏 → 评论/点赞持久化
4. **路线 4（教程 + 装备商业化）**: 学习进度 → 装备履历 → 个性化推荐

详细差距分析与具体修改方案见 `docs/创新产品设计/03_差距分析与路线/项目功能差距与修改路线.md`。

## 环境变量

根目录 `.env`（模板 `.env.example`）：
```
AMAP_WEB_SERVICE_KEY=
AMAP_SECURITY_CODE=
DEEPSEEK_API_KEY=
APP_ENV=development
```
