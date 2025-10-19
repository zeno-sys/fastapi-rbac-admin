# Zeno FastAPI Admin 后台管理系统

基于 FastAPI 构建的现代化后台管理系统后端，支持多租户架构、RBAC 权限控制和完整的系统管理功能。

## 功能特性

- 🚀 基于 FastAPI 构建，高性能异步 API
- 🔐 JWT 认证和基于角色的访问控制(RBAC)
- 🏢 多租户架构支持
- 👥 完整的用户管理系统（用户、角色、部门、岗位）
- 📋 权限菜单管理
- 🔄 自动路由注册机制
- 📖 离线 Swagger 文档支持
- 🐳 容器化部署友好

## 技术栈

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL 数据库 ORM
- [Pydantic](https://docs.pydantic.dev/) - 数据验证和设置管理
- [JWT](https://jwt.io/) - 安全令牌认证
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器
- [Loguru](https://github.com/Delgan/loguru) - 日志记录

## 系统功能模块

### 认证授权
- 用户登录/登出
- JWT 访问令牌和刷新令牌机制
- 密码加密存储

### 用户管理
- 用户增删改查
- 用户状态管理
- 用户角色分配

### 角色管理
- 角色增删改查
- 角色权限分配

### 部门管理
- 部门树形结构管理
- 部门信息维护

### 岗位管理
- 岗位信息维护
- 岗位状态管理

### 租户管理
- 多租户隔离
- 租户信息管理
- 租户状态控制

### 权限管理
- 菜单权限管理
- 按钮级别权限控制
- API 接口权限配置

## 项目结构

```
app/
├── api/                 # API 接口层
│   ├── endpoints/       # API 端点
│   │   └── system/      # 系统管理相关接口
│   └── vo/              # 数据传输对象
├── core/                # 核心组件
├── models/              # 数据模型
├── services/            # 业务逻辑层
└── utils/               # 工具函数
config/                  # 配置文件
static/                  # 静态资源
```

## 快速开始

### 环境要求

- Python 3.11+
- 数据库 (MySQL/PostgreSQL)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

1. 复制 `.env.example` 到 `.env` 并配置相应参数
2. 修改 `config/dev.yaml` 中的数据库配置

### 运行项目

```bash
# 开发模式运行
uvicorn main:app --reload

# 生产模式运行
uvicorn main:app --host 0.0.0.0 --port 8000
```

默认访问地址：
- API 文档: http://localhost:8000/offline/docs
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

## 配置说明

项目支持多环境配置：

- `config/base.yaml` - 基础配置
- `config/dev.yaml` - 开发环境配置
- `config/prod.yaml` - 生产环境配置

通过设置 `ENV` 环境变量切换环境，默认为 `dev`。

## 多租户支持

系统采用多租户架构设计，通过以下方式实现租户隔离：

1. JWT Token 中携带 `tenant_id`
2. 请求头 `X-Tenant-ID` 指定租户
3. 数据表中包含 `tenant_id` 字段实现数据隔离

## 权限控制

系统采用基于角色的访问控制(RBAC)模型：

```
用户(User) ←→ 用户角色(UserRole) ←→ 角色(Role) ←→ 角色权限(RolePermission) ←→ 权限(Permission)
```

通过装饰器 `@require_permission` 实现接口级别的权限控制。

## API 文档

系统集成了 Swagger UI 离线文档，访问 `/offline/docs` 查看完整 API 文档。

## 部署

推荐使用 Docker 容器化部署：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 许可证

MIT License