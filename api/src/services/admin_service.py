from models.core_models import User, Film, Post, Comment, Log
from models.relations_models import FilmGenre, FilmDirector
from db import db
from datetime import datetime
import os
from flask import current_app as app
from werkzeug.utils import secure_filename
from services.log_service import LogService

class AdminService:

    @classmethod
    def get_total_users(cls):
        """
        Get total number of users.

        Returns:
            int: Total user count
        """
        return db.session.query(User).count()

    @classmethod
    def get_total_posts(cls):
        """
        Get total number of posts.

        Returns:
            int: Total post count
        """
        return db.session.query(Post).count()

    @classmethod
    def get_total_comments(cls):
        """
        Get total number of comments.

        Returns:
            int: Total comment count
        """
        return db.session.query(Comment).count()

    @classmethod
    def get_total_films(cls):
        """
        Get total number of films.

        Returns:
            int: Total film count
        """
        return db.session.query(Film).count()

    @classmethod
    def get_admin_stats(cls):
        """
        Get all admin statistics in one call.

        Returns:
            dict: Statistics data
        """
        return {
            'total_users': cls.get_total_users(),
            'total_posts': cls.get_total_posts(),
            'total_comments': cls.get_total_comments(),
            'total_films': cls.get_total_films()
        }

    @classmethod
    def get_top_active_users(cls, limit=10):
        """
        Get top active users based on log activity.

        Args:
            limit: int - Number of top users to return

        Returns:
            list of dicts: [{user_id, username, log_count}, ...]
        """
        from sqlalchemy import func

        # Query top users by log count
        top_users = (db.session.query(
            User.id.label('user_id'),
            User.username,
            func.count(Log.id).label('log_count')
        )
        .join(Log, User.id == Log.user_id)
        .group_by(User.id, User.username)
        .order_by(func.count(Log.id).desc())
        .limit(limit)
        .all())

        result = []
        for row in top_users:
            result.append({
                'user_id': row.user_id,
                'username': row.username,
                'log_count': int(row.log_count)
            })

        return result

    @classmethod
    def add_film(cls, dto: dict):
        """
        Add a new film to the database.

        Args:
            dto: dict containing film data

        Returns:
            Film: The created film object
        """
        # Validate required fields
        if not dto.get('title'):
            raise ValueError("Film title is required")

        # Handle release_date parsing
        release_date = dto.get('release_date')
        if release_date and isinstance(release_date, str):
            try:
                from datetime import datetime
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Invalid release_date format. Expected YYYY-MM-DD")

        # Create new film
        film = Film(
            title=dto['title'],
            tmdb_id=dto.get('tmdb_id'),
            overview=dto.get('overview'),
            release_date=release_date,
            duration=dto.get('duration'),
            rating=dto.get('rating', 0.0),
            vote_count=dto.get('vote_count', 0),
            language=dto.get('language'),
            poster_url=dto.get('poster_url', 'film.jpg')
        )

        db.session.add(film)
        db.session.flush()  # Get the film ID

        # Handle genres if provided
        if dto.get('genre_ids'):
            from models.core_models import Genre
            for genre_id in dto['genre_ids']:
                genre = db.session.query(Genre).get(genre_id)
                if genre:
                    film_genre = FilmGenre(film_id=film.id, genre_id=genre_id)
                    db.session.add(film_genre)

        # Handle directors if provided
        if dto.get('director_ids'):
            from models.core_models import Director
            for director_id in dto['director_ids']:
                director = db.session.query(Director).get(director_id)
                if director:
                    film_director = FilmDirector(film_id=film.id, director_id=director_id)
                    db.session.add(film_director)

        db.session.commit()
        LogService.log_action(1, f"Admin added film {film.id}: {film.title}")  # 使用0作为admin用户ID
        return film

    @classmethod
    def add_film_with_poster(cls, dto: dict, poster_file=None):
        """
        Add a new film to the database with optional poster upload.

        Args:
            dto: dict containing film data
            poster_file: FileStorage object for poster upload (optional)

        Returns:
            Film: The created film object

        Raises:
            ValueError: If validation fails
        """
        # Handle poster file upload if provided
        if poster_file and poster_file.filename:
            try:
                # Get file extension
                if '.' not in poster_file.filename:
                    raise ValueError("Invalid file type")
                extension = poster_file.filename.rsplit('.', 1)[1].lower()

                # Generate poster filename based on title
                title = dto.get('title', '').strip()
                if not title:
                    raise ValueError("Film title is required for poster upload")

                # Sanitize title for filename
                import re
                safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
                poster_filename = f"{safe_title}.{extension}"

                # Ensure unique filename - use correct path relative to api/src
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))  # api/src/services
                posters_dir = os.path.join(current_dir, '..', 'data', 'posters')
                posters_dir = os.path.abspath(posters_dir)  # Get absolute path
                os.makedirs(posters_dir, exist_ok=True)

                print(f"DEBUG: Saving poster to directory: {posters_dir}")
                print(f"DEBUG: Poster filename: {poster_filename}")

                counter = 1
                original_filename = poster_filename
                while os.path.exists(os.path.join(posters_dir, poster_filename)):
                    name, ext = os.path.splitext(original_filename)
                    poster_filename = f"{name}_{counter}{ext}"
                    counter += 1

                # Save file with the generated filename
                file_path = os.path.join(posters_dir, poster_filename)
                poster_file.save(file_path)

                print(f"DEBUG: File saved to: {file_path}")
                print(f"DEBUG: File exists after save: {os.path.exists(file_path)}")

                dto['poster_url'] = poster_filename
            except Exception as e:
                print(f"DEBUG: Error saving poster: {str(e)}")
                raise ValueError(f"Poster upload failed: {str(e)}")
        else:
            # No poster file, use default
            dto['poster_url'] = 'film.jpg'

        # Use the existing add_film method
        return cls.add_film(dto)

    @classmethod
    def delete_film(cls, film_id: int):
        """
        Delete a film from the database.

        Args:
            film_id: int - ID of the film to delete

        Returns:
            bool: True if successful
        """
        film = db.session.query(Film).get(film_id)
        if not film:
            raise ValueError("Film not found")

        # Delete poster file if it's not the default one
        if film.poster_url and film.poster_url != 'film.jpg':
            try:
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))  # api/src/services
                poster_path = os.path.join(current_dir, '..', 'data', 'posters', film.poster_url)
                poster_path = os.path.abspath(poster_path)

                if os.path.exists(poster_path):
                    os.remove(poster_path)
                    print(f"DEBUG: Deleted poster file: {poster_path}")
            except Exception as e:
                print(f"DEBUG: Error deleting poster file: {str(e)}")
                # Don't fail the entire operation if poster deletion fails

        # Delete related records first
        # Delete film-genre relations
        db.session.query(FilmGenre).filter_by(film_id=film_id).delete()

        # Delete film-director relations
        db.session.query(FilmDirector).filter_by(film_id=film_id).delete()

        # Delete film ratings
        from models.relations_models import FilmRating
        db.session.query(FilmRating).filter_by(film_id=film_id).delete()

        # Delete film favorites
        from models.relations_models import FilmFavorite
        db.session.query(FilmFavorite).filter_by(film_id=film_id).delete()

        # Finally delete the film
        db.session.delete(film)
        db.session.commit()

        LogService.log_action(1, f"Admin deleted film {film_id}: {film.title}")  # 使用0作为admin用户ID
        return True

    @classmethod
    def get_films_paginated(cls, page: int = 1, per_page: int = 20):
        """
        Get films with pagination for admin panel.

        Args:
            page: int - Page number (1-based)
            per_page: int - Number of films per page

        Returns:
            dict: {
                'films': list of film dicts,
                'total': total number of films,
                'page': current page,
                'per_page': items per page,
                'total_pages': total number of pages
            }
        """
        from services.film_service import FilmService

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count
        total = cls.get_total_films()

        # Get paginated films
        query = db.session.query(Film).order_by(Film.id.desc()).offset(offset).limit(per_page)
        films = query.all()

        # Enrich film data
        film_dicts = []
        for film in films:
            film_dict = FilmService._enrich_film_dict(film)
            film_dicts.append(film_dict)

        total_pages = (total + per_page - 1) // per_page

        return {
            'films': film_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

    @classmethod
    def search_films_by_title(cls, title: str, page: int = 1, per_page: int = 20):
        """
        Search films by title using Trie + edit distance matching with pagination.

        Args:
            title: str - Search keyword for film title
            page: int - Page number (1-based)
            per_page: int - Number of films per page

        Returns:
            dict: Same structure as get_films_paginated
        """
        from services.film_service import FilmService
        from common.uilts import Trie

        # Get all films first
        all_films = db.session.query(Film).all()

        # Build Trie with all film titles
        trie = Trie()
        title_to_film = {}  # Map title to film object for quick lookup

        for film in all_films:
            trie.insert(film.title)
            title_to_film[film.title] = film

        # Search using Trie + edit distance
        matched_titles = []

        # First, try prefix matching
        prefix_matches = trie.search_prefix(title, max_results=50)  # Get more candidates
        matched_titles.extend(prefix_matches)

        # If we need more results, use edit distance search
        if len(matched_titles) < 50:  # Ensure we have enough candidates before pagination
            remaining_slots = 50 - len(matched_titles)
            edit_matches = trie.search_with_edit_distance(
                title,
                max_distance=3,  # Allow up to 3 edits
                max_results=remaining_slots
            )

            # Extract titles from edit distance results
            edit_titles = [match[0] for match in edit_matches]
            # Add only titles not already in matched_titles
            for edit_title in edit_titles:
                if edit_title not in matched_titles:
                    matched_titles.append(edit_title)

        # Remove duplicates while preserving order
        seen = set()
        unique_titles = []
        for title in matched_titles:
            if title not in seen:
                seen.add(title)
                unique_titles.append(title)

        # Sort by relevance (exact prefix matches first, then by title alphabetically)
        prefix_set = set(prefix_matches)
        unique_titles.sort(key=lambda x: (0 if x in prefix_set else 1, x))

        # Apply pagination to matched results
        total = len(unique_titles)
        offset = (page - 1) * per_page
        paginated_titles = unique_titles[offset:offset + per_page]

        # Get film objects for paginated results
        films = [title_to_film[title] for title in paginated_titles if title in title_to_film]

        # Enrich film data
        film_dicts = []
        for film in films:
            film_dict = FilmService._enrich_film_dict(film)
            film_dicts.append(film_dict)

        total_pages = (total + per_page - 1) // per_page

        return {
            'films': film_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'search_query': title
        }

    @classmethod
    def get_users_paginated(cls, page: int = 1, per_page: int = 20, username: str = None):
        """
        Get users with pagination for admin panel, optionally filtered by username using Trie + edit distance matching.

        Args:
            page: int - Page number (1-based)
            per_page: int - Number of users per page
            username: str - Optional username filter (uses intelligent matching)

        Returns:
            dict: {
                'users': list of user dicts,
                'total': total number of users,
                'page': current page,
                'per_page': items per page,
                'total_pages': total number of pages,
                'search_query': search term (if provided)
            }
        """
        from common.uilts import Trie

        # Get all users first
        all_users = db.session.query(User).all()

        if username:
            # Build Trie with all usernames
            trie = Trie()
            username_to_user = {}  # Map username to user object for quick lookup

            for user in all_users:
                trie.insert(user.username)
                username_to_user[user.username] = user

            # Search using Trie + edit distance
            matched_usernames = []

            # First, try prefix matching
            prefix_matches = trie.search_prefix(username, max_results=100)  # Get more candidates
            matched_usernames.extend(prefix_matches)

            # If we need more results, use edit distance search
            if len(matched_usernames) < 100:  # Ensure we have enough candidates before pagination
                remaining_slots = 100 - len(matched_usernames)
                edit_matches = trie.search_with_edit_distance(
                    username,
                    max_distance=3,  # Allow up to 3 edits
                    max_results=remaining_slots
                )

                # Extract usernames from edit distance results
                edit_usernames = [match[0] for match in edit_matches]
                # Add only usernames not already in matched_usernames
                for edit_username in edit_usernames:
                    if edit_username not in matched_usernames:
                        matched_usernames.append(edit_username)

            # Remove duplicates while preserving order
            seen = set()
            unique_usernames = []
            for uname in matched_usernames:
                if uname not in seen:
                    seen.add(uname)
                    unique_usernames.append(uname)

            # Sort by relevance (exact prefix matches first, then by username alphabetically)
            prefix_set = set(prefix_matches)
            unique_usernames.sort(key=lambda x: (0 if x in prefix_set else 1, x))

            # Apply pagination to matched results
            total = len(unique_usernames)
            offset = (page - 1) * per_page
            paginated_usernames = unique_usernames[offset:offset + per_page]

            # Get user objects for paginated results
            users = [username_to_user[uname] for uname in paginated_usernames if uname in username_to_user]

            # Sort users by ID descending (maintain original order preference)
            users.sort(key=lambda u: u.id, reverse=True)
        else:
            # No search filter - get all users with pagination
            total = len(all_users)
            offset = (page - 1) * per_page

            # Sort all users by ID descending and apply pagination
            all_users_sorted = sorted(all_users, key=lambda u: u.id, reverse=True)
            users = all_users_sorted[offset:offset + per_page]

        # Convert to dicts
        user_dicts = [user.to_dict() for user in users]

        total_pages = (total + per_page - 1) // per_page

        result = {
            'users': user_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

        if username:
            result['search_query'] = username

        return result

    @classmethod
    def delete_user_by_admin(cls, user_id: int):
        """
        Delete a user by admin (different from user self-deletion).

        Args:
            user_id: int - ID of the user to delete

        Returns:
            bool: True if successful
        """
        user = db.session.query(User).get(user_id)
        if not user:
            raise ValueError("User not found")

        if user.username == 'admin':
            raise ValueError("Cannot delete admin user")

        # Delete user and all related data directly (admin override)
        # Remove avatar file if not default
        avatars_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "avatars"))
        if getattr(user, "avatar_url", None) and user.avatar_url and user.avatar_url != "user.png":
            avatar_path = os.path.join(avatars_dir, user.avatar_url)
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    pass

        # Delete related records first
        # Delete user posts (will cascade delete comments and likes)
        user_posts = db.session.query(Post).filter_by(user_id=user_id).all()
        post_ids = [post.id for post in user_posts]

        # Delete post tags for user's posts
        from models.relations_models import PostTag
        if post_ids:
            db.session.query(PostTag).filter(PostTag.post_id.in_(post_ids)).delete()

        # Delete user posts
        db.session.query(Post).filter_by(user_id=user_id).delete()

        # Delete user comments
        db.session.query(Comment).filter_by(user_id=user_id).delete()

        # Delete user ratings
        from models.relations_models import FilmRating
        db.session.query(FilmRating).filter_by(user_id=user_id).delete()

        # Delete user favorites
        from models.relations_models import FilmFavorite
        db.session.query(FilmFavorite).filter_by(user_id=user_id).delete()

        # Delete user tags relations
        from models.relations_models import UserTag
        db.session.query(UserTag).filter_by(user_id=user_id).delete()

        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        LogService.log_action(1, f"Admin deleted user {user_id}: {user.username}")  # 使用0作为admin用户ID
        return True

    @classmethod
    def get_user_posts_paginated(cls, user_id: int, page: int = 1, per_page: int = 20):
        """
        Get posts by a specific user with pagination.

        Args:
            user_id: int - User ID
            page: int - Page number (1-based)
            per_page: int - Number of posts per page

        Returns:
            dict: {
                'posts': list of post dicts,
                'total': total number of posts,
                'page': current page,
                'per_page': items per page,
                'total_pages': total number of pages
            }
        """
        from services.post_service import PostService

        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count for this user
        total = db.session.query(Post).filter_by(user_id=user_id).count()

        # Get paginated posts
        posts = db.session.query(Post).filter_by(user_id=user_id).order_by(Post.created_at.desc()).offset(offset).limit(per_page).all()

        # Enrich post data
        post_dicts = []
        for post in posts:
            post_dict = PostService._build_post_dict(post.id, user_id)
            post_dicts.append(post_dict)

        total_pages = (total + per_page - 1) // per_page

        return {
            'posts': post_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'user_id': user_id
        }

    @classmethod
    def delete_post_by_admin(cls, post_id: int):
        """
        Delete a specific post by admin.

        Args:
            post_id: int - Post ID to delete

        Returns:
            bool: True if successful
        """
        post = db.session.query(Post).get(post_id)
        if not post:
            raise ValueError("Post not found")

        # Delete post will cascade delete related comments and likes
        db.session.delete(post)
        db.session.commit()

        LogService.log_action(1, f"Admin deleted post {post_id} by user {post.user_id}")  # 使用0作为admin用户ID
        return True

    @classmethod
    def get_user_comments_paginated(cls, user_id: int, page: int = 1, per_page: int = 20):
        """
        Get comments by a specific user with pagination.

        Args:
            user_id: int - User ID
            page: int - Page number (1-based)
            per_page: int - Number of comments per page

        Returns:
            dict: {
                'comments': list of comment dicts,
                'total': total number of comments,
                'page': current page,
                'per_page': items per page,
                'total_pages': total number of pages
            }
        """
        # Calculate offset
        offset = (page - 1) * per_page

        # Get total count for this user
        total = db.session.query(Comment).filter_by(user_id=user_id).count()

        # Get paginated comments
        comments = db.session.query(Comment).filter_by(user_id=user_id).order_by(Comment.created_at.desc()).offset(offset).limit(per_page).all()

        # Convert to dicts and enrich with user info and post info
        comment_dicts = []
        for comment in comments:
            comment_dict = {
                'comment_id': comment.id,
                'user_id': comment.user_id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat() if comment.created_at else None,
                'updated_at': comment.updated_at.isoformat() if comment.updated_at else None
            }

            # Add user info
            user = db.session.query(User).get(comment.user_id)
            if user:
                comment_dict['user_info'] = {
                    'id': user.id,
                    'username': user.username,
                    'avatar_url': user.avatar_url
                }

            # Add post info through PostComment relationship
            from models.relations_models import PostComment
            post_comment = db.session.query(PostComment).filter_by(comment_id=comment.id).first()
            if post_comment:
                post = db.session.query(Post).get(post_comment.post_id)
                if post:
                    comment_dict['post_id'] = post.id
                    comment_dict['post_title'] = post.title
                else:
                    comment_dict['post_id'] = post_comment.post_id
                    comment_dict['post_title'] = 'Unknown Post'
            else:
                comment_dict['post_id'] = None
                comment_dict['post_title'] = 'Unknown Post'

            comment_dicts.append(comment_dict)

        total_pages = (total + per_page - 1) // per_page

        return {
            'comments': comment_dicts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'user_id': user_id
        }

    @classmethod
    def delete_comment_by_admin(cls, comment_id: int):
        """
        Delete a specific comment by admin.

        Args:
            comment_id: int - Comment ID to delete

        Returns:
            bool: True if successful
        """
        comment = db.session.query(Comment).get(comment_id)
        if not comment:
            raise ValueError("Comment not found")

        # Delete comment
        db.session.delete(comment)
        db.session.commit()

        LogService.log_action(1, f"Admin deleted comment {comment_id} by user {comment.user_id}")  # 使用0作为admin用户ID
        return True
