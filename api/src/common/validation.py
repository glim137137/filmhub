import re
import bcrypt
from common.message import Message
from common.exception import ValidationException
from common.uilts import PasswordUitls
from models.core_models import User, Tag
import bcrypt


class SignValidation:

    @staticmethod
    def v_signup_dto(dto: dict):
        """
        Validate the sign up dto
        """
        username = dto.get('username')
        email = dto.get('email')
        password = dto.get('password')

        if not username:
            raise ValidationException(Message.USERNAME_REQUIRED)
        if not email:
            raise ValidationException(Message.EMAIL_REQUIRED)
        if not password:
            raise ValidationException(Message.PASSWORD_REQUIRED)

        # check username
        if len(username) > 128:
            raise ValidationException(Message.USERNAME_TOO_LONG)
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidationException(Message.USERNAME_ALREADY_EXISTS)
        # check email
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationException(Message.EMAIL_ALREADY_EXISTS)
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationException(Message.EMAIL_FORMAT_INVALID)
        if len(email) > 128:
            raise ValidationException(Message.EMAIL_TOO_LONG)
        # check password
        if not PasswordUitls.is_strong_password(password):
            raise ValidationException(Message.PASSWORD_NOT_STRONG)
        if len(password) > 128:
            raise ValidationException(Message.PASSWORD_TOO_LONG)

        return username, email, password

    @staticmethod
    def v_signin_dto(dto: dict):
        """
        Validate the sign in dto

        Args:
            dto: uid(email or username), password
        """

        uid = dto.get('uid')
        password = dto.get('password')

        if not uid:
            raise ValidationException(Message.UID_REQUIRED)
        if not password:
            raise ValidationException(Message.PASSWORD_REQUIRED)

        # check uid
        if len(uid) > 128:
            raise ValidationException(Message.UID_TOO_LONG)
        user = User.query.filter_by(username=uid).first()
        if not user:
            user = User.query.filter_by(email=uid).first()
        if not user:
            raise ValidationException(Message.USER_NOT_FOUND)

        # check password
        if not bcrypt.checkpw(password.encode(), user.password):
            raise ValidationException(Message.PASSWORD_NOT_MATCH)

        return uid, password

class UserValidation:

    @staticmethod
    def v_update_user_dto(user_id: int, dto: dict):
        """
        Validate update dto. Fields are optional.
        
        Args:
            dto: {username, email, bio}
        """
        username = dto.get('username')
        email = dto.get('email')

        if username:
            if len(username) > 128:
                raise ValidationException(Message.USERNAME_TOO_LONG)
            user = User.query.filter_by(username=username).first()
            if user and getattr(user, "id", None) != int(user_id):
                raise ValidationException(Message.USERNAME_ALREADY_EXISTS)

        if email:
            if len(email) > 128:
                raise ValidationException(Message.EMAIL_TOO_LONG)
            user = User.query.filter_by(email=email).first()
            if user and getattr(user, "id", None) != int(user_id):
                raise ValidationException(Message.EMAIL_ALREADY_EXISTS)
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationException(Message.EMAIL_FORMAT_INVALID)

        return dto



    @staticmethod
    def v_change_password_dto(user_id: int, dto: dict):
        """
        Validate change password dto: requires current_password and new_password.

        Args:
            dto: {current_password, new_password}
        """
        old_password = dto.get('current_password')
        new_password = dto.get('new_password')

        if not old_password:
            raise ValidationException(Message.PASSWORD_REQUIRED)
        if not new_password:
            raise ValidationException(Message.PASSWORD_REQUIRED)
        if len(old_password) > 128:
            raise ValidationException(Message.PASSWORD_TOO_LONG)
        if len(new_password) > 128:
            raise ValidationException(Message.PASSWORD_TOO_LONG)
        if not PasswordUitls.is_strong_password(new_password):
            raise ValidationException(Message.PASSWORD_NOT_STRONG)

        user = User.query.get(user_id)
        if not bcrypt.checkpw(old_password.encode(), user.password):
            raise ValidationException(Message.PASSWORD_NOT_MATCH)

        return old_password, new_password

    @staticmethod
    def v_delete_user_dto(user_id: int, dto: dict):
        """
        Validate delete account dto: requires password confirmation.
        """
        password = dto.get('password')
        if not password:
            raise ValidationException(Message.PASSWORD_REQUIRED)
        user = User.query.get(user_id)
        if not bcrypt.checkpw(password.encode(), user.password):
            raise ValidationException(Message.PASSWORD_NOT_MATCH)
        return True




class FilmValidation:

    @staticmethod
    def v_search_dto(dto: dict):
        """
        Validate search DTO: expects {'keyword': '<text>'}
        """
        if not dto or not isinstance(dto, dict):
            raise ValidationException(Message.INVALID)
        keyword = dto.get('keyword')
        if keyword is None or (isinstance(keyword, str) and not keyword.strip()):
            raise ValidationException(Message.KEYWORD_REQUIRED)
        return dto

    @staticmethod
    def v_favorite_dto(dto: dict):
        """
        Validate favorite DTO: expects {'film_id': int}
        """
        if not dto or not isinstance(dto, dict):
            raise ValidationException(Message.INVALID)
        film_id = dto.get('film_id')
        if film_id is None:
            raise ValidationException(Message.FILM_ID_REQUIRED)
        try:
            film_id = int(film_id)
        except Exception:
            raise ValidationException(Message.FILM_ID_MUST_INT)
        return film_id

    @staticmethod
    def v_rating_dto(dto: dict):
        """
        Validate rating DTO: expects {'film_id': int, 'rating': int}
        """
        if not dto or not isinstance(dto, dict):
            raise ValidationException(Message.INVALID)
        film_id = dto.get('film_id')
        rating = dto.get('rating')
        if film_id is None:
            raise ValidationException(Message.FILM_ID_REQUIRED)
        if rating is None:
            raise ValidationException(Message.RATING_REQUIRED)
        try:
            film_id = int(film_id)
        except Exception:
            raise ValidationException(Message.FILM_ID_MUST_INT)
        try:
            rating = int(rating)
        except Exception:
            raise ValidationException(Message.RATING_MUST_INT)
        if rating < 0 or rating > 10:
            raise ValidationException(Message.RATING_RANGE)
        return film_id, rating

class TagValidation:
    @staticmethod
    def v_tag_dto(dto: dict):
        """
        Validate search DTO: expects {'keyword': '<text>'}
        """
        tag_name = dto.get("name")
        # tag name is required
        if not tag_name:
            raise ValidationException(Message.TAG_NAME_REQUIRED)
        # tag not too long
        if len(tag_name) > 128:
            raise ValidationException(Message.TAG_TOO_LONG)
        return tag_name


class PostValidation:
    @staticmethod
    def v_create_post_dto(dto: dict):
        title = dto.get('title')
        if not title:
            raise ValidationException(Message.TITLE_REQUIRED)
        if len(title) > 255:
            raise ValidationException(Message.TITLE_TOO_LONG)
        # tags optional but if present must be list
        tags = dto.get('tags')
        if tags is not None and not isinstance(tags, list):
            raise ValidationException(Message.TAGS_MUST_BE_LIST)
        return dto

    @staticmethod
    def v_update_post_dto(dto: dict):
        if not dto or not isinstance(dto, dict):
            raise ValidationException(Message.INVALID)
        if 'title' in dto and dto.get('title') is not None and len(dto.get('title')) > 255:
            raise ValidationException(Message.TITLE_TOO_LONG)
        if 'tags' in dto and dto.get('tags') is not None and not isinstance(dto.get('tags'), list):
            raise ValidationException(Message.TAGS_MUST_BE_LIST)
        return dto


class CommentValidation:
    @staticmethod
    def v_create_comment_dto(dto: dict):
        if not dto or not isinstance(dto, dict):
            raise ValidationException(Message.INVALID)
        content = dto.get('content')
        if not content or not str(content).strip():
            raise ValidationException(Message.CONTENT_REQUIRED)
        return dto
