import bcrypt
from flask import current_app as app
from db import db
from models.core_models import User
from common.validation import SignValidation
from common.uilts import JWTUtils
from services.log_service import LogService


class SignService:

    @classmethod
    def signup(cls, dto: dict):
        """
        Register a new user.

        Args:
            dto: { username, email, password }
        Returns:
            User
        """
        username, email, password = SignValidation.v_signup_dto(dto)

        # hash password
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # create user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        LogService.log_action(user.id, f"Registered successfully")
        return user

    @classmethod
    def signin(cls, dto: dict):
        """
        Authenticate a user and return token.

        Args:
            dto: { uid, password }
        Returns:
            dict { user: {id, username, email}, token }
        """
        uid, password = SignValidation.v_signin_dto(dto)
        user = User.query.filter_by(username=uid).first()
        if not user:
            user = User.query.filter_by(email=uid).first()

        token = JWTUtils.create_token(user)

        LogService.log_action(user.id, f"Signed in successfully")
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token
        }