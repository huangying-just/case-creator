# 案例改编专家 - 部署指南

## 🚀 快速部署

### 本地开发环境

```bash
# 使用一键启动脚本
chmod +x start.sh
./start.sh
```

### Docker 容器环境

```bash
# 使用Docker专用启动脚本
chmod +x docker-start.sh
./docker-start.sh
```

## 📋 部署方式对比

| 环境 | 启动脚本 | 适用场景 | 特点 |
|------|----------|----------|------|
| 本地开发 | `start.sh` | 开发调试 | 自动检测环境，支持热重载 |
| Docker容器 | `docker-start.sh` | 生产部署 | 容器优化，自动重启，服务监控 |

## 🔧 手动部署

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（如果不存在）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 启动服务
python3 run.py
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🌐 外网访问配置

### 1. 前端配置（已完成）

前端已配置为支持外网访问：
- `vite.config.js` 中设置 `host: '0.0.0.0'`
- `package.json` 中添加 `--host 0.0.0.0` 参数
- 配置了 `allowedHosts` 支持域名访问

### 2. 后端配置（已完成）

后端已配置为支持外网访问：
- Flask应用绑定到 `0.0.0.0:8865`

### 3. 域名访问

如果使用域名访问，需要在 `frontend/vite.config.js` 中添加您的域名到 `allowedHosts` 数组：

```javascript
allowedHosts: [
  'your-domain.com',  // 添加您的域名
  'case.cflp.ai',     // 示例域名
  'localhost',
  '127.0.0.1'
]
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8865  # 后端端口
   lsof -i :8866  # 前端端口
   
   # 杀死进程
   kill -9 <PID>
   ```

2. **虚拟环境问题**
   ```bash
   # 删除虚拟环境重新创建
   rm -rf backend/venv
   cd backend
   python3 -m venv venv
   ```

3. **依赖安装失败**
   ```bash
   # 清理npm缓存
   npm cache clean --force
   
   # 删除node_modules重新安装
   rm -rf frontend/node_modules
   cd frontend && npm install
   ```

4. **Docker容器中的权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x docker-start.sh
   
   # 检查文件所有权
   chown -R www-data:www-data /app
   ```

## 🔒 安全配置

### 生产环境建议

1. **环境变量配置**
   - 设置强密码的 `SECRET_KEY`
   - 配置正确的 `OPENROUTER_API_KEY`
   - 设置 `FLASK_DEBUG=false`

2. **网络安全**
   - 配置防火墙规则
   - 使用反向代理（Nginx）
   - 启用HTTPS

3. **服务监控**
   - 使用 PM2 或 systemd 管理进程
   - 配置日志轮转
   - 设置健康检查

## 📊 服务监控

### 健康检查端点

- 后端状态：`http://localhost:8865/api/workflow/status`
- 前端页面：`http://localhost:8866`

### 日志查看

```bash
# 查看后端日志
tail -f backend.log

# 查看前端日志
tail -f frontend.log
```

## 🎯 访问地址

部署成功后，您可以通过以下地址访问：

- **前端界面**: `http://your-server:8866`
- **后端API**: `http://your-server:8865`
- **域名访问**: `http://case.cflp.ai:8866` (如已配置)

## ⚡ 性能优化

### 生产环境优化

1. **前端构建**
   ```bash
   cd frontend
   npm run build
   ```

2. **使用生产级服务器**
   - 后端：使用 Gunicorn 替代 Flask 开发服务器
   - 前端：使用 Nginx 提供静态文件服务

3. **缓存配置**
   - 启用浏览器缓存
   - 配置 CDN
   - 使用 Redis 缓存API响应 