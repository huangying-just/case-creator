from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .routes import auth, workflow, cases, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(workflow.bp)
    app.register_blueprint(cases.bp)
    app.register_blueprint(admin.bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app 