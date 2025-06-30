from flask import Blueprint, request, jsonify
from ..models import User, Case, APIUsage
from .. import db

bp = Blueprint('cases', __name__, url_prefix='/api/cases')

@bp.route('/search', methods=['GET'])
def search_cases():
    """搜索案例"""
    try:
        # 获取查询参数
        query = request.args.get('q', '')
        difficulty_level = request.args.get('difficulty_level')
        case_scenario = request.args.get('case_scenario')
        creator_uuid = request.args.get('creator_uuid')
        is_public = request.args.get('is_public')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建过滤条件
        filters = {}
        if difficulty_level:
            filters['difficulty_level'] = difficulty_level
        if case_scenario:
            filters['case_scenario'] = case_scenario
        if creator_uuid:
            filters['creator_uuid'] = creator_uuid
        if is_public is not None:
            filters['is_public'] = is_public.lower() == 'true'
        
        # 搜索案例
        cases_query = Case.search(query, filters)
        cases_paginated = cases_query.order_by(Case.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'cases': [case.to_summary() for case in cases_paginated.items],
            'total': cases_paginated.total,
            'pages': cases_paginated.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'搜索案例失败: {str(e)}'}), 500

@bp.route('/<int:case_id>', methods=['GET'])
def get_case(case_id):
    """获取案例详情"""
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': '案例不存在'}), 404
        
        # 增加查看次数
        case.increment_view()
        
        return jsonify({
            'case': case.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取案例失败: {str(e)}'}), 500

@bp.route('/user/<user_uuid>', methods=['GET'])
def get_user_cases(user_uuid):
    """获取用户的案例列表"""
    try:
        # 验证用户
        user = User.query.filter_by(uuid=user_uuid).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户案例
        cases = Case.query.filter_by(creator_uuid=user_uuid)\
            .order_by(Case.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'cases': [case.to_summary() for case in cases.items],
            'total': cases.total,
            'pages': cases.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取用户案例失败: {str(e)}'}), 500

@bp.route('/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    """更新案例"""
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': '案例不存在'}), 404
        
        data = request.get_json()
        
        # 验证权限（只有创建者可以编辑）
        if case.creator_uuid != data.get('user_uuid'):
            return jsonify({'error': '没有权限编辑此案例'}), 403
        
        # 更新案例信息
        if 'title' in data:
            case.title = data['title']
        if 'content' in data:
            case.content = data['content']
        if 'knowledge_points' in data:
            case.knowledge_points = data['knowledge_points']
        if 'learning_objectives' in data:
            case.learning_objectives = data['learning_objectives']
        if 'case_scenario' in data:
            case.case_scenario = data['case_scenario']
        if 'difficulty_level' in data:
            case.difficulty_level = data['difficulty_level']
        if 'questions' in data:
            case.set_questions(data['questions'])
        if 'tags' in data:
            case.set_tags(data['tags'])
        if 'is_public' in data:
            case.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'message': '案例更新成功',
            'case': case.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新案例失败: {str(e)}'}), 500

@bp.route('/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    """删除案例"""
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': '案例不存在'}), 404
        
        data = request.get_json()
        
        # 验证权限（只有创建者可以删除）
        if case.creator_uuid != data.get('user_uuid'):
            return jsonify({'error': '没有权限删除此案例'}), 403
        
        db.session.delete(case)
        db.session.commit()
        
        return jsonify({'message': '案例删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除案例失败: {str(e)}'}), 500

@bp.route('/<int:case_id>/like', methods=['POST'])
def like_case(case_id):
    """点赞案例"""
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': '案例不存在'}), 404
        
        case.increment_like()
        
        return jsonify({
            'message': '点赞成功',
            'like_count': case.like_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'点赞失败: {str(e)}'}), 500

@bp.route('/public', methods=['GET'])
def get_public_cases():
    """获取公开案例列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, view_count, like_count
        
        # 构建查询
        query = Case.query.filter_by(is_public=True)
        
        # 排序
        if sort_by == 'view_count':
            query = query.order_by(Case.view_count.desc())
        elif sort_by == 'like_count':
            query = query.order_by(Case.like_count.desc())
        else:
            query = query.order_by(Case.created_at.desc())
        
        cases = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'cases': [case.to_summary() for case in cases.items],
            'total': cases.total,
            'pages': cases.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取公开案例失败: {str(e)}'}), 500

@bp.route('/stats', methods=['GET'])
def get_cases_stats():
    """获取案例统计信息"""
    try:
        from sqlalchemy import func
        
        # 总体统计
        total_cases = Case.query.count()
        public_cases = Case.query.filter_by(is_public=True).count()
        total_views = db.session.query(func.sum(Case.view_count)).scalar() or 0
        total_likes = db.session.query(func.sum(Case.like_count)).scalar() or 0
        
        # 按难度分组统计
        difficulty_stats = db.session.query(
            Case.difficulty_level,
            func.count(Case.id).label('count')
        ).group_by(Case.difficulty_level).all()
        
        # 按场景分组统计
        scenario_stats = db.session.query(
            Case.case_scenario,
            func.count(Case.id).label('count')
        ).group_by(Case.case_scenario).limit(10).all()
        
        # 热门案例（按查看次数）
        popular_cases = Case.query.filter_by(is_public=True)\
            .order_by(Case.view_count.desc()).limit(5).all()
        
        return jsonify({
            'total': {
                'cases': total_cases,
                'public_cases': public_cases,
                'total_views': total_views,
                'total_likes': total_likes
            },
            'by_difficulty': [
                {'difficulty': stat[0], 'count': stat[1]}
                for stat in difficulty_stats
            ],
            'by_scenario': [
                {'scenario': stat[0], 'count': stat[1]}
                for stat in scenario_stats
            ],
            'popular_cases': [case.to_summary() for case in popular_cases]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500

@bp.route('/export/<user_uuid>', methods=['GET'])
def export_user_cases(user_uuid):
    """导出用户案例"""
    try:
        # 验证用户
        user = User.query.filter_by(uuid=user_uuid).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户所有案例
        cases = Case.query.filter_by(creator_uuid=user_uuid).all()
        
        # 转换为导出格式
        export_data = {
            'user_info': user.to_dict(),
            'export_time': db.func.now(),
            'cases_count': len(cases),
            'cases': [case.to_dict() for case in cases]
        }
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': f'导出案例失败: {str(e)}'}), 500 