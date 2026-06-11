# Agent 开发约定

本文件是仓库根目录的 agent 必读文件。后续任何自动化开发、协作 agent 或人工接手前，都应先阅读本文件，再修改代码。

## Python 后端环境

后端开发统一使用 conda 环境 `fish`：

```bash
conda activate fish
cd backend
```

运行 FastAPI 后端：

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

不要使用 Docker，不要新增 `docker-compose.yml`。

## 依赖管理

后端 Python 依赖统一维护在：

```text
backend/requirements.txt
```

如果开发中新增、删除或升级 Python 依赖，必须同步更新 `backend/requirements.txt`。不要只在本地 conda 环境里安装依赖而不记录。

建议流程：

```bash
conda activate fish
cd backend
pip install <package>
pip freeze > requirements.txt
```

如只是补充一个明确依赖，也可以手动编辑 `backend/requirements.txt`，但要确保后端仍可安装和启动。

## 当前项目边界

- 前端继续使用 Vue3 + Vite。
- 后端主入口是 FastAPI：`backend/app/main.py`。
- 根目录 `data/` 使用 JSON 集合模拟 NoSQL 数据库。
- 每个数据集合都应有对应的 `.schema.json` 字段描述文件。
- 不要把高德 Key、DeepSeek Key 或其他真实密钥写入代码和提交记录。

## 本地 Codex Skill

项目内安装了 `taste-skill`：

```text
.codex/skill/taste-skill/SKILL.md
```

当任务涉及前端落地页、作品集、视觉重设计或需要提升页面审美时，agent 应先阅读该 skill，再修改 Vue3 + Vite 前端代码。该 skill 来自本机：

```text
/Users/charlezk9/Projects/OpenSourceProjects/taste-skill/skills/taste-skill
```
