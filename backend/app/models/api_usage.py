from datetime import datetime
from .. import db
from sqlalchemy import func

class APIUsage(db.Model):
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)  # 成本(美元)
    request_type = db.Column(db.String(50))  # 请求类型: 案例改编/题目生成/etc
    workflow_step = db.Column(db.String(100))  # 具体的工作流步骤
    session_id = db.Column(db.String(36))  # 会话ID，便于关联
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_uuid, model_name, tokens_used=0, cost=0.0, 
                 request_type=None, workflow_step=None, session_id=None):
        self.user_uuid = user_uuid
        self.model_name = model_name
        self.tokens_used = tokens_used
        self.cost = cost
        self.request_type = request_type
        self.workflow_step = workflow_step
        self.session_id = session_id
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_uuid': self.user_uuid,
            'model_name': self.model_name,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'request_type': self.request_type,
            'workflow_step': self.workflow_step,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_user_stats(cls, user_uuid, start_date=None, end_date=None):
        """获取用户统计信息"""
        query = cls.query.filter_by(user_uuid=user_uuid)
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        stats = query.with_entities(
            func.sum(cls.tokens_used).label('total_tokens'),
            func.sum(cls.cost).label('total_cost'),
            func.count(cls.id).label('total_requests')
        ).first()
        
        return {
            'total_tokens': int(stats.total_tokens or 0),
            'total_cost': float(stats.total_cost or 0),
            'total_requests': int(stats.total_requests or 0)
        }
    
    @classmethod
    def get_system_stats(cls, start_date=None, end_date=None):
        """获取系统统计信息"""
        query = cls.query
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        # 总体统计
        total_stats = query.with_entities(
            func.sum(cls.tokens_used).label('total_tokens'),
            func.sum(cls.cost).label('total_cost'),
            func.count(cls.id).label('total_requests'),
            func.count(func.distinct(cls.user_uuid)).label('active_users')
        ).first()
        
        # 按模型统计
        model_stats = query.with_entities(
            cls.model_name,
            func.sum(cls.tokens_used).label('tokens'),
            func.sum(cls.cost).label('cost'),
            func.count(cls.id).label('requests')
        ).group_by(cls.model_name).all()
        
        # 按请求类型统计
        type_stats = query.with_entities(
            cls.request_type,
            func.sum(cls.tokens_used).label('tokens'),
            func.sum(cls.cost).label('cost'),
            func.count(cls.id).label('requests')
        ).group_by(cls.request_type).all()
        
        return {
            'total': {
                'tokens': int(total_stats.total_tokens or 0),
                'cost': float(total_stats.total_cost or 0),
                'requests': int(total_stats.total_requests or 0),
                'active_users': int(total_stats.active_users or 0)
            },
            'by_model': [
                {
                    'model_name': stat.model_name,
                    'tokens': int(stat.tokens or 0),
                    'cost': float(stat.cost or 0),
                    'requests': int(stat.requests or 0)
                }
                for stat in model_stats
            ],
            'by_type': [
                {
                    'request_type': stat.request_type,
                    'tokens': int(stat.tokens or 0),
                    'cost': float(stat.cost or 0),
                    'requests': int(stat.requests or 0)
                }
                for stat in type_stats
            ]
        }
    
    def __repr__(self):
        return f'<APIUsage {self.id}: {self.user_uuid} - {self.model_name} - {self.tokens_used} tokens>' 