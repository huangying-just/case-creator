from datetime import datetime
from .. import db
import json

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    knowledge_points = db.Column(db.Text)  # 关联知识点
    learning_objectives = db.Column(db.Text)  # 学习目标
    case_scenario = db.Column(db.String(200))  # 案例场景
    difficulty_level = db.Column(db.String(20))  # 难度等级: 初级/中级/高级
    creator_uuid = db.Column(db.String(36), db.ForeignKey('users.uuid'), nullable=False)
    questions = db.Column(db.Text)  # 相关题目(JSON格式)
    tags = db.Column(db.Text)  # 标签(JSON格式)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开
    view_count = db.Column(db.Integer, default=0)  # 查看次数
    like_count = db.Column(db.Integer, default=0)  # 点赞次数
    
    def __init__(self, title, content, creator_uuid, knowledge_points=None, 
                 learning_objectives=None, case_scenario=None, difficulty_level=None, 
                 questions=None, tags=None, is_public=False):
        self.title = title
        self.content = content
        self.creator_uuid = creator_uuid
        self.knowledge_points = knowledge_points
        self.learning_objectives = learning_objectives
        self.case_scenario = case_scenario
        self.difficulty_level = difficulty_level
        self.questions = json.dumps(questions) if questions else None
        self.tags = json.dumps(tags) if tags else None
        self.is_public = is_public
    
    def get_questions(self):
        """获取题目列表"""
        if self.questions:
            try:
                return json.loads(self.questions)
            except:
                return []
        return []
    
    def set_questions(self, questions):
        """设置题目列表"""
        self.questions = json.dumps(questions) if questions else None
    
    def get_tags(self):
        """获取标签列表"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []
    
    def set_tags(self, tags):
        """设置标签列表"""
        self.tags = json.dumps(tags) if tags else None
    
    def increment_view(self):
        """增加查看次数"""
        self.view_count += 1
        db.session.commit()
    
    def increment_like(self):
        """增加点赞次数"""
        self.like_count += 1
        db.session.commit()
    
    def to_dict(self, include_content=True):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'knowledge_points': self.knowledge_points,
            'learning_objectives': self.learning_objectives,
            'case_scenario': self.case_scenario,
            'difficulty_level': self.difficulty_level,
            'creator_uuid': self.creator_uuid,
            'questions': self.get_questions(),
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_public': self.is_public,
            'view_count': self.view_count,
            'like_count': self.like_count
        }
        
        if include_content:
            data['content'] = self.content
            
        return data
    
    def to_summary(self):
        """转换为摘要格式（不包含完整内容）"""
        return self.to_dict(include_content=False)
    
    @classmethod
    def search(cls, query, filters=None):
        """搜索案例"""
        cases = cls.query
        
        if query:
            cases = cases.filter(
                db.or_(
                    cls.title.contains(query),
                    cls.content.contains(query),
                    cls.knowledge_points.contains(query),
                    cls.case_scenario.contains(query)
                )
            )
        
        if filters:
            if filters.get('difficulty_level'):
                cases = cases.filter_by(difficulty_level=filters['difficulty_level'])
            if filters.get('case_scenario'):
                cases = cases.filter_by(case_scenario=filters['case_scenario'])
            if filters.get('creator_uuid'):
                cases = cases.filter_by(creator_uuid=filters['creator_uuid'])
            if filters.get('is_public') is not None:
                cases = cases.filter_by(is_public=filters['is_public'])
        
        return cases
    
    def __repr__(self):
        return f'<Case {self.id}: {self.title}>' 