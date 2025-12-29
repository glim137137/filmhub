from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from common.result import Result
from services.post_service import PostService

post_bp = Blueprint('post', __name__, url_prefix='/api')


@post_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new post.

    Body:
        { "title": "...", "content": "...", "tags": ["a","b"] }
    """
    dto = request.get_json() or {}
    user_id = get_jwt_identity()
    PostService.create_post(user_id, dto)
    return jsonify(Result.success()), 200


@post_bp.route('/posts', methods=['DELETE'])
@jwt_required()
def delete_post():
    """
    Delete a post.

    Body:
        { "post_id": 123 }
    """
    dto = request.get_json() or {}
    user_id = get_jwt_identity()
    PostService.delete_post(user_id, dto)
    return jsonify(Result.success()), 200


@post_bp.route('/posts', methods=['PUT'])
@jwt_required()
def update_post():
    """
    Update a post.

    Body:
        { "post_id": 123, "title": "...", "content": "...", "tags": [...] }
        All fields optional except post_id.
    """
    dto = request.get_json() or {}
    user_id = get_jwt_identity()
    post = PostService.update_post(user_id, dto)
    return jsonify(Result.success()), 200


@post_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post_by_id(post_id):
    """
    Get post by id.

    Args:
        post_id: int
    """
    post = PostService.get_post_by_id(post_id)
    return jsonify(Result.success(data=post)), 200


@post_bp.route('/films/<int:film_id>/posts', methods=['POST'])
@jwt_required()
def get_film_posts(film_id):
    """
    Get posts related to a film.
    """
    user_id = get_jwt_identity()
    posts = PostService.get_film_posts(user_id, film_id)
    return jsonify(Result.success(data={'posts': posts})), 200


@post_bp.route('/tags/<int:tag_id>/posts', methods=['POST'])
@jwt_required()
def get_tag_posts(tag_id):
    """
    Get posts by tag with pagination.

    Body:
        { "page": 0, "page_size": 10 }
    """
    dto = request.get_json() or {}
    page = dto.get('page', 0)
    page_size = dto.get('page_size', 10)

    user_id = get_jwt_identity()
    posts, has_more = PostService.get_tag_posts(user_id, tag_id, page, page_size)
    return jsonify(Result.success(data={'posts': posts, 'has_more': has_more})), 200


@post_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    """
    Like a post.
    """
    user_id = get_jwt_identity()
    post = PostService.like_post(user_id, post_id)
    return jsonify(Result.success(data=post)), 200


@post_bp.route('/posts/like', methods=['DELETE'])
@jwt_required()
def unlike_post():
    """
    Unlike a post.

    Body:
        { "post_id": 123 }
    """
    dto = request.get_json() or {}
    user_id = get_jwt_identity()
    post = PostService.unlike_post(user_id, dto)
    return jsonify(Result.success(data=post)), 200





# comments
@post_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    """
    Create a comment on a post.

    Body:
        { "content": "..." }
    Returns:
        { "comment": { ... } }
    """
    dto = request.get_json() or {}
    user_id = get_jwt_identity()
    comment = PostService.create_comment(user_id, post_id, dto)
    return jsonify(Result.success(data={"comment": comment})), 200


@post_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """
    Delete a comment.
    """
    user_id = get_jwt_identity()
    PostService.delete_comment(user_id, comment_id)
    return jsonify(Result.success()), 200

@post_bp.route('/comments/<int:comment_id>', methods=['GET'])
@jwt_required()
def get_comment(comment_id):
    """
    Get a comment.
    """
    user_id = get_jwt_identity()
    comment = PostService.get_comment(user_id, comment_id)
    return jsonify(Result.success(data=comment)), 200

@post_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
@jwt_required()
def get_post_comments(post_id):
    """
    Get comments of a post.
    """
    user_id = get_jwt_identity()
    comments = PostService.get_post_comments(user_id, post_id)
    return jsonify(Result.success(data=comments)), 200