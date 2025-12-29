from flask import current_app as app
from sqlalchemy.sql.functions import user
from db import db
from models.core_models import Post, Comment, Tag, User
from models.relations_models import PostTag, PostComment
from models.relations_models import FilmGenre, FilmDirector
from models.relations_models import PostLike
from models.core_models import Film, Genre, Director
from common.exception import ValidationException
from common.message import Message
from common.validation import PostValidation, CommentValidation
from datetime import datetime
from services.log_service import LogService


class PostService:

    @classmethod
    def create_post(cls, user_id: int, dto: dict):
        """
        Create a post with optional tags.

        Args:
            user_id: int author id
            dto: { title, content, tags }
        Returns:
            dict: created post (enriched)
        """
        PostValidation.v_create_post_dto(dto)
        title = dto.get('title')
        content = dto.get('content')
        tags = dto.get('tags') or []

        post = Post(user_id=user_id, title=title, content=content)
        db.session.add(post)
        db.session.flush()  # ensure post.id available without committing

        # attach tags, create missing tags; minimize commits by using flush
        for t in tags:
            if not t:
                continue
            tag = db.session.query(Tag).filter_by(name=t).first()
            if not tag:
                tag = Tag(name=t)
                db.session.add(tag)
                db.session.flush()
            rel = PostTag(post_id=post.id, tag_id=tag.id)
            db.session.add(rel)

        db.session.commit()
        LogService.log_action(user_id, f"Created post {post.id}")
        return cls._build_post_dict(post.id)

    @classmethod
    def delete_post(cls, user_id: int, dto: dict):
        """
        Delete a post and its relations.

        Args:
            user_id: int requester id
            dto: { post_id: int }
        Returns:
            True on success
        """
        post_id = dto.get('post_id')
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)
        if int(post.user_id) != int(user_id):
            raise ValidationException(Message.FORBIDDEN)

        # delete post_tags
        db.session.query(PostTag).filter_by(post_id=post_id).delete(synchronize_session=False)

        # delete comments associated with this post in batch
        comment_ids = [r[0] for r in db.session.query(PostComment.comment_id).filter_by(post_id=post_id).all()]
        if comment_ids:
            db.session.query(Comment).filter(Comment.id.in_(comment_ids)).delete(synchronize_session=False)
        # delete post_comment relations
        db.session.query(PostComment).filter_by(post_id=post_id).delete(synchronize_session=False)

        db.session.delete(post)
        db.session.commit()
        LogService.log_action(user_id, f"Deleted post {post_id}")
        return True

    @classmethod
    def update_post(cls, user_id: int, dto: dict):
        """
        Update a post's fields and tags (optional).

        Args:
            user_id: int author id
            dto: { post_id, title?, content?, tags? }
        Returns:
            dict: updated post (enriched)
        """
        post_id = dto.get('post_id')
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)
        if int(post.user_id) != int(user_id):
            raise ValidationException(Message.FORBIDDEN)

        # validate update fields
        PostValidation.v_update_post_dto(dto)

        if 'title' in dto and dto.get('title') is not None:
            post.title = dto.get('title')
        if 'content' in dto and dto.get('content') is not None:
            post.content = dto.get('content')

        # replace tags if provided (list); use flush to avoid per-tag commits
        if 'tags' in dto and isinstance(dto.get('tags'), list):
            db.session.query(PostTag).filter_by(post_id=post_id).delete()
            for t in dto.get('tags'):
                if not t:
                    continue
                tag = db.session.query(Tag).filter_by(name=t).first()
                if not tag:
                    tag = Tag(name=t)
                    db.session.add(tag)
                    db.session.flush()
                rel = PostTag(post_id=post_id, tag_id=tag.id)
                db.session.add(rel)

        db.session.add(post)
        db.session.commit()
        LogService.log_action(user_id, f"Updated post {post_id}")
        return cls._build_post_dict(post_id)

    @classmethod
    def get_post_by_id(cls, post_id: int):
        """
        Get a single post by id.

        Args:
            post_id: int
        Returns:
            dict: enriched post or {}
        """
        post = db.session.query(Post).get(post_id)
        if not post:
            return {}
        return cls._build_post_dict(post_id)

    @classmethod
    def get_film_posts(cls, user_id: int, film_id: int):
        """
        Get posts related to a film by title or tag/genre match.

        Returns:
            list of enriched posts
        """
        if not film_id:
            raise ValidationException(Message.FILM_ID_REQUIRED)
        film = db.session.query(Film).get(film_id)
        if not film:
            return []

        title = (film.title or "").strip()

        # posts where tags match film title
        posts_query = db.session.query(Post).join(PostTag, Post.id == PostTag.post_id).join(Tag, Tag.id == PostTag.tag_id).filter(
            Tag.name == title
        ).distinct()

        return [cls._build_post_dict(p.id, user_id) for p in posts_query.all()]

    @classmethod
    def get_tag_posts(cls, user_id: int, tag_id: int, page: int = 0, page_size: int = 10):
        """
        Get posts that contain a specific tag with pagination.

        Args:
            user_id: int - ID of the user making the request
            tag_id: int - ID of the tag to filter posts by
            page: int - Page number (0-based)
            page_size: int - Number of posts per page
        Returns:
            tuple: (list of enriched posts, has_more boolean)
        """
        # Get total count for pagination
        total_count = db.session.query(Post)\
            .join(PostTag, Post.id == PostTag.post_id)\
            .join(Tag, Tag.id == PostTag.tag_id)\
            .filter(Tag.id == tag_id)\
            .count()

        # Get paginated posts
        posts_query = db.session.query(Post)\
            .join(PostTag, Post.id == PostTag.post_id)\
            .join(Tag, Tag.id == PostTag.tag_id)\
            .filter(Tag.id == tag_id)\
            .order_by(Post.created_at.desc())\
            .offset(page * page_size)\
            .limit(page_size + 1)\
            .distinct()

        posts = posts_query.all()
        has_more = len(posts) > page_size

        # If we have more posts than page_size, remove the extra one
        if has_more:
            posts = posts[:-1]

        return [cls._build_post_dict(p.id, user_id) for p in posts], has_more

    @classmethod
    def like_post(cls, user_id: int, post_id: int):
        """
        Like a post. Idempotent.

        Returns: enriched post dict
        """
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)
        # check existing like
        existing = db.session.query(PostLike).filter_by(post_id=post_id, user_id=user_id).first()
        if existing:
            return cls._build_post_dict(post_id)
        like = PostLike(post_id=post_id, user_id=user_id)
        db.session.add(like)
        post.like_count = (post.like_count or 0) + 1
        db.session.add(post)
        db.session.commit()
        LogService.log_action(user_id, f"Like post {post_id}")
        return cls._build_post_dict(post_id, user_id)

    @classmethod
    def unlike_post(cls, user_id: int, dto: dict):
        """
        Remove like from a post. Idempotent.

        Body: { post_id: int }
        Returns: enriched post dict
        """
        post_id = dto.get('post_id')
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)
        existing = db.session.query(PostLike).filter_by(post_id=post_id, user_id=user_id).first()
        if not existing:
            return cls._build_post_dict(post_id)
        db.session.delete(existing)
        post.like_count = max(0, (post.like_count or 0) - 1)
        db.session.add(post)
        db.session.commit()
        LogService.log_action(user_id, f"Unlike post {post_id}")
        return cls._build_post_dict(post_id, user_id)

    @classmethod
    def create_comment(cls, user_id: int, post_id: int,dto: dict):
        """
        Create a comment on a post.

        Args:
            user_id: int
            dto: { content: str }
        Returns:
            dict: created comment (enriched)
        """
        CommentValidation.v_create_comment_dto(dto)
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)
        content = dto.get('content')
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)
        comment = Comment(user_id=user_id, content=content)
        db.session.add(comment)
        db.session.flush()
        rel = PostComment(post_id=post_id, comment_id=comment.id)
        db.session.add(rel)
        db.session.commit()
        LogService.log_action(user_id, f"Create comment on post {post_id}")
        return cls._build_comment_dict(comment.id)


    @classmethod
    def delete_comment(cls, user_id: int, comment_id: int):
        """
        Delete a comment.

        Args:
            user_id: int
            dto: { comment_id: int }
        Returns:
            True on success
        """
        if not comment_id:
            raise ValidationException(Message.COMMENT_ID_REQUIRED)
        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise ValidationException(Message.COMMENT_NOT_FOUND)
        if int(comment.user_id) != int(user_id):
            raise ValidationException(Message.FORBIDDEN)
        # remove post_comment relation(s)
        db.session.query(PostComment).filter_by(comment_id=comment_id).delete(synchronize_session=False)
        db.session.delete(comment)
        db.session.commit()
        LogService.log_action(user_id, f"Delete comment {comment_id}")
        return True

    @classmethod
    def get_comment(cls, user_id: int, comment_id: int):
        """
        Get a specific comment.

        Args:
            user_id: int - ID of the user making the request
            comment_id: int - ID of the comment to retrieve
        Returns:
            dict: enriched comment data
        """
        if not comment_id:
            raise ValidationException(Message.COMMENT_ID_REQUIRED)

        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise ValidationException(Message.COMMENT_NOT_FOUND)

        return cls._build_comment_dict(comment_id)

    @classmethod
    def get_post_comments(cls, user_id: int, post_id: int):
        """
        Get all comments for a specific post.

        Args:
            user_id: int - ID of the user making the request
            post_id: int - ID of the post to get comments for
        Returns:
            list: list of enriched comment data
        """
        if not post_id:
            raise ValidationException(Message.POST_ID_REQUIRED)

        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)

        # Get all comments for this post
        comment_relations = db.session.query(PostComment)\
            .filter(PostComment.post_id == post_id)\
            .all()

        comments = []
        for relation in comment_relations:
            comment_dict = cls._build_comment_dict(relation.comment_id)
            if comment_dict:  # Only add if comment exists
                comments.append(comment_dict)

        return comments

    @classmethod
    def update_user_post(cls, user_id: int, post_id: int, update_data: dict):
        """
        Update a post by the authenticated user.

        Args:
            user_id: int - User ID (for authorization)
            post_id: int - Post ID to update
            update_data: dict - Data to update (title, content)
        Returns:
            dict: Updated post dictionary
        """
        # Get the post
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValidationException(Message.POST_NOT_FOUND)

        # Check ownership
        if int(post.user_id) != int(user_id):
            raise ValidationException(Message.UNAUTHORIZED)

        # Update fields
        if 'title' in update_data:
            title = update_data['title'].strip()
            if not title:
                raise ValidationException(Message.CONTENT_REQUIRED)
            if len(title) > 256:
                raise ValidationException(Message.TITLE_TOO_LONG)
            post.title = title

        if 'content' in update_data:
            content = update_data['content'].strip()
            if not content:
                raise ValidationException(Message.CONTENT_REQUIRED)
            post.content = content

        # Update tags if provided
        if 'tags' in update_data:
            tags = update_data['tags'] or []
            # Remove existing tag relationships
            from models.relations_models import PostTag
            db.session.query(PostTag).filter_by(post_id=post_id).delete()

            # Add new tags
            for tag_name in tags:
                if not tag_name:
                    continue
                tag = db.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    db.session.flush()
                rel = PostTag(post_id=post_id, tag_id=tag.id)
                db.session.add(rel)

        post.updated_at = datetime.now()
        db.session.commit()
        LogService.log_action(user_id, f"Updated post {post_id}")

        # Return updated post data
        return cls._build_post_dict(post_id)

    @classmethod
    def update_user_comment(cls, user_id: int, comment_id: int, update_data: dict):
        """
        Update a comment by the authenticated user.

        Args:
            user_id: int - User ID (for authorization)
            comment_id: int - Comment ID to update
            update_data: dict - Data to update (content)
        Returns:
            dict: Updated comment dictionary
        """
        # Get the comment
        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise ValidationException(Message.COMMENT_NOT_FOUND)


        # Check ownership
        if int(comment.user_id) != int(user_id):
            raise ValidationException(Message.UNAUTHORIZED)

        # Update content
        if 'content' in update_data:
            content = update_data['content'].strip()
            if not content:
                raise ValidationException(Message.CONTENT_REQUIRED)
            comment.content = content
            comment.updated_at = datetime.now()

        db.session.commit()
        LogService.log_action(user_id, f"Updated comment {comment_id}")

        # Return updated comment data
        return cls._build_comment_dict(comment_id)

    @classmethod
    def _build_post_dict(cls, post_id: int, current_user_id: int = None):
        """
        Build enriched post dict including tags and comments.

        Args:
            post_id: int
        Returns:
            dict
        """
        post = db.session.query(Post).get(post_id)
        if not post:
            return {}
        user = db.session.query(User).get(post.user_id)
        user_info = user.to_dict() if user else {}

        # tags
        tag_rows = db.session.query(Tag.name).join(PostTag, Tag.id == PostTag.tag_id).filter(PostTag.post_id == post_id).all()
        tags = [r[0] for r in tag_rows] if tag_rows else []

        # comment count (for display purposes)
        comment_count = db.session.query(PostComment).filter_by(post_id=post_id).count()

        # check if current user liked this post (if provided)
        is_liked = False
        if current_user_id:
            like_exists = db.session.query(PostLike).filter_by(post_id=post_id, user_id=current_user_id).first()
            is_liked = bool(like_exists)

        return {
            "post_id": post.id,
            "user_id": post.user_id,
            "user_info": user_info,
            "title": post.title,
            "content": post.content,
            "tags": tags,
            "created_at": post.created_at.isoformat() if getattr(post, "created_at", None) else None,
            "updated_at": post.updated_at.isoformat() if getattr(post, "updated_at", None) else None,
            "like_count": post.like_count or 0,
            "comment_count": comment_count,
            "is_like": is_liked
        }

    @classmethod
    def _build_comment_dict(cls, comment_id: int):
        """
        Build enriched comment dict.

        Args:
            comment_id: int
        Returns:
            dict
        """
        c = db.session.query(Comment).get(comment_id)
        if not c:
            return {}
        cu = db.session.query(User).get(c.user_id)
        return {
            "comment_id": c.id,
            "user_id": c.user_id,
            "user_info": cu.to_dict() if cu else {},
            "content": c.content,
            "created_at": c.created_at.isoformat() if getattr(c, "created_at", None) else None,
            "updated_at": c.updated_at.isoformat() if getattr(c, "updated_at", None) else None,
        }

    @classmethod
    def get_user_posts(cls, user_id: int, offset: int = 0, limit: int = 20):
        """
        Get posts by a specific user with pagination.

        Args:
            user_id: int - User ID
            offset: int - Offset for pagination
            limit: int - Number of posts to fetch
        Returns:
            list: List of post dictionaries with tags, user_id, user_info
        """
        posts = db.session.query(Post)\
            .filter_by(user_id=user_id)\
            .order_by(Post.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

        result = []
        for post in posts:
            # Get user info
            user = db.session.query(User).get(post.user_id)

            # Get tags
            from models.relations_models import PostTag
            tags = db.session.query(Tag)\
                .join(PostTag)\
                .filter(PostTag.post_id == post.id)\
                .all()
            tags_list = [tag.name for tag in tags]

            # Count comments and likes
            comment_count = db.session.query(PostComment)\
                .filter_by(post_id=post.id)\
                .count()
            like_count = db.session.query(PostLike)\
                .filter_by(post_id=post.id)\
                .count()

            post_dict = {
                "post_id": post.id,
                "user_id": post.user_id,
                "user_info": user.to_dict() if user else {},
                "title": post.title,
                "content": post.content,
                "tags": tags_list,
                "created_at": post.created_at.isoformat() if getattr(post, "created_at", None) else None,
                "updated_at": post.updated_at.isoformat() if getattr(post, "updated_at", None) else None,
                "comment_count": comment_count,
                "like_count": like_count,
            }
            result.append(post_dict)

        return result

    @classmethod
    def get_user_comments(cls, user_id: int, offset: int = 0, limit: int = 20):
        """
        Get comments by a specific user with pagination.

        Args:
            user_id: int - User ID
            offset: int - Offset for pagination
            limit: int - Number of comments to fetch
        Returns:
            list: List of comment dictionaries with user_id, user_info
        """
        comments = db.session.query(Comment)\
            .filter_by(user_id=user_id)\
            .order_by(Comment.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

        result = []
        for comment in comments:
            # Get user info
            user = db.session.query(User).get(comment.user_id)

            # Get post info through PostComment relationship
            from models.relations_models import PostComment
            post_comment = db.session.query(PostComment).filter_by(comment_id=comment.id).first()
            post_title = None
            if post_comment:
                post = db.session.query(Post).get(post_comment.post_id)
                post_title = post.title if post else None

            comment_dict = {
                "comment_id": comment.id,
                "user_id": comment.user_id,
                "user_info": user.to_dict() if user else {},
                "content": comment.content,
                "post_id": post_comment.post_id if post_comment else None,
                "post_title": post_title,
                "created_at": comment.created_at.isoformat() if getattr(comment, "created_at", None) else None,
                "updated_at": comment.updated_at.isoformat() if getattr(comment, "updated_at", None) else None,
            }
            result.append(comment_dict)

        return result
