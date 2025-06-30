from datetime import datetime
from .. import db
import uuid

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_uuid, title=None):
        self.user_uuid = user_uuid
        self.session_id = str(uuid.uuid4())
        self.title = title or f"对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.messages.count()
        }
    
    def __repr__(self):
        return f'<Conversation {self.session_id}: {self.title}>'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' 或 'assistant'
    content = db.Column(db.Text, nullable=False)
    workflow_step = db.Column(db.String(100))  # 工作流步骤标识
    model_used = db.Column(db.String(100))  # 使用的AI模型
    tokens_used = db.Column(db.Integer, default=0)  # 消耗的token数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, conversation_id, role, content, workflow_step=None, model_used=None, tokens_used=0):
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.workflow_step = workflow_step
        self.model_used = model_used
        self.tokens_used = tokens_used
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'workflow_step': self.workflow_step,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.id}: {self.role} - {self.content[:50]}...>' 