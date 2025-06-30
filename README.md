# 案例改编专家 🤖

基于AI的案例改编和题目生成专家系统，使用OpenRouter API提供多模型支持。

## ✨ 功能特性

### 🎯 核心功能
- **智能案例改编**：基于用户提供的知识点、学习目标和场景，智能改编教学案例
- **自动题目生成**：根据案例内容生成多种题型的配套题目
- **多难度支持**：支持初级、中级、高级三种难度等级
- **多模型选择**：支持GPT-4o、Claude-3等多种AI模型

### 👨‍💼 管理功能
- **用户管理**：UUID-based用户身份识别
- **对话历史**：完整的对话记录和追溯
- **案例库管理**：案例的存储、检索和管理
- **使用统计**：API调用统计和成本分析

### 🛡️ 安全特性
- **API密钥加密**：用户API密钥安全存储
- **权限控制**：管理员权限分离
- **数据隔离**：用户数据完全隔离

## 🏗️ 技术架构

### 后端技术栈
- **框架**：Flask + SQLAlchemy
- **数据库**：SQLite
- **AI集成**：OpenRouter API
- **API设计**：RESTful风格

### 前端技术栈
- **框架**：React 18 + Vite
- **UI组件**：Ant Design
- **路由**：React Router
- **状态管理**：React Hooks

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 获取OpenRouter API密钥

访问 [OpenRouter](https://openrouter.ai/) 注册并获取API密钥。

### 2. 配置环境变量

首次运行时，系统会自动创建 `.env` 配置文件，您需要填入以下关键配置：

```bash
# 必填：您的OpenRouter API密钥
OPENROUTER_API_KEY=your_api_key_here

# 可选：默认模型（推荐使用成本较低的模型）
DEFAULT_MODEL=gpt-4o-mini

# 可选：默认用户配置
DEFAULT_USER_UUID=your_uuid_here
DEFAULT_USER_NICKNAME=您的昵称
```

完整的环境变量配置说明：

```bash
# ===== OpenRouter API 配置 =====
OPENROUTER_API_KEY=your_openrouter_api_key_here  # 必填
DEFAULT_MODEL=gpt-4o-mini                         # 默认AI模型

# ===== 应用配置 =====
FLASK_DEBUG=true                                  # 开发模式
SECRET_KEY=your-secret-key-here                   # 应用密钥
DATABASE_URL=sqlite:///case_creator.db            # 数据库路径

# ===== 服务端口配置 =====
BACKEND_PORT=8865                                 # 后端端口
FRONTEND_PORT=8866                                # 前端端口

# ===== 用户配置（可选） =====
DEFAULT_USER_UUID=                                # 默认用户UUID
DEFAULT_USER_NICKNAME=案例改编用户                # 默认用户昵称

# ===== 系统配置 =====
MAX_DAILY_REQUESTS=100                            # 每日请求限制
ENABLE_REGISTRATION=true                          # 是否允许注册
MAINTENANCE_MODE=false                            # 维护模式
LOG_LEVEL=INFO                                    # 日志级别
```

### 3. 启动系统

```bash
# 克隆项目
git clone <repository-url>
cd case-creator

# 运行启动脚本
chmod +x start.sh
./start.sh
```

启动脚本会自动：
- 创建和配置 `.env` 文件
- 检查Python和Node.js环境
- 创建Python虚拟环境
- 安装后端和前端依赖
- 启动后端服务（端口8865）
- 启动前端服务（端口8866）

### 4. 访问系统

- **前端界面**：http://localhost:8866
- **后端API**：http://localhost:8865
- **管理面板**：http://localhost:8866/admin

## 📖 使用指南

### 1. 用户设置
首次使用需要在设置页面配置：
- UUID（用户唯一标识）
- OpenRouter API密钥
- 默认AI模型

### 2. 案例改编
在主页填写以下信息：
- **知识点内容**：详细描述案例涉及的知识点
- **学习目标**：明确的教学目标
- **案例场景**：应用场景或行业背景
- **参考材料**：现有案例材料（可选）
- **题目设置**：是否生成题目及难度要求

### 3. 结果查看
系统将生成：
- 改编后的完整案例
- 配套的练习题目（如需要）
- 详细的答案解析

## 📊 API文档

### 核心接口

#### 执行工作流
```http
POST /api/workflow/execute
Content-Type: application/json

{
  "user_uuid": "用户UUID",
  "knowledgePoints": "知识点内容",
  "learningObjectives": "学习目标",
  "caseScenario": "案例场景",
  "caseMaterials": "参考材料（可选）",
  "yes_or_no": "是否生成题目",
  "questionType": "题目类型及数量",
  "difficultyLevel": "难度等级"
}
```

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "uuid": "用户UUID",
  "nickname": "用户昵称",
  "api_key": "OpenRouter API密钥",
  "model_name": "默认模型"
}
```

### 更多API
详细的API文档请参考代码中的路由定义。

## 🗄️ 数据库设计

### 核心表结构
- **users**：用户信息表
- **conversations**：对话会话表
- **messages**：消息记录表
- **cases**：案例库表
- **api_usage**：API使用统计表
- **system_config**：系统配置表

## 🔧 配置说明

### 环境变量
```bash
# Flask配置
FLASK_DEBUG=true
SECRET_KEY=your-secret-key

# 数据库配置
DATABASE_URL=sqlite:///case_creator.db

# OpenRouter配置
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### 系统配置
系统支持动态配置管理，主要配置项：
- 应用名称和版本
- 用户每日请求限制
- 默认AI模型
- 缓存设置
- 日志级别

## 📈 开发路线图

### 第一阶段 ✅
- [x] 基础架构搭建
- [x] 核心工作流引擎
- [x] OpenRouter API集成
- [x] 基础前端界面

### 第二阶段 🚧
- [ ] 完整的案例改编功能
- [ ] 题目生成优化
- [ ] 用户认证系统
- [ ] 对话历史管理

### 第三阶段 📋
- [ ] 管理员功能完善
- [ ] 案例库管理
- [ ] 数据统计分析
- [ ] 导入导出功能

### 第四阶段 🎯
- [ ] 性能优化
- [ ] 安全加固
- [ ] 部署自动化
- [ ] 监控告警

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 🔧 手动配置

如果您更喜欢手动配置：

### 后端配置

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行后端
python3 run.py
```

### 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🎯 环境变量详解

### 优先级说明

系统按以下优先级读取配置：

1. **用户设置**：用户在界面中配置的API密钥和模型
2. **环境变量**：`.env` 文件中的配置
3. **默认值**：系统内置的默认配置

这意味着：
- 如果用户没有配置API密钥，系统会使用环境变量中的 `OPENROUTER_API_KEY`
- 如果用户没有选择模型，系统会使用环境变量中的 `DEFAULT_MODEL`
- 新用户注册时会自动使用环境变量中的默认配置

### 模型选择建议

| 模型 | 特点 | 适用场景 | 成本 |
|------|------|----------|------|
| gpt-4o-mini | 快速、经济 | 日常案例改编 | 低 |
| gpt-4o | 性能强大 | 复杂案例分析 | 中 |
| claude-3-haiku | 快速响应 | 简单文本处理 | 低 |
| claude-3-sonnet | 平衡性能 | 综合案例处理 | 中 |
| claude-3-opus | 最强性能 | 高质量创作 | 高 |

## 🚨 故障排除

### 常见问题

1. **API密钥错误**
   ```bash
   错误：API密钥未设置，请在环境变量或用户设置中配置OpenRouter API密钥
   ```
   解决方案：
   - 检查 `.env` 文件中的 `OPENROUTER_API_KEY`
   - 确认API密钥有效且有足够余额
   - 在用户设置页面重新配置API密钥

2. **端口冲突**
   ```bash
   错误：Address already in use
   ```
   解决方案：
   - 修改 `.env` 中的 `BACKEND_PORT` 和 `FRONTEND_PORT`
   - 或者终止占用端口的进程

3. **Python命令未找到**
   ```bash
   错误：zsh: command not found: python
   ```
   解决方案：
   - 确保安装了Python 3.8+
   - 使用 `python3` 而不是 `python`
   - 检查Python是否添加到PATH

4. **前端启动失败**
   ```bash
   错误：npm error code ENOENT
   ```
   解决方案：
   - 确保在 `frontend` 目录下运行 `npm run dev`
   - 先运行 `npm install` 安装依赖
   - 检查Node.js和npm版本

5. **数据库连接错误**
   ```bash
   错误：database is locked
   ```
   解决方案：
   - 停止所有服务进程
   - 删除 `backend/instance/case_creator.db-journal` 文件
   - 重新启动服务

### 环境检查命令

```bash
# 检查Python版本
python3 --version

# 检查Node.js版本
node --version
npm --version

# 检查端口占用
lsof -i :8865  # 后端端口
lsof -i :8866  # 前端端口

# 查看系统进程
ps aux | grep python
ps aux | grep node
```

### 日志查看

- **后端日志**：控制台输出
- **前端日志**：浏览器开发者工具控制台
- **API调用日志**：数据库中的 `api_usage` 表

### 重置系统

如果遇到严重问题，可以重置系统：

```bash
# 停止所有服务
pkill -f "python.*run.py"
pkill -f "npm.*dev"

# 删除虚拟环境
rm -rf backend/venv

# 删除前端依赖
rm -rf frontend/node_modules

# 重新启动
./start.sh
```

## 📚 API调试经验总结

在开发过程中，我们遇到了一系列API调用问题，经过反复调试最终解决。以下是宝贵的经验总结，为后续开发提供参考：

### 🔍 问题1：字符编码异常

**现象：**
```
'latin-1' codec can't encode characters in position 0-5: ordinal not in range(256)
```

**根本原因：**
- Python `requests` 库在发送包含中文字符的JSON数据时，默认使用 `latin-1` 编码
- OpenRouter API需要正确的UTF-8编码才能处理中文内容

**解决方案：**
```python
# 修改前 - 使用json参数（可能导致编码问题）
response = requests.post(url, headers=headers, json=payload)

# 修改后 - 显式指定UTF-8编码
response = requests.post(
    url,
    headers=headers,
    data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
)

# 同时更新请求头
headers = {
    "Content-Type": "application/json; charset=utf-8",  # 显式指定编码
    "X-Title": "Case Creator Expert"  # 避免中文标题
}
```

**经验教训：**
- 处理多语言内容时，始终显式指定UTF-8编码
- 避免在HTTP头部使用非ASCII字符
- 使用 `ensure_ascii=False` 确保中文字符正确序列化

### 🔍 问题2：环境变量加载失败

**现象：**
- API密钥已配置但系统提示未设置
- 配置的默认模型没有生效

**根本原因：**
- `.env` 文件位于项目根目录，但 `load_dotenv()` 在后端子目录中执行
- 相对路径导致无法找到正确的 `.env` 文件

**解决方案：**
```python
# 修改前 - 没有指定路径
load_dotenv()

# 修改后 - 计算正确的.env文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)
```

**经验教训：**
- 始终使用绝对路径加载配置文件
- 考虑项目结构层次，计算正确的相对路径
- 在开发环境中验证环境变量是否正确加载

### 🔍 问题3：用户模型优先级逻辑错误

**现象：**
- 环境变量配置了 `google/gemini-2.5-flash-lite-preview-06-17`
- 但系统实际使用了 `gpt-4o-mini`

**根本原因：**
- 用户模型的默认值覆盖了环境变量配置
- 优先级逻辑不正确

**解决方案：**
```python
# 修改前 - 错误的优先级逻辑
def get_preferred_model(self):
    if self.model_name:
        return self.model_name
    return current_app.config.get('DEFAULT_MODEL', 'gpt-4o-mini')

# 修改后 - 正确的优先级逻辑  
def get_preferred_model(self):
    # 如果用户有个人设置且不是默认值，使用用户设置
    if self.model_name and self.model_name != 'gpt-4o-mini':
        return self.model_name
    # 否则优先使用环境变量配置
    return current_app.config.get('DEFAULT_MODEL', 'gpt-4o-mini')
```

**经验教训：**
- 明确定义配置优先级：用户设置 > 环境变量 > 系统默认值
- 区分"用户显式设置"和"系统默认值"
- 为新用户提供合理的默认配置

### 🔍 问题4：跨域配置滞后

**现象：**
- 前端端口频繁变化（8866→8867→8868→8869→8871）
- 出现CORS跨域错误

**根本原因：**
- 开发环境中端口经常冲突
- 后端CORS配置没有及时更新

**解决方案：**
```python
# 动态CORS配置，支持多个端口
CORS_ORIGINS = [
    f"http://localhost:{FRONTEND_PORT}",
    f"http://127.0.0.1:{FRONTEND_PORT}",
    "http://localhost:8866",  # 默认端口
    "http://localhost:8867",  # 备用端口1  
    "http://localhost:8868",  # 备用端口2
    "http://localhost:8869",  # 备用端口3
    "http://localhost:8871",  # 备用端口4
]
```

**经验教训：**
- 为开发环境预配置多个端口
- 考虑使用通配符或动态CORS配置
- 在配置文件中集中管理端口设置

### 🔍 问题5：前端废弃警告

**现象：**
```
(node:61152) [DEP0060] DeprecationWarning: The `util._extend` API is deprecated. Please use Object.assign() instead.
```

**根本原因：**
- Node.js依赖包使用了过时的API
- 开发环境显示了所有警告信息

**解决方案：**
```json
{
  "scripts": {
    "dev": "NODE_NO_WARNINGS=1 vite"
  }
}
```

**经验教训：**
- 对于第三方包的废弃警告，可以选择性屏蔽
- 关注但不必立即修复非关键的依赖警告
- 定期更新依赖包版本

### 🛠️ 调试最佳实践

1. **分层调试法**
   ```bash
   # 1. 验证配置加载
   python3 -c "from app.config import Config; print(Config.OPENROUTER_API_KEY[:10])"
   
   # 2. 测试API连通性  
   curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models
   
   # 3. 测试应用接口
   curl -X POST http://localhost:8865/api/workflow/execute -H "Content-Type: application/json" -d '{...}'
   ```

2. **添加调试日志**
   ```python
   # 在关键节点添加调试输出
   print(f"DEBUG: API密钥长度: {len(api_key) if api_key else 0}")
   print(f"DEBUG: 使用模型: {model_name}")
   print(f"DEBUG: 请求数据: {payload}")
   ```

3. **错误信息保留**
   ```python
   try:
       response = requests.post(...)
   except Exception as e:
       print(f"DEBUG: API调用异常: {str(e)}")
       return {"success": False, "error": str(e)}
   ```

### 📋 调试检查清单

在遇到API调用问题时，按以下顺序检查：

- [ ] ✅ 环境变量是否正确加载
- [ ] ✅ API密钥是否有效且有余额  
- [ ] ✅ 模型名称是否正确
- [ ] ✅ 请求数据编码是否正确
- [ ] ✅ 网络连接是否正常
- [ ] ✅ CORS配置是否匹配当前端口
- [ ] ✅ 错误日志是否提供有用信息

通过系统化的调试方法和经验积累，类似问题在未来可以更快速地定位和解决。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息

## 📞 联系方式

- 项目地址：[GitHub Repository]
- 需要帮助：请查看项目文档或提交Issue
- 问题反馈：[Issues]
- 邮箱联系：[Email]

## 🙏 致谢

- [OpenRouter](https://openrouter.ai/) - 提供AI模型API服务
- [Ant Design](https://ant.design/) - 优秀的React UI组件库
- [Flask](https://flask.palletsprojects.com/) - 轻量级Python Web框架

---

**⭐ 如果这个项目对您有帮助，请给个Star！** 