from db import db
from datetime import datetime

# user
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(128), default="user.png")
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

# tag
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# film
class Film(db.Model):
    __tablename__ = 'films'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    tmdb_id = db.Column(db.Integer)
    overview = db.Column(db.Text)
    release_date = db.Column(db.Date)
    duration = db.Column(db.Integer)
    rating = db.Column(db.Float)
    vote_count = db.Column(db.Integer)
    language = db.Column(db.String(32))
    poster_url = db.Column(db.String(512), default="film.jpg")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'tmdb_id': self.tmdb_id,
            'overview': self.overview,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'duration': self.duration,
            'poster_url': self.poster_url,
            'rating': self.rating,
            'vote_count': self.vote_count,
            'language': self.language
        }

# genre
class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# director
class Director(db.Model):
    __tablename__ = 'directors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# post
class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'like_count': self.like_count,
            'created_at': self.updated_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# comment
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    def to_dict(self):
        # Get post info through PostComment relationship
        from models.relations_models import PostComment
        from db import db

        post_comment = db.session.query(PostComment).filter_by(comment_id=self.id).first()
        post_title = None
        if post_comment:
            post = db.session.query(Post).get(post_comment.post_id)
            post_title = post.title if post else None

        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'post_id': post_comment.post_id if post_comment else None,
            'post_title': post_title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
# log
class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'created_at': self.created_at.isoformat()
        }