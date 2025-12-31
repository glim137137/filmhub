from models.core_models import Film, Genre, Director
from models.relations_models import FilmGenre, FilmDirector, FilmRating, FilmFavorite
from flask import current_app as app
from db import db
from common.uilts import FilmTrie
from common.validation import FilmValidation
from common.exception import ValidationException
from models.core_models import Tag
import numpy as np

class FilmService:

    @classmethod
    def get_film_by_id(cls, film_id: int, user_id=None):
        """
        Get film details by id.

        Args:
            film_id: int
            user_id: optional int for personalization
        Returns:
            dict: enriched film dict or {}
        """
        film = db.session.query(Film).get(film_id)
        return cls._enrich_film_dict(film, user_id=user_id)

    @classmethod
    def get_film_by_title(cls, title: str, user_id=None):
        """
        Get film details by title.

        Args:
            title: str - film title (exact match)
            user_id: optional int for personalization
        Returns:
            dict: enriched film dict or {}
        """
        film = db.session.query(Film).filter(Film.title == title).first()
        return cls._enrich_film_dict(film, user_id=user_id)

    @classmethod
    def get_all_genres(cls):
        """
        Get all genres ordered by name.

        Returns:
            list[Genre]
        """
        return db.session.query(Genre).order_by(Genre.name).all()


    @classmethod
    def get_high_rate_films(cls, limit: int = 10, user_id=None):
        """
        Get top rated films.

        Args:
            limit: max number of films
            user_id: optional int for personalization
        Returns:
            list of enriched film dicts
        """
        films = db.session.query(Film).filter(Film.rating != None).order_by(Film.rating.desc(), Film.vote_count.desc()).limit(limit).all()
        return [cls._enrich_film_dict(f, user_id=user_id) for f in films]

    @classmethod
    def get_latest_films(cls, limit: int = 10, user_id=None):
        """
        Get latest released films.

        Args:
            limit: max number of films
            user_id: optional int for personalization
        Returns:
            list of enriched film dicts
        """
        films = db.session.query(Film).filter(Film.release_date != None).order_by(Film.release_date.desc()).limit(limit).all()
        return [cls._enrich_film_dict(f, user_id=user_id) for f in films]

    @classmethod
    def get_film_by_keyword(cls, dto: dict, user_id=None):
        """
        Search films by keyword using FilmTrie with edit distance.
        Searches across title, director, and year fields.

        Args:
            dto: { keyword: str }
            user_id: optional int for personalization
        Returns:
            list of enriched film dicts with search_score
        """
        try:
            FilmValidation.v_search_dto(dto)
        except Exception as e:
            raise ValidationException(str(e))

        keyword = (dto.get('keyword') or '').strip()
        if not keyword:
            return []

        # Create and populate FilmTrie
        film_trie = FilmTrie()

        # Fetch all films and enrich with director/year data
        candidates = Film.query.all()
        if not candidates:
            return []

        for f in candidates:
            # Get directors
            dir_rows = db.session.query(Director.name).join(FilmDirector, Director.id == FilmDirector.director_id).filter(FilmDirector.film_id == f.id).all()
            directors = [d[0] for d in dir_rows] if dir_rows else []

            # Get genres (for completeness, though not used in search)
            gen_rows = db.session.query(Genre.name).join(FilmGenre, Genre.id == FilmGenre.genre_id).filter(FilmGenre.film_id == f.id).all()
            genres = [g[0] for g in gen_rows] if gen_rows else []

            # Prepare film data for trie
            film_data = {
                'id': f.id,
                'title': f.title or '',
                'directors': directors,
                'genres': genres,
                'year': (f.release_date.year if getattr(f, 'release_date', None) else None),
                'rating': (f.rating or 0.0),
                'vote_count': (f.vote_count or 0)
            }

            # Insert into trie
            film_trie.insert_film(film_data)

        # Search using trie
        search_results = film_trie.search_films(keyword, max_edit_distance=2, max_results=10)

        # Enrich results with full film data
        enriched = []
        for result in search_results:
            fid = result.get('id')
            film_obj = db.session.query(Film).get(fid)
            if film_obj:
                fdict = cls._enrich_film_dict(film_obj, user_id=user_id)
                fdict['search_score'] = result.get('search_score', 0)
                enriched.append(fdict)

        return enriched


    @classmethod
    def get_filtered_films(cls, dto: dict, user_id=None):
        """
        Get films filtered by multiple criteria.

        Args:
            dto: dict with filters {
                genre_id: int (optional),
                year: string (optional),
                language: string (optional),
                page: int (default: 1),
                per_page: int (default: 20)
            }
            user_id: optional int for personalization
        Returns:
            list: list of enriched film dicts
        """
        try:
            # Extract pagination params
            page = max(1, int(dto.get('page', 1)))
            per_page = min(50, max(1, int(dto.get('per_page', 20))))  # Limit to 50 per page
            offset = (page - 1) * per_page

            # Build query
            query = Film.query

            # Apply filters
            if dto.get('genre_id'):
                genre_id = int(dto['genre_id'])
                query = query.join(FilmGenre).filter(FilmGenre.genre_id == genre_id)

            if dto.get('year'):
                year = dto['year']
                query = query.filter(db.extract('year', Film.release_date) == int(year))

            if dto.get('language'):
                language = dto['language']
                query = query.filter(Film.language == language)

            # Apply pagination and ordering
            films = query.order_by(Film.rating.desc(), Film.release_date.desc())\
                        .offset(offset)\
                        .limit(per_page)\
                        .all()

            # Enrich film data
            result = []
            for film in films:
                enriched = cls._enrich_film_dict(film, user_id=user_id)
                result.append(enriched)

            return result

        except Exception as e:
            return []

    @classmethod
    def get_recommendations(cls, user_id: int, limit: int = 5):
        """
        Recommend films using content-based filtering with 3-step pipeline:
        1. Item Feature: Convert films to vectors using genre one-hot encoding
        2. User Profile: Create user vector by weighted average of positive feedback items
        3. Similarity Ranking: Calculate cosine similarity between user profile and item vectors

        Args:
            user_id: int
            limit: number of recommendations
        Returns:
            list of enriched film dicts
        """

        # Step 1: (Item Feature) - Convert films to vectors using genre, language, director, year one-hot encoding
        # Get all genres
        all_genres = db.session.query(Genre).order_by(Genre.id).all()
        genre_id_to_index = {genre.id: i for i, genre in enumerate(all_genres)}
        num_genres = len(all_genres)

        # Get all unique languages
        all_languages = db.session.query(Film.language).filter(Film.language.isnot(None)).distinct().all()
        all_languages = [lang[0] for lang in all_languages if lang[0]]
        language_to_index = {lang: i for i, lang in enumerate(sorted(all_languages))}
        num_languages = len(all_languages)

        # Get all unique directors
        all_directors = db.session.query(Director).order_by(Director.id).all()
        director_id_to_index = {director.id: i for i, director in enumerate(all_directors)}
        num_directors = len(all_directors)

        # Get year range for normalization (continuous value)
        all_years = db.session.query(Film.release_date).filter(Film.release_date.isnot(None)).distinct().all()
        all_years = [date.year for date, in all_years if date and date.year]
        if all_years:
            min_year = min(all_years)
            max_year = max(all_years)
            year_range = max_year - min_year if max_year > min_year else 1
        else:
            min_year = 2000  # default fallback
            year_range = 1

        # Total feature dimension (year is now a single continuous value)
        total_features = num_genres + num_languages + num_directors + 1  # +1 for normalized year

        # Get all films with their features
        films = db.session.query(Film).all()
        film_features = {}

        for film in films:
            # Get film genres
            film_genres = db.session.query(FilmGenre.genre_id).filter(FilmGenre.film_id == film.id).all()
            genre_ids = [fg.genre_id for fg in film_genres]

            # Get film directors
            film_directors = db.session.query(FilmDirector.director_id).filter(FilmDirector.film_id == film.id).all()
            director_ids = [fd.director_id for fd in film_directors]

            # Create one-hot encoding vector
            feature_vector = np.zeros(total_features)

            # Add genre features
            for genre_id in genre_ids:
                if genre_id in genre_id_to_index:
                    feature_vector[genre_id_to_index[genre_id]] = 1.0

            # Add language feature
            if film.language and film.language in language_to_index:
                feature_vector[num_genres + language_to_index[film.language]] = 1.0

            # Add director features
            for director_id in director_ids:
                if director_id in director_id_to_index:
                    feature_vector[num_genres + num_languages + director_id_to_index[director_id]] = 1.0

            # Add year feature (normalized continuous value 0-1)
            if film.release_date and film.release_date.year:
                normalized_year = (film.release_date.year - min_year) / year_range
                feature_vector[total_features - 1] = normalized_year

            film_features[film.id] = feature_vector

        # Step 2: (User Profile) - Create user vector by weighted average of positive feedback
        # Get user's positive feedback: ratings and favorites
        user_ratings = db.session.query(FilmRating.film_id, FilmRating.rating).filter(FilmRating.user_id == user_id).all()
        user_favorites = db.session.query(FilmFavorite.film_id).filter(FilmFavorite.user_id == user_id).all()

        # Cold start: if user has no interactions, return popular films
        if not user_ratings and not user_favorites:
            popular_films = (db.session.query(Film)
                           .filter(Film.vote_count.isnot(None))
                           .order_by(Film.vote_count.desc())
                           .limit(limit)
                           .all())
            return [cls._enrich_film_dict(film, user_id=user_id) for film in popular_films]

        # Build user profile vector
        user_profile = np.zeros(total_features)
        total_weight = 0.0

        # Process ratings (weight by rating score, rating is 0-10)
        for film_id, rating in user_ratings:
            if film_id in film_features:
                weight = rating  # Rating is 0-10, use directly as weight
                user_profile += weight * film_features[film_id]
                total_weight += weight

        # Process favorites (higher weight than maximum rating)
        favorite_weight = 15.0  # Give favorites higher weight than max rating (10.0)
        for fav in user_favorites:
            film_id = fav.film_id
            if film_id in film_features:
                user_profile += favorite_weight * film_features[film_id]
                total_weight += favorite_weight

        # Normalize user profile
        if total_weight > 0:
            user_profile = user_profile / total_weight

        # Step 3: (Similarity Ranking & Recommendation)
        # Calculate similarities between user profile and all film features
        similarities = []

        # Get films user has already interacted with to exclude
        interacted_films = set()
        interacted_films.update([r.film_id for r in user_ratings])
        interacted_films.update([f.film_id for f in user_favorites])

        for film_id, film_vector in film_features.items():
            if film_id not in interacted_films:
                # Calculate cosine similarity using numpy
                dot_product = np.dot(user_profile, film_vector)
                norm_user = np.linalg.norm(user_profile)
                norm_film = np.linalg.norm(film_vector)

                if norm_user == 0 or norm_film == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_user * norm_film)

                similarities.append((film_id, similarity))

        # Sort by similarity (descending) and take top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get recommended films
        recommended_films = []
        for film_id, similarity in similarities[:limit]:
            film = db.session.query(Film).get(film_id)
            if film:
                recommended_films.append(cls._enrich_film_dict(film, user_id=user_id))

        return recommended_films
    @classmethod
    def _enrich_film_dict(cls, film_obj, user_id=None):
        """
        Enrich a Film object into a dict including directors, genres and user-specific info.

        Args:
            film_obj: Film
            user_id: optional int
        Returns:
            dict
        """
        base = film_obj.to_dict() if film_obj else {}
        # directors
        dir_rows = db.session.query(Director.name).join(FilmDirector, Director.id == FilmDirector.director_id).filter(FilmDirector.film_id == film_obj.id).all()
        directors = [d[0] for d in dir_rows] if dir_rows else []
        # genres
        gen_rows = db.session.query(Genre.name).join(FilmGenre, Genre.id == FilmGenre.genre_id).filter(FilmGenre.film_id == film_obj.id).all()
        genres = [g[0] for g in gen_rows] if gen_rows else []
        # user_rating
        user_rating = None
        user_favorite = False
        try:
            if user_id is not None:
                fr = db.session.query(FilmRating).filter_by(film_id=film_obj.id, user_id=int(user_id)).first()
                if fr:
                    user_rating = int(fr.rating) if fr.rating is not None else None
                ff = db.session.query(FilmFavorite).filter_by(film_id=film_obj.id, user_id=int(user_id)).first()
                user_favorite = True if ff else False
        except Exception:
            user_rating = None
            user_favorite = False

        base['directors'] = directors
        base['genres'] = genres
        base['user_rating'] = user_rating
        base['user_favorite'] = user_favorite
        return base