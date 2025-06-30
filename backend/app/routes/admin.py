from flask import Blueprint, request, jsonify
from ..models import User, Case, Conversation, Message, APIUsage, SystemConfig
from .. import db
from datetime import datetime, timedelta
import shutil
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        data = request.get_json() if request.method in ['POST', 'PUT'] else {}
        admin_uuid = data.get('admin_uuid') or request.headers.get('X-Admin-UUID')
        
        if not admin_uuid:
            return jsonify({'error': '需要管理员身份验证'}), 401
        
        admin = User.query.filter_by(uuid=admin_uuid, is_admin=True).first()
        if not admin:
            return jsonify({'error': '管理员权限不足'}), 403
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status')  # active, inactive, all
        
        # 构建查询
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.uuid.contains(search),
                    User.nickname.contains(search)
                )
            )
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        users = query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户列表失败: {str(e)}'}), 500

@bp.route('/stats/overview', methods=['GET'])
@admin_required
def get_system_overview():
    """获取系统概览统计"""
    try:
        from sqlalchemy import func
        
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # 案例统计
        total_cases = Case.query.count()
        public_cases = Case.query.filter_by(is_public=True).count()
        
        # 对话统计
        total_conversations = Conversation.query.count()
        total_messages = Message.query.count()
        
        # API使用统计
        api_stats = APIUsage.get_system_stats()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users
            },
            'cases': {
                'total': total_cases,
                'public': public_cases
            },
            'conversations': {
                'total': total_conversations,
                'total_messages': total_messages
            },
            'api_usage': api_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取系统统计失败: {str(e)}'}), 500 