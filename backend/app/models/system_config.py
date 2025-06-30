from datetime import datetime
from .. import db

class SystemConfig(db.Model):
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, config_key, config_value, description=None):
        self.config_key = config_key
        self.config_value = config_value
        self.description = description
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(config_key=key).first()
        return config.config_value if config else default
    
    @classmethod
    def set_config(cls, key, value, description=None):
        """设置配置值"""
        config = cls.query.filter_by(config_key=key).first()
        if config:
            config.config_value = value
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
        else:
            config = cls(config_key=key, config_value=value, description=description)
            db.session.add(config)
        
        db.session.commit()
        return config
    
    @classmethod
    def get_all_configs(cls):
        """获取所有配置"""
        configs = cls.query.all()
        return {config.config_key: config.config_value for config in configs}
    
    @classmethod
    def init_default_configs(cls):
        """初始化默认配置"""
        default_configs = [
            ('app_name', '案例改编专家', '应用名称'),
            ('app_version', '1.0.0', '应用版本'),
            ('max_daily_requests', '100', '用户每日最大请求数'),
            ('default_model', 'gpt-4o-mini', '默认AI模型'),
            ('enable_registration', 'true', '是否允许用户注册'),
            ('maintenance_mode', 'false', '维护模式'),
            ('cache_enabled', 'true', '是否启用缓存'),
            ('log_level', 'INFO', '日志级别'),
            ('backup_frequency', '24', '备份频率(小时)'),
            ('openrouter_timeout', '30', 'OpenRouter API超时时间(秒)'),
            ('max_case_length', '10000', '案例最大长度'),
            ('max_questions_count', '20', '最大题目数量'),
            ('enable_public_cases', 'true', '是否允许公开案例'),
            ('admin_email', '', '管理员邮箱'),
            ('welcome_message', '欢迎使用案例改编专家！', '欢迎消息')
        ]
        
        for key, value, desc in default_configs:
            existing = cls.query.filter_by(config_key=key).first()
            if not existing:
                config = cls(config_key=key, config_value=value, description=desc)
                db.session.add(config)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}: {self.config_value}>' 