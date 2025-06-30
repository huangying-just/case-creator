#!/usr/bin/env python3
"""
案例改编专家 - 后端服务启动文件
"""

import os
from app import create_app
from app.models import SystemConfig

def main():
    """主函数"""
    # 创建Flask应用
    app = create_app()
    
    # 初始化默认配置
    with app.app_context():
        SystemConfig.init_default_configs()
    
    # 获取配置
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 8865)
    debug = app.config.get('DEBUG', False)
    
    print(f"""
🚀 案例改编专家启动中...
📡 服务地址: http://{host}:{port}
🔧 调试模式: {'开启' if debug else '关闭'}
📖 API文档: http://{host}:{port}/api/docs (计划中)
👨‍💼 管理面板: http://{host}:{port}/admin (计划中)
    """)
    
    # 启动应用
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")

if __name__ == '__main__':
    main() 