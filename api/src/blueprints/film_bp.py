from flask import Blueprint, request, jsonify
from common.result import Result
from services.film_service import FilmService
from flask_jwt_extended import jwt_required, get_jwt_identity

film_bp = Blueprint('film', __name__, url_prefix='/api')

@film_bp.route('/films/<int:film_id>', methods=['GET'])
@jwt_required()
def get_film_by_id(film_id):
    """
    Get film details by id.

    Args:
        film_id: int
    """
    film = FilmService.get_film_by_id(film_id, user_id=get_jwt_identity())
    return jsonify(Result.success(data=film)), 200

@film_bp.route('/films', methods=['POST'])
@jwt_required()
def get_film_by_keyword():
    """
    Search films by keyword.

    Body:
        { "keyword": "..." }
    """
    dto = request.get_json() or {}
    data = FilmService.get_film_by_keyword(dto, user_id=get_jwt_identity())
    return jsonify(Result.success(data=data)), 200


@film_bp.route('/films/title/<string:title>', methods=['GET'])
@jwt_required()
def get_film_by_title(title):
    """
    Get film details by exact title.

    Args:
        title: string - film title (URL encoded)
    """
    film = FilmService.get_film_by_title(title, user_id=get_jwt_identity())
    return jsonify(Result.success(data=film)), 200


@film_bp.route('/films/filter', methods=['POST'])
@jwt_required()
def get_filtered_films():
    """
    Get films with multiple filters applied.

    Body:
        {
            "genre_id": int (optional),
            "year": string (optional),
            "language": string (optional),
            "page": int (default: 1),
            "per_page": int (default: 20)
        }
    """
    dto = request.get_json() or {}
    result = FilmService.get_filtered_films(dto, user_id=get_jwt_identity())
    return jsonify(Result.success(data={'films': result})), 200


@film_bp.route('/genres', methods=['GET'])
@jwt_required()
def get_all_genres():
    """
    Get all genres.

    Args:
        (no body)
    """
    genres = FilmService.get_all_genres()
    data = [g.to_dict() for g in genres] if genres else []
    return jsonify(Result.success(data=data)), 200


@film_bp.route('/films/top-rated', methods=['GET'])
@jwt_required()
def get_high_rate_films():
    """
    Get top rated films.

    Args:
        (no body) - optional 'limit' query param
    """
    data = FilmService.get_high_rate_films(user_id=get_jwt_identity())
    return jsonify(Result.success(data=data)), 200


@film_bp.route('/films/latest', methods=['GET'])
@jwt_required()
def get_latest_films():
    """
    Get latest films.

    Args:
        (no body) - optional 'limit' query param
    """
    data = FilmService.get_latest_films(user_id=get_jwt_identity())
    return jsonify(Result.success(data=data)), 200
 

@film_bp.route('/films/recommend', methods=['GET'])
@jwt_required()
def get_recommend_films():
    """
    Recommend films for the authenticated user.

    Args:
        (no body) - uses user's tags and favorites
    """
    data = FilmService.get_recommendations(get_jwt_identity())
    return jsonify(Result.success(data=data)), 200

