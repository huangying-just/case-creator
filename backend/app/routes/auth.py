from flask import Blueprint, request, jsonify, current_app
from ..models import User, SystemConfig
from .. import db
import uuid
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 检查是否允许注册
        if SystemConfig.get_config('enable_registration', 'true').lower() != 'true':
            return jsonify({'error': '当前不允许注册新用户'}), 403
        
        # 验证必需字段
        if not data.get('uuid'):
            return jsonify({'error': 'UUID是必需的'}), 400
        
        # 检查UUID是否已存在
        existing_user = User.query.filter_by(uuid=data['uuid']).first()
        if existing_user:
            return jsonify({'error': '用户已存在'}), 409
        
        # 创建新用户
        user = User(
            uuid=data['uuid'],
            nickname=data.get('nickname', f'用户_{data["uuid"][:8]}')
        )
        
        # 设置API密钥和模型
        if data.get('api_key'):
            user.set_api_key(data['api_key'])
        if data.get('model_name'):
            user.preferred_model = data['model_name']
        else:
            user.preferred_model = SystemConfig.get_config('default_model', 'gpt-4o-mini')
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """用户登录 - 支持多种登录方式"""
    try:
        print("=== LOGIN API CALLED ===")
        data = request.get_json()
        print(f"Request data: {data}")
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        user_uuid = data.get('user_uuid', '').strip()
        nickname = data.get('nickname', '').strip()
        password = data.get('password')
        
        # 如果没有提供UUID，但配置了默认UUID，则使用默认值
        if not user_uuid and current_app.config.get('DEFAULT_USER_UUID'):
            user_uuid = current_app.config.get('DEFAULT_USER_UUID')
            
        # 如果没有提供昵称，使用默认昵称
        if not nickname:
            nickname = current_app.config.get('DEFAULT_USER_NICKNAME', '案例改编用户')
        
        user = None
        
        # 1. 通过UUID查找用户
        if user_uuid:
            user = User.query.filter_by(uuid=user_uuid).first()
        
        # 2. 通过昵称查找用户（如果没有UUID）
        if not user and nickname:
            user = User.query.filter_by(nickname=nickname).first()
        
        # 3. 如果用户不存在，自动创建新用户（如果启用了注册）
        if not user and current_app.config.get('ENABLE_REGISTRATION', True):
            # 生成UUID（如果没有提供）
            if not user_uuid:
                user_uuid = str(uuid.uuid4())
            
            # 创建新用户
            user = User(
                uuid=user_uuid,
                nickname=nickname,
                password_hash=generate_password_hash(password) if password else None
            )
            
            # 如果配置了默认API密钥，设置给新用户
            default_api_key = current_app.config.get('OPENROUTER_API_KEY')
            if default_api_key:
                user.set_api_key(default_api_key)
                
            # 如果配置了默认模型，设置给新用户
            default_model = current_app.config.get('DEFAULT_MODEL')
            if default_model:
                user.preferred_model = default_model
            
            db.session.add(user)
            db.session.commit()
            
            # 生成访问令牌
            access_token = create_access_token(identity=str(user.id))
            
            return jsonify({
                'message': '用户创建成功并已登录',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'uuid': user.uuid,
                    'nickname': user.nickname,
                    'openrouter_api_key': user.get_api_key(),
                    'preferred_model': user.get_preferred_model(),
                    'created_at': user.created_at.isoformat()
                }
            }), 201
        
        # 4. 验证用户登录
        if user:
            # 如果设置了密码，验证密码
            if user.password_hash and password:
                if not check_password_hash(user.password_hash, password):
                    return jsonify({'error': '密码错误'}), 401
            
            # 生成访问令牌
            access_token = create_access_token(identity=str(user.id))
            
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'uuid': user.uuid,
                    'nickname': user.nickname,
                    'openrouter_api_key': user.get_api_key(),
                    'preferred_model': user.get_preferred_model(),
                    'created_at': user.created_at.isoformat()
                }
            }), 200
        
        # 5. 如果用户不存在且禁用了注册
        return jsonify({'error': '用户不存在且系统已禁用注册功能'}), 404
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@bp.route('/profile/<user_uuid>', methods=['GET'])
def get_profile(user_uuid):
    """获取用户资料"""
    try:
        user = User.query.filter_by(uuid=user_uuid).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户资料失败: {str(e)}'}), 500

@bp.route('/profile/<user_uuid>', methods=['PUT'])
def update_profile(user_uuid):
    """更新用户资料"""
    try:
        user = User.query.filter_by(uuid=user_uuid).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新用户信息
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'api_key' in data:
            user.set_api_key(data['api_key'])
        if 'model_name' in data:
            user.preferred_model = data['model_name']
        
        db.session.commit()
        
        return jsonify({
            'message': '用户资料更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新用户资料失败: {str(e)}'}), 500

@bp.route('/validate/<user_uuid>', methods=['GET'])
def validate_user(user_uuid):
    """验证用户UUID"""
    try:
        user = User.query.filter_by(uuid=user_uuid).first()
        
        if not user:
            return jsonify({'valid': False, 'message': '用户不存在'}), 404
        
        if not user.is_active:
            return jsonify({'valid': False, 'message': '用户账户已被禁用'}), 403
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'验证失败: {str(e)}'}), 500 