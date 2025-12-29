from flask import Blueprint, request, jsonify
from common.result import Result
from services.sign_service import SignService

sign_bp = Blueprint('sign', __name__, url_prefix='/api')

@sign_bp.route('/signup', methods=['POST'])
def signup():
    """
    Sign up a new user.

    Body:
        { "username": "...", "email": "...", "password": "..." }
    """
    dto = request.get_json()
    SignService.signup(dto)
    return jsonify(Result.success()), 200


@sign_bp.route('/signin', methods=['POST'])
def signin():
    """
    Sign in a user.

    Body:
        { "uid": "<username|email>", "password": "..." }
    """
    dto = request.get_json()
    token = SignService.signin(dto)
    return jsonify(Result.success(data=token)), 200
