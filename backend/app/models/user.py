from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .. import db
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    nickname = db.Column(db.String(100))
    api_key = db.Column(db.Text)  # 加密存储的OpenRouter API密钥
    model_name = db.Column(db.String(100), default='gpt-4o-mini')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # 关系
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    cases = db.relationship('Case', backref='creator', lazy='dynamic')
    api_usage = db.relationship('APIUsage', backref='user', lazy='dynamic')
    
    def __init__(self, uuid=None, nickname=None, api_key=None, model_name='gpt-4o-mini'):
        self.uuid = uuid or str(uuid.uuid4())
        self.nickname = nickname
        self.api_key = api_key
        self.model_name = model_name
    
    def set_api_key(self, api_key):
        """设置加密的API密钥"""
        # 这里可以加入加密逻辑
        self.api_key = api_key
    
    def get_api_key(self):
        """
        获取OpenRouter API密钥
        优先级：用户设置 > 环境变量 > None
        """
        if self.api_key:
            return self.api_key
        
        # 如果用户没有设置，尝试从环境变量获取默认值
        try:
            return current_app.config.get('OPENROUTER_API_KEY')
        except RuntimeError:
            # 如果不在应用上下文中，返回None
            return None
    
    def get_preferred_model(self):
        """
        获取首选模型
        优先级：用户设置 > 环境变量 > 默认值
        """
        # 如果用户有个人设置且不是默认值，使用用户设置
        if self.model_name and self.model_name != 'gpt-4o-mini':
            return self.model_name
        
        # 如果用户没有设置或使用默认值，尝试从环境变量获取
        try:
            return current_app.config.get('DEFAULT_MODEL', 'gpt-4o-mini')
        except RuntimeError:
            # 如果不在应用上下文中，返回默认值
            return 'gpt-4o-mini'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'nickname': self.nickname,
            'model_name': self.get_preferred_model(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'has_api_key': bool(self.get_api_key()),
            'has_personal_api_key': bool(self.api_key),  # 区分个人设置和系统默认
            'using_default_config': not bool(self.api_key or self.model_name)  # 是否使用默认配置
        }
    
    def __repr__(self):
        return f'<User {self.uuid}: {self.nickname}>' 