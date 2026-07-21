# Toutiao Test - 新闻应用 API

基于 **FastAPI + SQLAlchemy 2.x (Async)** 的新闻资讯后端服务，提供分类管理、新闻列表分页查询、新闻详情（含自动浏览量统计）等功能。

---

## 技术栈

| 组件 | 技术选型 | 版本 |
|------|---------|------|
| Web 框架 | FastAPI | 0.139.2 |
| ORM | SQLAlchemy (Async) | 2.0.51 |
| 数据验证 | Pydantic | 2.13.4 |
| 数据库 | MySQL | 8.0 |
| 异步驱动 | aiomysql | 0.3.2 |
| ASGI 服务器 | Uvicorn | 0.51.0 |
| 测试框架 | pytest + pytest-asyncio | 9.1.1 |
| 容器化 | Docker + Docker Compose | — |

---

## 项目结构

```
toutiao_test/
├── main.py                  # 应用入口，FastAPI 实例 & 中间件
├── config/
│   └── db_conf.py           # 数据库连接配置（异步引擎 & 会话工厂）
├── models/
│   ├── news.py              # 新闻 ORM 模型（含 Base 基类）
│   └── news_category.py     # 新闻分类 ORM 模型
├── schemas/
│   ├── common.py            # 统一响应模型 ResponseModel
│   ├── news.py              # 新闻 Pydantic 模型（Create / Update / Response）
│   └── news_category.py     # 分类 Pydantic 模型
├── crud/
│   ├── news.py              # 新闻 CRUD 操作
│   └── news_category.py     # 分类 CRUD 操作
├── routers/
│   └── news.py              # 新闻相关 API 路由
├── scripts/
│   └── seed_news.py         # 种子数据脚本
├── tests/
│   ├── conftest.py          # 测试配置（SQLite 内存数据库）
│   ├── test_crud_news.py    # 新闻 CRUD 单元测试（14 个）
│   ├── test_crud_category.py# 分类 CRUD 单元测试（2 个）
│   └── test_api.py          # API 集成测试（10 个）
├── Dockerfile               # Docker 镜像构建
├── docker-compose.yml       # Docker Compose 编排
├── .dockerignore            # Docker 构建忽略规则
├── pytest.ini               # pytest 配置
└── requirements.txt         # Python 依赖清单
```

---

## API 接口

所有接口统一返回格式：`{ "code": int, "message": str, "data": any }`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 健康检查 |
| GET | `/hello/{name}` | 问候接口 |
| GET | `/api/news/categories` | 获取所有新闻分类（按 sort_order 升序） |
| GET | `/api/news/list` | 分页查询新闻列表 |
| GET | `/api/news/detail` | 获取新闻详情（浏览量自动 +1） |

### 接口参数

**`/api/news/list`**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| categoryId | int | 否 | — | 按分类 ID 过滤 |
| page | int | 否 | 1 | 页码（≥1） |
| pageSize | int | 否 | 10 | 每页条数（1~100） |

**`/api/news/detail`**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 新闻 ID |

### 响应示例

```json
// GET /api/news/categories
{
  "code": 200,
  "message": "success",
  "data": [
    { "id": 1, "name": "头条", "sort_order": 1 },
    { "id": 2, "name": "社会", "sort_order": 2 }
  ]
}

// GET /api/news/list?categoryId=1&page=1&pageSize=10
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "新闻标题",
        "description": "摘要",
        "content": "正文内容",
        "image": "https://example.com/img.jpg",
        "author": "作者",
        "category_id": 1,
        "views": 128,
        "publish_time": "2024-06-01T12:00:00",
        "created_at": "2024-06-01T12:00:00",
        "updated_at": "2024-06-01T12:00:00"
      }
    ],
    "total": 150,
    "page": 1,
    "pageSize": 10
  }
}

// GET /api/news/detail?id=42
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 42,
    "title": "新闻标题",
    "views": 129
  }
}
```

---

## 数据库表结构

### news 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AUTO) | 主键 |
| title | VARCHAR(255) | 标题 |
| description | VARCHAR(500) | 摘要 |
| content | TEXT | 正文 |
| image | VARCHAR(255) | 封面图 URL |
| author | VARCHAR(50) | 作者 |
| category_id | INT | 分类 ID |
| views | INT | 浏览量（默认 0） |
| publish_time | DATETIME | 发布时间 |
| created_at | DATETIME | 创建时间（自动） |
| updated_at | DATETIME | 更新时间（自动） |

### news_category 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK, AUTO) | 主键 |
| name | VARCHAR(50) | 分类名称 |
| sort_order | INT | 排序序号（默认 0） |
| created_at | DATETIME | 创建时间（自动） |
| updated_at | DATETIME | 更新时间（自动） |

---

## 本地开发

### 环境要求

- Python 3.14+
- MySQL 8.0

### 1. 克隆项目并创建虚拟环境

```bash
cd toutiao_test
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `config/db_conf.py` 中的数据库连接字符串，或设置环境变量：

```bash
export DATABASE_URL="mysql+aiomysql://root:your-password@localhost:3306/news_app?charset=utf8mb4"
```

确保 MySQL 中已创建 `news_app` 数据库：

```sql
CREATE DATABASE news_app CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- 应用地址：http://127.0.0.1:8000
- Swagger 文档：http://127.0.0.1:8000/docs
- ReDoc 文档：http://127.0.0.1:8000/redoc

### 5. 插入测试数据（可选）

```bash
PYTHONPATH=$(pwd) python scripts/seed_news.py
```

### 6. 运行测试

```bash
python -m pytest tests/ -v
```

测试使用 SQLite 内存数据库，无需连接 MySQL，共 26 个测试用例。

---

## Docker 部署

### 方式一：Docker Compose（推荐）

一键启动应用 + MySQL 数据库：

```bash
docker-compose up --build -d
```

- 应用访问：http://127.0.0.1:8000
- MySQL 端口：3306（root 密码：`my-secret-pw`，数据库：`news_app`）

查看日志：

```bash
docker-compose logs -f app
```

停止服务：

```bash
docker-compose down          # 停止容器
docker-compose down -v       # 停止并清除数据卷
```

### 方式二：仅 Docker 构建应用镜像

适用于已有独立 MySQL 实例的场景：

```bash
# 构建镜像
docker build -t toutiao-test .

# 运行容器，通过环境变量指定数据库地址
docker run -d \
  --name toutiao-app \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://root:password@host.docker.internal:3306/news_app?charset=utf8mb4" \
  toutiao-test
```

### 方式三：生产环境部署

```bash
# 使用多 worker 启动
docker run -d \
  --name toutiao-app \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pass@db-host:3306/news_app" \
  toutiao-test \
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 异步连接字符串 | `mysql+aiomysql://root:my-secret-pw@localhost:3306/news_app?charset=utf8mb4` |

---

## 注意事项

1. **greenlet 依赖**：SQLAlchemy 2.x 异步模式强制要求 `greenlet` 库，已包含在 `requirements.txt` 中
2. **数据库表需预先创建**：本项目未使用 `metadata.create_all()` 自动建表，需手动在 MySQL 中创建表结构
3. **CORS 配置**：`main.py` 中默认允许所有源（`allow_origins=["*"]`），生产环境请指定具体域名
4. **连接池参数**：`pool_size=10`，`max_overflow=20`，可根据生产负载在 `config/db_conf.py` 中调整
