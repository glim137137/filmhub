from flask import Blueprint, jsonify, request
from common.result import Result
from services.admin_service import AdminService
from services.log_service import LogService
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api')

def admin_required(f):
    """
    Decorator to check if the current user is an admin.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        # Check if user exists and is admin
        from services.user_service import UserService
        user = UserService.get_user_by_id(user_id)
        if not user or user.username != 'admin':
            return jsonify(Result.error('Access denied. Admin privileges required.')), 403
        return f(*args, **kwargs)
    return decorated_function

# stats
@admin_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """
    Get admin statistics.

    Returns:
        {
            "total_users": int,
            "total_posts": int,
            "total_comments": int,
            "total_films": int
        }
    """
    stats = AdminService.get_admin_stats()
    return jsonify(Result.success(data=stats)), 200

@admin_bp.route('/admin/stats/users', methods=['GET'])
@admin_required
def get_total_users():
    """
    Get total number of users.

    Returns:
        { "total_users": int }
    """
    total = AdminService.get_total_users()
    return jsonify(Result.success(data={'total_users': total})), 200

@admin_bp.route('/admin/stats/posts', methods=['GET'])
@admin_required
def get_total_posts():
    """
    Get total number of posts.

    Returns:
        { "total_posts": int }
    """
    total = AdminService.get_total_posts()
    return jsonify(Result.success(data={'total_posts': total})), 200

@admin_bp.route('/admin/stats/comments', methods=['GET'])
@admin_required
def get_total_comments():
    """
    Get total number of comments.

    Returns:
        { "total_comments": int }
    """
    total = AdminService.get_total_comments()
    return jsonify(Result.success(data={'total_comments': total})), 200

@admin_bp.route('/admin/stats/films', methods=['GET'])
@admin_required
def get_total_films():
    """
    Get total number of films.

    Returns:
        { "total_films": int }
    """
    total = AdminService.get_total_films()
    return jsonify(Result.success(data={'total_films': total})), 200

@admin_bp.route('/admin/stats/top-active-users', methods=['GET'])
@admin_required
def get_top_active_users():
    """
    Get top active users based on log activity.

    Query Parameters:
        limit: int - Number of users to return (default: 10, max: 50)

    Returns:
        { "top_users": [{user_id, username, log_count}, ...] }
    """
    limit = request.args.get('limit', 10, type=int)
    if limit < 1 or limit > 50:
        limit = 10

    top_users = AdminService.get_top_active_users(limit)
    return jsonify(Result.success(data={'top_users': top_users})), 200

# film
@admin_bp.route('/admin/films', methods=['POST'])
@admin_required
def add_film():
    """
    Add a new film with optional poster upload.

    Form data can include:
    - film_data: JSON string containing film information (title, tmdb_id, overview, release_date, duration, rating, vote_count, language, poster_url, genre_ids, director_ids)
    - poster: Image file for poster upload

    If both poster file and poster_url are provided in film_data, file takes precedence.

    Returns:
        { "film": { ... } }
    """
    import os
    from werkzeug.utils import secure_filename

    # Get form data
    dto = {}

    # Handle JSON data if provided
    json_data = request.get_json(silent=True)
    if json_data:
        dto.update(json_data)

    # Handle form data (multipart/form-data)
    if request.form:
        for key, value in request.form.items():
            if key == 'film_data':
                # Parse film_data as JSON
                import json
                try:
                    film_data = json.loads(value)
                    dto.update(film_data)
                except json.JSONDecodeError:
                    return jsonify(Result.error('Invalid film_data JSON format')), 400
            elif key not in dto:  # Don't override JSON data
                dto[key] = value

    # Get poster file if provided
    poster_file = request.files.get('poster') if request.files else None

    print(f"DEBUG: poster_file received: {poster_file}")
    if poster_file:
        print(f"DEBUG: poster filename: {poster_file.filename}")
    print(f"DEBUG: dto before processing: {dto}")

    # Validate required fields
    if not dto.get('title'):
        return jsonify(Result.error('Film title is required')), 400

    # Use service method that handles poster upload
    film = AdminService.add_film_with_poster(dto, poster_file)
    return jsonify(Result.success(data={'film': film.to_dict()})), 201

@admin_bp.route('/admin/films/<int:film_id>', methods=['DELETE'])
@admin_required
def delete_film(film_id):
    """
    Delete a film by ID.

    Args:
        film_id: int - Film ID to delete

    Returns:
        Success message
    """
    AdminService.delete_film(film_id)
    return jsonify(Result.success()), 200

@admin_bp.route('/admin/films', methods=['GET'])
@admin_required
def get_films():
    """
    Get all films with pagination for admin panel.

    Query Parameters:
        page: int - Page number (default: 1)
        per_page: int - Items per page (default: 20)
        title: str - Search by film title (optional)

    Returns:
        {
            "films": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "total_pages": int,
            "search_query": str (only if searching)
        }
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    title = request.args.get('title', '').strip()

    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    # Search or get all films
    if title:
        result = AdminService.search_films_by_title(title, page, per_page)
    else:
        result = AdminService.get_films_paginated(page, per_page)

    return jsonify(Result.success(data=result)), 200

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    Get all users with pagination for admin panel.

    Query Parameters:
        page: int - Page number (default: 1)
        per_page: int - Items per page (default: 20)
        username: str - Search by username (optional)

    Returns:
        {
            "users": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "total_pages": int,
            "search_query": str (only if searching)
        }
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    username = request.args.get('username', '').strip()

    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    # Get users
    result = AdminService.get_users_paginated(page, per_page, username)
    return jsonify(Result.success(data=result)), 200

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Delete a user by admin.

    Args:
        user_id: int - User ID to delete

    Returns:
        Success message
    """
    AdminService.delete_user_by_admin(user_id)
    return jsonify(Result.success()), 200

@admin_bp.route('/admin/users/<int:user_id>/posts', methods=['GET'])
@admin_required
def get_user_posts(user_id):
    """
    Get posts by a specific user with pagination.

    Args:
        user_id: int - User ID

    Query Parameters:
        page: int - Page number (default: 1)
        per_page: int - Items per page (default: 20)

    Returns:
        {
            "posts": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "total_pages": int,
            "user_id": int
        }
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    result = AdminService.get_user_posts_paginated(user_id, page, per_page)
    return jsonify(Result.success(data=result)), 200

@admin_bp.route('/admin/posts/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_post(post_id):
    """
    Delete a specific post by admin.

    Args:
        post_id: int - Post ID to delete

    Returns:
        Success message
    """
    AdminService.delete_post_by_admin(post_id)
    return jsonify(Result.success()), 200

@admin_bp.route('/admin/users/<int:user_id>/comments', methods=['GET'])
@admin_required
def get_user_comments(user_id):
    """
    Get comments by a specific user with pagination.

    Args:
        user_id: int - User ID

    Query Parameters:
        page: int - Page number (default: 1)
        per_page: int - Items per page (default: 20)

    Returns:
        {
            "comments": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "total_pages": int,
            "user_id": int
        }
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    result = AdminService.get_user_comments_paginated(user_id, page, per_page)
    return jsonify(Result.success(data=result)), 200

@admin_bp.route('/admin/comments/<int:comment_id>', methods=['DELETE'])
@admin_required
def delete_comment(comment_id):
    """
    Delete a specific comment by admin.

    Args:
        comment_id: int - Comment ID to delete

    Returns:
        Success message
    """
    AdminService.delete_comment_by_admin(comment_id)
    return jsonify(Result.success()), 200

# logs
@admin_bp.route('/admin/logs/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_logs(user_id):
    """
    Get logs for a specific user.

    Args:
        user_id: int - User ID

    Query Parameters:
        limit: int - Maximum number of logs to return (default: 50, max: 200)

    Returns:
        {
            "logs": [
                {
                    "id": int,
                    "user_id": int,
                    "action": str,
                    "created_at": str
                }
            ],
            "user_id": int
        }
    """
    limit = request.args.get('limit', 50, type=int)

    # Validate limit
    if limit < 1 or limit > 200:
        limit = 50

    logs = LogService.get_user_logs(user_id, limit)
    logs_data = [log.to_dict() for log in logs]

    return jsonify(Result.success(data={
        'logs': logs_data,
        'user_id': user_id
    })), 200

@admin_bp.route('/admin/logs/recent', methods=['GET'])
@admin_required
def get_recent_logs():
    """
    Get recent logs from all users with pagination.

    Query Parameters:
        page: int - Page number (default: 1)
        per_page: int - Number of logs per page (default: 50, max: 100)

    Returns:
        {
            "logs": [
                {
                    "id": int,
                    "user_id": int,
                    "username": str,
                    "action": str,
                    "created_at": str
                }
            ],
            "total": int,
            "pages": int,
            "current_page": int
        }
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 50

    result = LogService.get_recent_logs(page, per_page)

    # Convert log tuples to dictionaries
    logs_data = []
    for log, username in result['logs']:
        log_dict = log.to_dict()
        log_dict['username'] = username
        logs_data.append(log_dict)

    return jsonify(Result.success(data={
        'logs': logs_data,
        'total': result['total'],
        'pages': result['pages'],
        'current_page': result['current_page']
    })), 200

@admin_bp.route('/admin/logs/stats', methods=['GET'])
@admin_required
def get_logs_stats():
    """
    Get access statistics.

    Returns:
        {
            "today": int,
            "week": int,
            "month": int,
            "year": int
        }
    """
    stats = LogService.get_access_stats()
    return jsonify(Result.success(data=stats)), 200

