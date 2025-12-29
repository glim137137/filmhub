from flask import Blueprint, jsonify, request
from common.result import Result
from services.user_service import UserService
from flask_jwt_extended import get_jwt_identity, jwt_required

user_bp = Blueprint('user', __name__, url_prefix='/api')

@user_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_user_by_id():
    """
    Get authenticated user's info.

    Args:
        (no body) - user_id is taken from JWT identity
    """
    user = UserService.get_user_by_id(user_id=get_jwt_identity())
    data = user.to_dict()
    return jsonify(Result.success(data=data)), 200

@user_bp.route('/users/me', methods=['PUT'])
@jwt_required()
def update_user():
    """
    Update authenticated user's info.

    Body (multipart/form-data):
        username: "..."
        email: "..."
        bio: "..."
        avatar: file (optional)
    """
    # Handle both JSON and form-data requests
    if request.content_type and 'application/json' in request.content_type:
        dto = request.get_json()
    else:
        # Handle form-data
        dto = {}
        for key in request.form:
            dto[key] = request.form[key]

    avatar = request.files.get('avatar') if request.files else None
    UserService.update_user(get_jwt_identity(), dto, avatar)
    return jsonify(Result.success()), 200

@user_bp.route('/users/me/password', methods=['PUT'])
@jwt_required()
def update_password():
    """
    Change authenticated user's password.

    Body:
        { "old_password": "...", "new_password": "..." }
    """
    dto = request.get_json()
    UserService.change_password(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200

@user_bp.route('/users/me', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Delete authenticated user's account.

    Body:
        { "password": "..." }
    """
    dto = request.get_json()
    UserService.delete_user(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200



# favorites
@user_bp.route('/users/me/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    """
    Add a film to authenticated user's favorites.

    Body:
        { "film_id": 123 }
    """
    dto = request.get_json() or {}
    UserService.add_favorite(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200


@user_bp.route('/users/me/favorites', methods=['DELETE'])
@jwt_required()
def delete_favorite():
    """
    Remove a film from authenticated user's favorites.

    Body:
        { "film_id": 123 }
    """
    dto = request.get_json() or {}
    UserService.delete_favorite(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200


@user_bp.route('/users/me/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    """
    Get authenticated user's favorite films.

    Args:
        (no body) - user_id from JWT
    """
    films = UserService.get_favorites(get_jwt_identity())
    return jsonify(Result.success(data={'films': films})), 200
# ratings
@user_bp.route('/users/me/ratings', methods=['POST'])
@jwt_required()
def add_rating():
    """
    Add or update rating for a film by the authenticated user.

    Body:
        { "film_id": 123, "rating": 8 }
    """
    dto = request.get_json() or {}
    UserService.add_rating(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200


@user_bp.route('/users/me/ratings/<int:film_id>', methods=['GET'])
@jwt_required()
def get_rating(film_id):
    """
    Get authenticated user's rating for a specific film.

    Args:
        film_id: int - Film ID
    Returns:
        { "rating": int } or empty dict if no rating
    """
    rating = UserService.get_rating(get_jwt_identity(), film_id)
    return jsonify(Result.success(data={'rating': rating})), 200

# tags
@user_bp.route('/tags', methods=['GET'])
@jwt_required()
def get_all_tags():
    """
    Get popular tags ordered by usage count.

    Returns:
        { "tags": [ { "tag_id": int, "name": str, "count": int }, ... ] }
    """
    data = UserService.get_all_tags()
    return jsonify(Result.success(data={'tags': data})), 200

@user_bp.route('/users/me/tags', methods=['GET'])
@jwt_required()
def get_user_tags():
    """
    Get tags for the authenticated user.

    Args:
        (no body) - user_id from JWT
    """
    tags = UserService.get_user_tags(get_jwt_identity())
    data = [{'id': t.id, 'name': t.name} for t in tags]
    return jsonify(Result.success(data=data)), 200

@user_bp.route('/users/me/tags', methods=['POST'])
@jwt_required()
def add_user_tag():
    """
    Add a tag to the authenticated user (creates tag if missing).

    Body:
        { "name": "tagname" }
    """
    dto = request.get_json()
    UserService.add_tag_to_user(get_jwt_identity(), dto)
    return jsonify(Result.success()), 200

@user_bp.route('/users/me/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_user_tag(tag_id):
    """
    Remove a tag from the authenticated user.

    Args:
        tag_id: int - Tag ID to remove
    """
    UserService.remove_tag_from_user(get_jwt_identity(), tag_id)
    return jsonify(Result.success()), 200

@user_bp.route('/users/me/tag-tips', methods=['POST'])
@jwt_required()
def get_tags_by_keyword():
    """
    Recommend tags for the authenticated user based on keyword.

    Body:
        { "keyword": "tagname" }
    """
    dto = request.get_json()
    data = UserService.get_tags_by_keyword(get_jwt_identity(), dto)
    # data is a list of tag names
    data = [{'name': t} for t in data]
    return jsonify(Result.success(data=data)), 200

# posts and comments
@user_bp.route('/users/me/posts', methods=['GET'])
@jwt_required()
def get_user_posts():
    """
    Get authenticated user's posts with pagination.

    Query params:
        offset: int - Offset for pagination (default: 0)
        limit: int - Number of posts to fetch (default: 20)
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))

    from services.post_service import PostService
    posts = PostService.get_user_posts(get_jwt_identity(), offset, limit)
    return jsonify(Result.success(data={'posts': posts})), 200

@user_bp.route('/users/me/comments', methods=['GET'])
@jwt_required()
def get_user_comments():
    """
    Get authenticated user's comments with pagination.

    Query params:
        offset: int - Offset for pagination (default: 0)
        limit: int - Number of comments to fetch (default: 20)
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))

    from services.post_service import PostService
    comments = PostService.get_user_comments(get_jwt_identity(), offset, limit)
    return jsonify(Result.success(data={'comments': comments})), 200

@user_bp.route('/users/me/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_user_post(post_id):
    """
    Update authenticated user's post.

    Body:
        { "title": "...", "content": "...", "tags": ["tag1", "tag2"] }
    """
    dto = request.get_json()
    from services.post_service import PostService
    updated_post = PostService.update_user_post(get_jwt_identity(), post_id, dto)
    return jsonify(Result.success(data=updated_post)), 200

@user_bp.route('/users/me/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_user_comment(comment_id):
    """
    Update authenticated user's comment.

    Body:
        { "content": "..." }
    """
    dto = request.get_json()
    from services.post_service import PostService
    updated_comment = PostService.update_user_comment(get_jwt_identity(), comment_id, dto)
    return jsonify(Result.success(data=updated_comment)), 200


