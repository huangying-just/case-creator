from flask import Blueprint, request, jsonify
from ..models import User, Conversation, Message, Case, APIUsage
from ..services.workflow_engine import WorkflowEngine
from ..services.openrouter_service import OpenRouterService
from .. import db

bp = Blueprint('workflow', __name__, url_prefix='/api/workflow')

# 初始化服务
openrouter_service = OpenRouterService()
workflow_engine = WorkflowEngine(openrouter_service)

@bp.route('/execute', methods=['POST'])
def execute_workflow():
    """执行案例改编工作流"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['user_uuid', 'knowledgePoints', 'learningObjectives', 'caseScenario']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        # 获取或创建用户
        user = User.query.filter_by(uuid=data['user_uuid']).first()
        if not user:
            # 如果用户不存在，自动创建
            from flask import current_app
            user = User(
                uuid=data['user_uuid'],
                nickname=f"用户_{data['user_uuid'][:8]}"
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
            db.session.flush()  # 获取用户ID但不提交
        
        if not user.is_active:
            return jsonify({'error': '用户账户已被禁用'}), 403
        
        if not user.get_api_key():
            return jsonify({'error': '未配置API密钥，请在环境变量中设置OPENROUTER_API_KEY'}), 400
        
        # 创建新对话会话
        conversation = Conversation(
            user_uuid=user.uuid,
            title=f"案例改编: {data.get('caseScenario', '')[:50]}"
        )
        db.session.add(conversation)
        db.session.flush()  # 获取ID但不提交
        
        # 保存用户输入
        user_message = Message(
            conversation_id=conversation.id,
            role='user',
            content=str(data),
            workflow_step='user_input'
        )
        db.session.add(user_message)
        
        # 准备工作流输入
        workflow_input = {
            'user_uuid': user.uuid,
            'api_key': user.get_api_key(),
            'model_name': user.get_preferred_model(),
            'conversation_id': conversation.id,
            'session_id': conversation.session_id,
            **data
        }
        
        # 执行工作流
        print(f"DEBUG: 准备执行工作流，输入参数: {workflow_input}")
        result = workflow_engine.execute_workflow(workflow_input)
        print(f"DEBUG: 工作流执行结果: {result}")
        
        # 保存结果到数据库
        if result.get('case_content'):
            assistant_message = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=result['case_content'],
                workflow_step='case_generation',
                model_used=user.get_preferred_model(),
                tokens_used=result.get('tokens_used', 0)
            )
            db.session.add(assistant_message)
            
            # 保存案例到案例库
            case = Case(
                title=result.get('case_title', f"案例: {data['caseScenario']}"),
                content=result['case_content'],
                knowledge_points=data['knowledgePoints'],
                learning_objectives=data['learningObjectives'],
                case_scenario=data['caseScenario'],
                difficulty_level=data.get('difficultyLevel'),
                creator_uuid=user.uuid,
                questions=result.get('questions')
            )
            db.session.add(case)
        
        if result.get('questions'):
            questions_message = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=str(result['questions']),
                workflow_step='question_generation',
                model_used=user.get_preferred_model(),
                tokens_used=result.get('questions_tokens_used', 0)
            )
            db.session.add(questions_message)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': conversation.session_id,
            'case_content': result.get('case_content'),
            'questions': result.get('questions'),
            'case_id': case.id if 'case' in locals() else None,
            'tokens_used': result.get('total_tokens_used', 0)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'工作流执行失败: {str(e)}'}), 500

@bp.route('/conversations/<user_uuid>', methods=['GET'])
def get_user_conversations(user_uuid):
    """获取用户的对话历史"""
    try:
        # 验证用户
        user = User.query.filter_by(uuid=user_uuid).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询对话
        conversations = Conversation.query.filter_by(user_uuid=user_uuid)\
            .order_by(Conversation.updated_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'conversations': [conv.to_dict() for conv in conversations.items],
            'total': conversations.total,
            'pages': conversations.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取对话历史失败: {str(e)}'}), 500

@bp.route('/conversation/<session_id>', methods=['GET'])
def get_conversation_details(session_id):
    """获取对话详情"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({'error': '对话不存在'}), 404
        
        # 获取消息
        messages = Message.query.filter_by(conversation_id=conversation.id)\
            .order_by(Message.created_at.asc()).all()
        
        return jsonify({
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取对话详情失败: {str(e)}'}), 500

@bp.route('/conversation/<session_id>', methods=['DELETE'])
def delete_conversation(session_id):
    """删除对话"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({'error': '对话不存在'}), 404
        
        # 删除对话（级联删除消息）
        db.session.delete(conversation)
        db.session.commit()
        
        return jsonify({'message': '对话删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除对话失败: {str(e)}'}), 500

@bp.route('/regenerate', methods=['POST'])
def regenerate_content():
    """重新生成内容"""
    try:
        data = request.get_json()
        
        required_fields = ['session_id', 'step']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        conversation = Conversation.query.filter_by(session_id=data['session_id']).first()
        if not conversation:
            return jsonify({'error': '对话不存在'}), 404
        
        user = User.query.filter_by(uuid=conversation.user_uuid).first()
        if not user or not user.get_api_key():
            return jsonify({'error': '用户信息无效'}), 400
        
        # 根据步骤重新生成内容
        step = data['step']
        if step == 'case':
            # 重新生成案例
            result = workflow_engine.regenerate_case(data, user)
        elif step == 'questions':
            # 重新生成题目
            result = workflow_engine.regenerate_questions(data, user)
        else:
            return jsonify({'error': '未知的生成步骤'}), 400
        
        # 保存新消息
        new_message = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=result['content'],
            workflow_step=f'{step}_regeneration',
            model_used=user.model_name,
            tokens_used=result.get('tokens_used', 0)
        )
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'content': result['content'],
            'tokens_used': result.get('tokens_used', 0)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'重新生成失败: {str(e)}'}), 500

@bp.route('/status', methods=['GET'])
def get_workflow_status():
    """获取工作流状态"""
    try:
        return jsonify({
            'status': 'active',
            'version': '1.0.0',
            'available_models': [
                'gpt-4o',
                'gpt-4o-mini',
                'claude-3-opus',
                'claude-3-sonnet',
                'claude-3-haiku'
            ],
            'supported_features': [
                'case_adaptation',
                'question_generation',
                'difficulty_adjustment',
                'multi_question_types'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500 