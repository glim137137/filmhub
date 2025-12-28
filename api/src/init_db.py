import os
import sys
import csv
import bcrypt
from datetime import datetime
from flask import Flask

# Ensure import path is correct
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import DB_URL
from db import db
from models.core_models import *
from models.relations_models import *

CSV_DIR = os.path.join(BASE_DIR, 'db', 'data', 'csv')

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def load_from_csv(csv_path, model_class, mapper_func, skip_existing=True):
    """Load data from CSV file to database"""
    if not os.path.exists(csv_path):
        print(f"CSV file does not exist: {csv_path}")
        return 0

    count = 0
    with open(csv_path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                # Use mapper function to create model instance
                instance = mapper_func(row)
                if instance:
                    # Check if already exists (optional)
                    if skip_existing and hasattr(instance, 'id'):
                        existing = db.session.query(model_class).filter_by(id=instance.id).first()
                        if existing:
                            continue

                    db.session.add(instance)
                    count += 1

                    # Commit every 100 records to avoid excessive memory usage
                    if count % 100 == 0:
                        db.session.flush()

            except Exception as e:
                print(f"Error processing row (file: {csv_path}): {e}")
                continue

    if count > 0:
        db.session.commit()
        print(f"Imported {count} records from {os.path.basename(csv_path)}")

    return count

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def init_database():
    """Initialize database from CSV files"""
    app = create_app()

    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        print("Database tables created successfully")

        # 1. Load core entities (no foreign key dependencies)

        # Load users
        def user_mapper(row):
            try:
                # Handle password hashing
                password = row.get('password', '').strip()
                if password:
                    password = hash_password(password)
                else:
                    password = hash_password('defaultpassword')

                # Parse datetime
                created_at = datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow()
                updated_at = datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else datetime.utcnow()

                return User(
                    id=int(row['id']),
                    username=row['username'],
                    email=row['email'],
                    password=password,
                    bio=row.get('bio') or '',
                    avatar_url=row.get('avatar_url') or 'user.png',
                    created_at=created_at,
                    updated_at=updated_at
                )
            except Exception as e:
                print(f"Failed to map user: {e}")
                return None

        load_from_csv(os.path.join(CSV_DIR, 'users.csv'), User, user_mapper)

        # Create admin account
        admin_password = hash_password("@Adminadmin10")
        admin_user = User(
            id=148,  # Use a high ID to avoid conflict with CSV users
            username="admin",
            email="admin@qq.com",
            password=admin_password,
            bio="Administrator account",
            avatar_url="user.png",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(admin_user)
        db.session.flush()
        print("Admin account created: admin")

        # Load tags
        def tag_mapper(row):
            try:
                return Tag(
                    id=int(row['id']),
                    name=row['name']
                )
            except Exception as e:
                print(f"Failed to map tag: {e}")
                return None

        load_from_csv(os.path.join(CSV_DIR, 'tags.csv'), Tag, tag_mapper)

        # Load films
        def film_mapper(row):
            try:
                # Handle release date
                release_date_str = row.get('release_date', '').strip()
                release_date = None
                if release_date_str:
                    try:
                        release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                    except:
                        pass

                # Handle optional fields
                tmdb_id = int(row['tmdb_id']) if row.get('tmdb_id') and row['tmdb_id'].strip() else None
                duration = int(row['duration']) if row.get('duration') and row['duration'].strip() else None
                rating = float(row['rating']) if row.get('rating') and row['rating'].strip() else None
                vote_count = int(row['vote_count']) if row.get('vote_count') and row['vote_count'].strip() else None

                return Film(
                    id=int(row['id']),
                    title=row['title'],
                    tmdb_id=tmdb_id,
                    overview=row.get('overview') or '',
                    release_date=release_date,
                    duration=duration,
                    rating=rating,
                    vote_count=vote_count,
                    language=row.get('language') or '',
                    poster_url=row.get('poster_url') or ''
                )
            except Exception as e:
                print(f"Failed to map film: {e}")
                return None

        load_from_csv(os.path.join(CSV_DIR, 'films.csv'), Film, film_mapper)

        # Load genres
        def genre_mapper(row):
            try:
                return Genre(
                    id=int(row['id']),
                    name=row['name']
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'genres.csv'), Genre, genre_mapper)

        # Load directors
        def director_mapper(row):
            try:
                return Director(
                    id=int(row['id']),
                    name=row['name']
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'directors.csv'), Director, director_mapper)

        # 2. Load entities with foreign key dependencies

        # Load posts (depends on users)
        def post_mapper(row):
            try:
                # Parse datetime
                created_at = datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow()
                updated_at = datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else datetime.utcnow()

                return Post(
                    id=int(row['id']),
                    user_id=int(row['user_id']),
                    title=row['title'],
                    like_count=int(row['like_count']),
                    content=row.get('content') or '',
                    created_at=created_at,
                    updated_at=updated_at
                )
            except Exception as e:
                print(f"Failed to map post: {e}")
                return None

        load_from_csv(os.path.join(CSV_DIR, 'posts.csv'), Post, post_mapper)

        # Load comments (depends on users)
        def comment_mapper(row):
            try:
                # Parse datetime
                created_at = datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.utcnow()
                updated_at = datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else datetime.utcnow()

                return Comment(
                    id=int(row['id']),
                    user_id=int(row['user_id']),
                    content=row['content'],
                    created_at=created_at,
                    updated_at=updated_at
                )
            except Exception as e:
                print(f"Failed to map comment: {e}")
                return None

        load_from_csv(os.path.join(CSV_DIR, 'comments.csv'), Comment, comment_mapper)

        # 3. Load relationship tables (depends on core entities)

        # Load film-genre relationships
        def film_genre_mapper(row):
            try:
                return FilmGenre(
                    id=int(row['id']),
                    film_id=int(row['film_id']),
                    genre_id=int(row['genre_id'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'film_genres.csv'), FilmGenre, film_genre_mapper)

        # Load film-director relationships
        def film_director_mapper(row):
            try:
                return FilmDirector(
                    id=int(row['id']),
                    film_id=int(row['film_id']),
                    director_id=int(row['director_id'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'film_directors.csv'), FilmDirector, film_director_mapper)

        # Load user-tag relationships
        def user_tag_mapper(row):
            try:
                return UserTag(
                    id=int(row['id']),
                    user_id=int(row['user_id']),
                    tag_id=int(row['tag_id'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'user_tags.csv'), UserTag, user_tag_mapper)

        # Load post-tag relationships
        def post_tag_mapper(row):
            try:
                return PostTag(
                    id=int(row['id']),
                    post_id=int(row['post_id']),
                    tag_id=int(row['tag_id'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'post_tags.csv'), PostTag, post_tag_mapper)

        # Load post-comment relationships
        def post_comment_mapper(row):
            try:
                return PostComment(
                    id=int(row['id']),
                    post_id=int(row['post_id']),
                    comment_id=int(row['comment_id'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'post_comments.csv'), PostComment, post_comment_mapper)

        # Load film ratings
        def film_rating_mapper(row):
            try:
                return FilmRating(
                    id=int(row['id']),
                    film_id=int(row['film_id']),
                    user_id=int(row['user_id']),
                    rating=float(row['rating'])
                )
            except Exception:
                return None

        load_from_csv(os.path.join(CSV_DIR, 'film_ratings.csv'), FilmRating, film_rating_mapper)

        # Load film favorites (may be empty)
        def film_favorite_mapper(row):
            try:
                return FilmFavorite(
                    id=int(row['id']),
                    film_id=int(row['film_id']),
                    user_id=int(row['user_id'])
                )
            except Exception:
                return None

        # Load film favorites (file exists but may be empty)
        fav_path = os.path.join(CSV_DIR, 'film_favorites.csv')
        if os.path.exists(fav_path):
            # Check if file has more than just header
            with open(fav_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 1:  # Has data rows
                    load_from_csv(fav_path, FilmFavorite, film_favorite_mapper)
                else:
                    print("film_favorites.csv is empty, skipping import")
        else:
            print("film_favorites.csv does not exist, skipping import")

        print("\nDatabase initialization completed successfully!")

        # Print statistics
        print("\nDatabase record statistics:")
        print(f"Users: {db.session.query(User).count()} records")
        print(f"Tags: {db.session.query(Tag).count()} records")
        print(f"Films: {db.session.query(Film).count()} records")
        print(f"Genres: {db.session.query(Genre).count()} records")
        print(f"Directors: {db.session.query(Director).count()} records")
        print(f"Posts: {db.session.query(Post).count()} records")
        print(f"Comments: {db.session.query(Comment).count()} records")
        print(f"Film Ratings: {db.session.query(FilmRating).count()} records")
        print(f"Film Favorites: {db.session.query(FilmFavorite).count()} records")

if __name__ == '__main__':
    init_database()