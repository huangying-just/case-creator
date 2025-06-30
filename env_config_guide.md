# 环境变量配置指南

## 概述

案例改编专家系统支持通过环境变量进行配置，使您能够：
- 设置默认的OpenRouter API密钥
- 配置默认的AI模型
- 自定义系统行为和用户设置

## 配置文件

系统使用 `.env` 文件来管理环境变量。首次运行时，启动脚本会自动创建这个文件。

## 核心配置项

### OpenRouter API 配置

```bash
# 必填：您的OpenRouter API密钥
OPENROUTER_API_KEY=your_api_key_here

# 推荐的默认模型（成本较低）
DEFAULT_MODEL=gpt-4o-mini
```

### 服务端口配置

```bash
# 后端API服务端口
BACKEND_PORT=8865

# 前端界面端口
FRONTEND_PORT=8866
```

### 用户默认配置

```bash
# 默认用户UUID（可选）
DEFAULT_USER_UUID=

# 默认用户昵称
DEFAULT_USER_NICKNAME=案例改编用户
```

## 配置优先级

系统按以下优先级读取配置：

1. **用户个人设置** - 用户在界面中配置的API密钥和模型
2. **环境变量** - `.env` 文件中的配置
3. **系统默认值** - 代码中的硬编码默认值

### 示例场景

#### 场景1：团队共享配置
```bash
# .env 文件
OPENROUTER_API_KEY=team_shared_api_key
DEFAULT_MODEL=gpt-4o-mini
```
- 团队成员无需单独配置API密钥
- 所有用户默认使用团队指定的模型
- 个别用户仍可在设置中覆盖默认配置

#### 场景2：个人使用
```bash
# .env 文件
OPENROUTER_API_KEY=my_personal_api_key
DEFAULT_MODEL=claude-3-sonnet
DEFAULT_USER_UUID=my-fixed-uuid-123
```
- 系统自动使用您的个人API密钥
- 无需每次登录时输入UUID

## 使用建议

### 开发环境
```bash
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_REGISTRATION=true
```

### 生产环境
```bash
FLASK_DEBUG=false
SECRET_KEY=your-super-secure-secret-key
LOG_LEVEL=INFO
ENABLE_REGISTRATION=false
```

## 安全注意事项

1. **保护 .env 文件**：确保 `.env` 文件不被提交到版本控制系统
2. **API密钥安全**：定期轮换OpenRouter API密钥
3. **访问控制**：在生产环境中禁用不必要的注册功能

## 故障排除

### API密钥未生效
- 检查 `.env` 文件格式是否正确（无空格、无引号）
- 确保环境变量名称拼写正确
- 重启服务以加载新的环境变量

### 端口冲突
- 修改 `BACKEND_PORT` 和 `FRONTEND_PORT`
- 检查系统中是否有其他服务占用相同端口

### 配置不生效
- 确保 `.env` 文件位于项目根目录
- 检查文件权限，确保应用可以读取
- 重启服务以应用新配置

## 完整配置示例

```bash
# ===== OpenRouter API 配置 =====
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_MODEL=gpt-4o-mini

# ===== 应用配置 =====
FLASK_DEBUG=false
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=sqlite:///case_creator.db

# ===== 服务端口配置 =====
BACKEND_PORT=8865
FRONTEND_PORT=8866

# ===== 用户配置 =====
DEFAULT_USER_UUID=12345678-1234-1234-1234-123456789abc
DEFAULT_USER_NICKNAME=团队案例改编专家

# ===== 系统配置 =====
MAX_DAILY_REQUESTS=500
ENABLE_REGISTRATION=false
MAINTENANCE_MODE=false
LOG_LEVEL=INFO
```

## 验证配置

启动系统后，您可以通过以下方式验证配置：

1. **检查启动日志**：查看是否正确加载了环境变量
2. **API测试**：访问 `http://localhost:8865/api/workflow/status`
3. **用户设置页面**：检查是否显示了默认配置信息

## 技术支持

如果遇到配置问题，请：
1. 检查启动脚本的输出日志
2. 确认 `.env` 文件的格式和内容
3. 参考故障排除部分或提交Issue 