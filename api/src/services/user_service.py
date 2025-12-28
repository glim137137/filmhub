from models.core_models import User, Tag, Film, Director, Genre
from models.relations_models import UserTag, FilmFavorite, FilmRating
from flask import current_app as app
from db import db
import os
from werkzeug.utils import secure_filename
from common.exception import ValidationException
from common.message import Message
import bcrypt
from common.validation import UserValidation, TagValidation
from sqlalchemy import func
from models.relations_models import PostTag
from services.log_service import LogService

class UserService:

    @classmethod
    def get_user_by_id(cls, user_id: int):
        """
        Get a User by id.

        Args:
            user_id: int
        Returns:
            User or None
        """
        return db.session.query(User).get(user_id)

    @classmethod
    def update_user(cls, user_id: int, dto: dict, avatar_file):
        """
        Update user fields and optionally save uploaded avatar.

        Args:
            user_id: int
            dto: { username?, email?, bio? }
            avatar_file: file or None
        Returns:
            User
        """
        UserValidation.v_update_user_dto(user_id, dto)
        user = cls.get_user_by_id(user_id)

        # handle avatar file if present (filename will be user id based)
        if avatar_file:
            filename = secure_filename(avatar_file.filename or "")
            if "." not in filename:
                raise ValidationException(Message.AVATAR_FORMAT_INVALID)
            ext = filename.rsplit(".", 1)[1].lower()
            if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
                raise ValidationException(Message.AVATAR_EXT_INVALID)

            new_filename = f"{user_id}.{ext}"
            # avatars directory relative to this file
            avatars_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "avatars"))
            os.makedirs(avatars_dir, exist_ok=True)

            # Delete old avatar file if it's not the default one
            if user.avatar_url and user.avatar_url != 'user.png':
                old_avatar_path = os.path.join(avatars_dir, user.avatar_url)
                try:
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                except Exception as e:
                    raise ValidationException(Message.AVATAR_DELETE_FAILED)

            dest_path = os.path.join(avatars_dir, new_filename)
            try:
                avatar_file.save(dest_path)
            except Exception as e:
                raise ValidationException(Message.AVATAR_SAVE_FAILED)
            user.avatar_url = new_filename

        # update other fields
        if 'username' in dto and dto['username'] is not None:
            user.username = dto['username']
        if 'email' in dto and dto['email'] is not None:
            user.email = dto['email']
        if 'bio' in dto and dto['bio'] is not None:
            user.bio = dto['bio']

        db.session.add(user)
        db.session.commit()

        LogService.log_action(user_id, f"Updated user info successfully")
        return user

    @classmethod
    def change_password(cls, user_id: int, dto: dict):
        """
        Change user's password after verifying the old password.

        Args:
            user_id: int
            dto: { current_password, new_password }
        Returns:
            True on success
        """
        cpw, npw = UserValidation.v_change_password_dto(user_id, dto)

        # hash new password
        hashed = bcrypt.hashpw(npw.encode(), bcrypt.gensalt())
        user = cls.get_user_by_id(user_id)
        user.password = hashed
        db.session.add(user)
        db.session.commit()

        LogService.log_action(user_id, f"Changed password successfully")
        return True

    @classmethod
    def delete_user(cls, user_id: int, dto: dict):
        """
        Delete user and remove avatar file if exists.

        Args:
            user_id: int
            dto: { password }
        Returns:
            True on success
        """
        UserValidation.v_delete_user_dto(user_id, dto)
        user = cls.get_user_by_id(user_id)

        # remove avatar file if not default
        avatars_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "avatars"))
        if getattr(user, "avatar_url", None) and user.avatar_url != "user.png":
            avatar_path = os.path.join(avatars_dir, user.avatar_url)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

        db.session.delete(user)
        db.session.commit()

        LogService.log_action(user_id, f"Deleted account successfully")
        return True


    @classmethod
    def get_user_tags(cls, user_id: int):
        """
        Return tags associated with a user.

        Args:
            user_id: int
        Returns:
            list[Tag]
        """
        tags = (db.session.query(Tag)
                .join(UserTag, UserTag.tag_id == Tag.id)
                .filter(UserTag.user_id == user_id)
                .all())
        return tags

    @classmethod
    def add_tag_to_user(cls, user_id: int, dto: dict):
        """
        Add a tag to the user, creating the tag if missing.

        Args:
            user_id: int
            dto: { name: str }
        Returns:
            Tag
        """
        tag_name = TagValidation.v_tag_dto(dto)
        tag_id = None
        # ensure tag exists, minimize commits
        tag = db.session.query(Tag).filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.flush()

        # avoid duplicate relation
        existing = db.session.query(UserTag).filter_by(user_id=user_id, tag_id=tag.id).first()
        if existing:
            return tag

        rel = UserTag(user_id=user_id, tag_id=tag.id)
        tag_id = tag.id
        db.session.add(rel)
        db.session.commit()

        user = cls.get_user_by_id(user_id)
        LogService.log_action(user_id, f"Added tag {tag_id} successfully")
        return tag

    @classmethod
    def recommend_user_tags(cls, user_id: int, dto: dict):
        """
        Recommend up to 5 tags based on prefix matching and usage statistics.

        Args:
            user_id: int
            dto: { keyword: str }
        Returns:
            list[str] - tag names sorted by usage frequency
        """
        from models.relations_models import UserTag, PostTag

        keyword = (dto.get('keyword') or '').strip()
        if not keyword:
            raise ValidationException(Message.KEYWORD_REQUIRED)

        # Use prefix matching (case-insensitive)
        prefix_like = f"{keyword}%"

        # Find tags that start with the keyword prefix
        matching_tags = db.session.query(Tag).filter(Tag.name.ilike(prefix_like)).all()

        if not matching_tags:
            return []

        # Get tag usage statistics from UserTag and PostTag tables
        tag_usage = {}

        for tag in matching_tags:
            # Count from UserTag (user interests)
            user_count = db.session.query(UserTag).filter(UserTag.tag_id == tag.id).count()

            # Count from PostTag (content tags)
            post_count = db.session.query(PostTag).filter(PostTag.tag_id == tag.id).count()

            # Total usage count
            total_usage = user_count + post_count
            tag_usage[tag.name] = total_usage

        # Sort tags by total usage count (descending), then by name (ascending)
        sorted_tags = sorted(tag_usage.items(), key=lambda x: (-x[1], x[0]))

        # Return up to 5 tag names
        return [tag_name for tag_name, _ in sorted_tags[:5]]

    @classmethod
    def remove_tag_from_user(cls, user_id: int, tag_id: int):
        """
        Remove a tag from the user.

        Args:
            user_id: int
            tag_id: int
        """
        # find and delete the relation
        rel = db.session.query(UserTag).filter_by(user_id=user_id, tag_id=tag_id).first()
        if rel:
            db.session.delete(rel)
            db.session.commit()
        else:
            raise ValidationException(Message.TAG_NOT_FOUND)


    @classmethod
    def get_all_tags(cls):
        """
        Get all tags ordered by popularity (post usages + user usages).

        Returns:
            list of dicts: { tag_id, name, count }
        """

        # subquery counts
        post_counts = None
        user_counts = None
        if PostTag is not None:
            post_counts = (db.session.query(PostTag.tag_id.label('tag_id'),
                                            func.count(PostTag.id).label('post_count'))
                           .group_by(PostTag.tag_id)
                           .subquery())

        user_counts = (db.session.query(UserTag.tag_id.label('tag_id'),
                                        func.count(UserTag.id).label('user_count'))
                       .group_by(UserTag.tag_id)
                       .subquery())

        total_expr = (func.coalesce(post_counts.c.post_count, 0) + func.coalesce(user_counts.c.user_count, 0)) if post_counts is not None else func.coalesce(user_counts.c.user_count, 0)

        q = db.session.query(Tag.id.label('tag_id'), Tag.name, total_expr.label('count'))
        if post_counts is not None:
            q = q.outerjoin(post_counts, post_counts.c.tag_id == Tag.id)
        q = q.outerjoin(user_counts, user_counts.c.tag_id == Tag.id)

        q = q.order_by(total_expr.desc())
        rows = q.all()
        result = []
        for r in rows:
            result.append({'tag_id': r.tag_id, 'name': r.name, 'count': int(r.count or 0)})
        return result

    @classmethod
    def add_favorite(cls, user_id: int, dto: dict):
        """
        Add a film to user's favorites.

        Args:
            user_id: int
            dto: { film_id: int }
        Returns:
            True on success
        """
        from common.validation import FilmValidation
        film_id = FilmValidation.v_favorite_dto(dto)
        film = db.session.query(Film).get(film_id)
        if not film:
            raise ValidationException(Message.FILM_NOT_FOUND)
        existing = db.session.query(FilmFavorite).filter_by(user_id=user_id, film_id=film_id).first()
        if existing:
            return True
        fav = FilmFavorite(user_id=user_id, film_id=film_id)
        db.session.add(fav)
        db.session.commit()

        user = cls.get_user_by_id(user_id)
        LogService.log_action(user_id, f"Added favorite film {film_id}")
        return True

    @classmethod
    def delete_favorite(cls, user_id: int, dto: dict):
        """
        Remove a film from user's favorites.

        Args:
            user_id: int
            dto: { film_id: int }
        Returns:
            True on success
        """
        from common.validation import FilmValidation
        film_id = FilmValidation.v_favorite_dto(dto)
        existing = db.session.query(FilmFavorite).filter_by(user_id=user_id, film_id=film_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        else:
            raise ValidationException(Message.FAVORITE_NOT_FOUND)

        LogService.log_action(user_id, f"Removed favorite film {film_id}")
        return True

    @classmethod
    def get_favorites(cls, user_id: int):
        """
        Return list of enriched film dicts the user favorited.

        Args:
            user_id: int
        Returns:
            list[dict]
        """
        from services.film_service import FilmService
        rows = db.session.query(FilmFavorite.film_id).filter_by(user_id=user_id).all()
        film_ids = [r[0] for r in rows] if rows else []
        films = []
        for fid in film_ids:
            f = db.session.query(Film).get(fid)
            if f:
                films.append(FilmService._enrich_film_dict(f, user_id=user_id))
        return films

    @classmethod
    def add_rating(cls, user_id: int, dto: dict):
        """
        Add or update rating for a film by user and update film aggregate stats.

        Args:
            user_id: int
            dto: { film_id: int, rating: int }
        Returns:
            True on success
        """
        from common.validation import FilmValidation
        film_id, rating = FilmValidation.v_rating_dto(dto)
        film = db.session.query(Film).get(film_id)
        if not film:
            raise ValidationException(Message.FILM_NOT_FOUND)

        fr = db.session.query(FilmRating).filter_by(user_id=user_id, film_id=film_id).first()
        old_avg = film.rating or 0.0
        old_count = film.vote_count or 0

        if fr:
            # update existing rating
            old_rating = fr.rating or 0
            fr.rating = rating
            # recalc average: (old_avg*count - old_rating + rating)/count
            if old_count > 0:
                new_avg = (old_avg * old_count - old_rating + rating) / old_count
            else:
                new_avg = float(rating)
            film.rating = new_avg
            db.session.add(fr)
            db.session.add(film)
            db.session.commit()
            LogService.log_action(user_id, f"Updated rating for film {film_id} to {rating}")
            return True
        else:
            # new rating
            new_count = old_count + 1
            new_avg = (old_avg * old_count + rating) / new_count if new_count > 0 else float(rating)
            new_fr = FilmRating(user_id=user_id, film_id=film_id, rating=rating)
            film.vote_count = new_count
            film.rating = new_avg
            db.session.add(new_fr)
            db.session.add(film)
            db.session.commit()
            LogService.log_action(user_id, f"Added rating {rating} for film {film_id}")
            return True

    @classmethod
    def get_rating(cls, user_id: int, film_id: int):
        """
        Get user's rating for a specific film.

        Args:
            user_id: int
            film_id: int
        Returns:
            int or None: rating value (1-10) or None if no rating
        """
        fr = db.session.query(FilmRating).filter_by(user_id=user_id, film_id=film_id).first()
        return fr.rating if fr else None


