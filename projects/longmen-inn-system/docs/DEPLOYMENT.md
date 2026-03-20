# 龙门客栈业务管理系统 - 部署文档

> 🏮 文档版本: v1.0.0 | 最后更新: 2026-03-15

## 📚 目录

- [环境要求](#环境要求)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [数据库初始化](#数据库初始化)
- [环境变量配置](#环境变量配置)
- [Nginx配置](#nginx配置)
- [Docker部署](#docker部署)

---

## 环境要求

### 最小配置要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB SSD | 50GB SSD |
| 网络 | 10Mbps | 100Mbps |

### 软件依赖

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.9+ | 后端运行环境 |
| Node.js | 18+ | 前端运行环境 |
| npm/pnpm | 9+ | 前端包管理 |
| SQLite | 3.x | 开发环境数据库 |
| PostgreSQL | 14+ | 生产环境数据库 |
| Redis | 6+ | 缓存和消息队列 |
| Nginx | 1.18+ | 反向代理 |

---

## 后端部署

### 方式一：原生部署

#### 1. 克隆代码

```bash
git clone https://github.com/your-org/longmen-inn-system.git
cd longmen-inn-system/backend
```

#### 2. 创建虚拟环境

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

#### 5. 初始化数据库

```bash
# 执行数据库迁移
alembic upgrade head

# 初始化基础数据
python scripts/init_data.py
```

#### 6. 启动服务

```bash
# 开发模式（热重载）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

### 方式二：Systemd 服务部署

#### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/longmen-inn-backend.service
```

#### 2. 配置内容

```ini
[Unit]
Description=龙门客栈业务管理系统后端服务
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=longmen
Group=longmen
WorkingDirectory=/opt/longmen-inn-system/backend
Environment="PATH=/opt/longmen-inn-system/backend/venv/bin"
EnvironmentFile=/opt/longmen-inn-system/backend/.env
ExecStart=/opt/longmen-inn-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 3. 启动服务

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start longmen-inn-backend

# 设置开机自启
sudo systemctl enable longmen-inn-backend

# 查看状态
sudo systemctl status longmen-inn-backend

# 查看日志
sudo journalctl -u longmen-inn-backend -f
```

---

## 前端部署

### 1. 安装依赖

```bash
cd longmen-inn-system/frontend
npm install
# 或使用 pnpm
pnpm install
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# API基础URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# WebSocket URL
VITE_WS_URL=ws://localhost:8000/ws

# 静态资源URL
VITE_ASSETS_URL=http://localhost:8000/static
```

### 3. 构建

```bash
# 开发模式
npm run dev

# 生产构建
npm run build
```

构建输出位于 `dist/` 目录。

---

## 数据库初始化

### SQLite (开发环境)

```bash
cd backend
python scripts/init_db.py
```

### PostgreSQL (生产环境)

#### 1. 创建数据库和用户

```bash
# 切换到postgres用户
sudo -u postgres psql

# 创建数据库
CREATE DATABASE longmen_inn_db;

# 创建用户
CREATE USER longmen_user WITH PASSWORD 'your_secure_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE longmen_inn_db TO longmen_user;

# 退出
\q
```

#### 2. 执行迁移

```bash
cd backend

# 配置数据库URL
export DATABASE_URL="postgresql://longmen_user:your_secure_password@localhost:5432/longmen_inn_db"

# 执行迁移
alembic upgrade head

# 初始化数据
python scripts/init_data.py
```

---

## 环境变量配置

### 后端环境变量 (.env)

```bash
# ============================================
# 龙门客栈业务管理系统 - 环境变量配置
# ============================================

# 应用配置
APP_NAME=龙门客栈业务管理系统
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-super-secret-key-here

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
# SQLite (开发)
DATABASE_URL=sqlite:///./longmen_inn.db

# PostgreSQL (生产)
# DATABASE_URL=postgresql://user:password@localhost:5432/longmen_inn_db

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# OpenClaw集成配置
OPENCLAW_GATEWAY_URL=http://localhost:8080
OPENCLAW_API_KEY=your-openclaw-api-key
OPENCLAW_WS_URL=ws://localhost:8080/ws
```

### 前端环境变量 (.env)

```bash
# ============================================
# 龙门客栈业务管理系统前端 - 环境变量配置
# ============================================

# API配置
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# 静态资源
VITE_ASSETS_URL=http://localhost:8000/static
VITE_AVATAR_URL=http://localhost:8000/static/avatars

# 系统配置
VITE_APP_NAME=龙门客栈业务管理系统
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_REALTIME=true
```

---

## Nginx配置

### 1. 前端静态文件服务

```nginx
server {
    listen 80;
    server_name longmen.example.com;
    
    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # 前端静态文件
    location / {
        root /var/www/longmen-inn/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket代理
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. HTTPS配置（生产环境）

```nginx
server {
    listen 443 ssl http2;
    server_name longmen.example.com;
    
    # SSL证书
    ssl_certificate /etc/nginx/ssl/longmen.crt;
    ssl_certificate_key /etc/nginx/ssl/longmen.key;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    
    # 其他配置与HTTP相同...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name longmen.example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Docker部署

### 1. 项目结构

```
longmen-inn-system/
├── docker-compose.yml
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── frontend/
│   │   └── Dockerfile
│   └── nginx/
│       ├── Dockerfile
│       └── nginx.conf
└── ...
```

### 2. 后端Dockerfile

```dockerfile
# docker/backend/Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/app ./app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 前端Dockerfile

```dockerfile
# docker/frontend/Dockerfile
FROM node:20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY frontend/package*.json ./
RUN npm ci

# 复制源代码
COPY frontend/ ./

# 构建
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: longmen-db
    environment:
      POSTGRES_DB: longmen_inn_db
      POSTGRES_USER: longmen_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - longmen-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U longmen_user -d longmen_inn_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: longmen-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - longmen-network
    command: redis-server --appendonly yes

  # 后端API服务
  backend:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: longmen-backend
    environment:
      - DATABASE_URL=postgresql://longmen_user:${DB_PASSWORD:-changeme}@db:5432/longmen_inn_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - DEBUG=false
    volumes:
      - ./backend/app:/app/app
      - uploads:/app/uploads
    ports:
      - "8000:8000"
    networks:
      - longmen-network
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  # 前端Nginx服务
  frontend:
    build:
      context: .
      dockerfile: docker/frontend/Dockerfile
    container_name: longmen-frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - longmen-network
    depends_on:
      - backend
    restart: unless-stopped

  # Celery任务队列
  celery-worker:
    build:
      context: .
      dockerfile: docker/backend/Dockerfile
    container_name: longmen-celery
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://longmen_user:${DB_PASSWORD:-changeme}@db:5432/longmen_inn_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
    volumes:
      - ./backend/app:/app/app
    networks:
      - longmen-network
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads:

networks:
  longmen-network:
    driver: bridge
```

### 5. 部署命令

```bash
# 1. 克隆项目
git clone https://github.com/your-org/longmen-inn-system.git
cd longmen-inn-system

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件，配置密码和密钥

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 执行数据库迁移
docker-compose exec backend alembic upgrade head

# 6. 初始化数据
docker-compose exec backend python scripts/init_data.py
```

---

## 环境变量配置

### 后端环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `APP_NAME` | 否 | 龙门客栈业务管理系统 | 应用名称 |
| `APP_VERSION` | 否 | 1.0.0 | 应用版本 |
| `DEBUG` | 否 | false | 调试模式 |
| `SECRET_KEY` | 是 | - | 应用密钥（用于JWT签名） |
| `HOST` | 否 | 0.0.0.0 | 服务监听地址 |
| `PORT` | 否 | 8000 | 服务