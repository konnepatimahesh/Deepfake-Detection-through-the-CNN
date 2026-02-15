from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.user import db, User, SearchHistory
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required():
    """
    Decorator to require admin role
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_all_users():
    """
    Get all users (admin only)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users_query = User.query.order_by(User.created_at.desc())
        pagination = users_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'success': True,
            'users': users,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required()
def get_user_details(user_id):
    """
    Get detailed information about a specific user
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's analysis history
        analyses = SearchHistory.query.filter_by(user_id=user_id)\
            .order_by(SearchHistory.timestamp.desc())\
            .limit(10)\
            .all()
        
        analysis_count = SearchHistory.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'recent_analyses': [a.to_dict() for a in analyses],
            'total_analyses': analysis_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user details: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """
    Delete a user (admin only)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent admin from deleting themselves
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user's search history
        SearchHistory.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500


@admin_bp.route('/all-history', methods=['GET'])
@admin_required()
def get_all_history():
    """
    Get all users' search history (admin only)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history_query = SearchHistory.query.order_by(SearchHistory.timestamp.desc())
        pagination = history_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        history_items = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'history': history_items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch history: {str(e)}'}), 500


@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def get_system_stats():
    """
    Get overall system statistics (admin only)
    """
    try:
        total_users = User.query.count()
        total_analyses = SearchHistory.query.count()
        
        fake_count = SearchHistory.query.filter_by(detection_result='fake').count()
        real_count = SearchHistory.query.filter_by(detection_result='real').count()
        
        image_count = SearchHistory.query.filter_by(file_type='image').count()
        video_count = SearchHistory.query.filter_by(file_type='video').count()
        
        # Get recent activity
        recent_analyses = SearchHistory.query\
            .order_by(SearchHistory.timestamp.desc())\
            .limit(5)\
            .all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_analyses': total_analyses,
                'fake_detected': fake_count,
                'real_detected': real_count,
                'images_analyzed': image_count,
                'videos_analyzed': video_count
            },
            'recent_activity': [a.to_dict() for a in recent_analyses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required()
def update_user_role(user_id):
    """
    Update user role (admin only)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Prevent admin from changing their own role
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot change your own role'}), 400
        
        data = request.get_json()
        new_role = data.get('role', '').strip().lower()
        
        if new_role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role. Must be "user" or "admin"'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User role updated to {new_role}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update role: {str(e)}'}), 500