"""
Generate CSV files matching the database models from the provided
source CSVs: `film_data.csv` and `user_data.csv`.

Output CSV files will be placed in a `csv` folder under the data directory.

All comments in this file are written in English.
"""
from __future__ import annotations
import csv
import os
import re
import random
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "data")
SOURCE_FILM_CSV = os.path.join(DATA_DIR, "film_data.csv")
SOURCE_USER_CSV = os.path.join(DATA_DIR, "user_data.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "csv")

# unified strong password for all generated users
UNIFIED_PASSWORD = "Str0ngP@ssw0rd!2025"

def ensure_output_dir() -> None:
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def first_sentence(text: str) -> str:
    """Return the first sentence of a block of text.

    Splits on newlines and common sentence-ending punctuation.
    """
    if not text:
        return ""
    # normalize whitespace
    t = text.strip().replace("\r", "\n")
    # prefer newline as sentence boundary
    parts = [p for p in re.split(r"[\n]+", t) if p.strip()]
    if parts:
        candidate = parts[0].strip()
    else:
        candidate = t
    # find first sentence end punctuation (.!?。！?) and return up to it
    m = re.search(r"([\.!\?。\！\?])", candidate)
    if m:
        idx = m.end()
        return candidate[:idx].strip()
    # fallback: split by period-space
    if ". " in candidate:
        return candidate.split(". ", 1)[0].strip() + "."
    return candidate

def parse_comma_separated_list(field: str) -> List[str]:
    """Parse a comma-separated field into trimmed items; ignore empties."""
    if not field:
        return []
    return [x.strip() for x in field.split(",") if x.strip()]

def parse_pipe_separated_list(field: str) -> List[str]:
    """Parse a pipe-separated field into trimmed items; ignore empties."""
    if not field:
        return []
    return [x.strip() for x in field.split("|") if x.strip()]

def read_films() -> Tuple[List[Dict], Dict[str, int]]:
    """Read `film_data.csv` and return list of film rows and mapping tmdb_id -> film_id."""
    films = []
    tmdb_to_id: Dict[str, int] = {}
    with open(SOURCE_FILM_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # keep original id as integer id for the films table
            film_id = int(row["id"])
            films.append({
                "id": film_id,
                "title": row.get("title", ""),
                "tmdb_id": int(row["tmdb_id"]) if row.get("tmdb_id") else None,
                "overview": row.get("overview", ""),
                "release_date": row.get("release_date", "") or "",
                "duration": int(row["duration"]) if row.get("duration") else None,
                "rating": float(row["rating"]) if row.get("rating") else None,
                "vote_count": int(row["vote_count"]) if row.get("vote_count") else None,
                "language": row.get("language", "") or "",
                "poster_url": row.get("poster_url", "") or "",
                "director": row.get("director", "") or "",
                "genre": row.get("genre", "") or "",
            })
            if row.get("tmdb_id"):
                tmdb_to_id[str(row["tmdb_id"])] = film_id
    return films, tmdb_to_id

def read_user_comments() -> List[Dict]:
    """Read `user_data.csv` — this dataset contains commenter rows per film.

    Expected columns: id, tmdb_id, username, rating, content, created_at, updated_at, tags
    """
    comments = []
    with open(SOURCE_USER_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            comments.append(row)
    return comments

def write_csv(path: str, fieldnames: List[str], rows: List[Dict]) -> None:
    """Write CSV using given fieldnames and rows. Always write header."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # ensure every field exists (avoid KeyError)
            out = {k: ("" if r.get(k) is None else r.get(k)) for k in fieldnames}
            writer.writerow(out)

def generate_all_csvs() -> None:
    """Main pipeline to generate all target CSVs matching DB models."""
    ensure_output_dir()

    films, tmdb_to_id = read_films()
    comments_raw = read_user_comments()

    # 1) Write `films` CSV (columns must match model)
    films_rows = []
    for f in films:
        films_rows.append({
            "id": f["id"],
            "title": f["title"],
            "tmdb_id": f["tmdb_id"],
            "overview": f["overview"],
            "release_date": f["release_date"],
            "duration": f["duration"],
            "rating": f["rating"],
            "vote_count": f["vote_count"],
            "language": f["language"],
            "poster_url": f["poster_url"],
        })
    write_csv(os.path.join(OUTPUT_DIR, "films.csv"),
              ["id","title","tmdb_id","overview","release_date","duration","rating","vote_count","language","poster_url"],
              films_rows)

    # 2) Build users from commenters (unique usernames)
    username_to_id: Dict[str, int] = {}
    users_rows = []
    next_user_id = 1
    for row in comments_raw:
        username = (row.get("username") or "").strip()
        if not username:
            continue
        if username not in username_to_id:
            uid = next_user_id
            username_to_id[username] = uid
            next_user_id += 1
            # create email from username - only allow letters and digits
            email_safe = re.sub(r"[^a-zA-Z0-9]", "_", username).lower()
            if not email_safe:
                email_safe = f"user{uid}"

            users_rows.append({
                "id": uid,
                "username": username,
                "email": f"{email_safe}@example.com",
                "password": UNIFIED_PASSWORD,
                "bio": "",
                "avatar_url": "user.png",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })
    write_csv(os.path.join(OUTPUT_DIR, "users.csv"),
              ["id","username","email","password","bio","avatar_url","created_at","updated_at"],
              users_rows)

    # 3) Extract tags globally and per-user
    tag_name_to_id: Dict[str, int] = {}
    next_tag_id = 1
    user_tags_rows = []
    for row in comments_raw:
        username = (row.get("username") or "").strip()
        if not username:
            continue
        uid = username_to_id.get(username)
        tags_field = row.get("tags") or ""
        # 修改：使用竖线分隔符解析 tags
        tags = parse_pipe_separated_list(tags_field)
        for t in tags:
            if t not in tag_name_to_id:
                tag_name_to_id[t] = next_tag_id
                next_tag_id += 1
            user_tags_rows.append({
                "id": None,  # fill later
                "user_id": uid,
                "tag_id": tag_name_to_id[t],
            })
    # de-duplicate user_tags rows
    seen_ut = set()
    unique_user_tags = []
    next_ut_id = 1
    for r in user_tags_rows:
        key = (r["user_id"], r["tag_id"])
        if key in seen_ut:
            continue
        seen_ut.add(key)
        r["id"] = next_ut_id
        next_ut_id += 1
        unique_user_tags.append(r)
    # write tags.csv
    tags_rows = [{"id": tid, "name": name} for name, tid in tag_name_to_id.items()]
    # ensure stable order
    tags_rows.sort(key=lambda x: x["id"])
    write_csv(os.path.join(OUTPUT_DIR, "tags.csv"),
              ["id","name"],
              tags_rows)
    write_csv(os.path.join(OUTPUT_DIR, "user_tags.csv"),
              ["id","user_id","tag_id"],
              unique_user_tags)

    # 4) Genres and Directors and their mappings
    genre_name_to_id: Dict[str, int] = {}
    director_name_to_id: Dict[str, int] = {}
    next_genre_id = 1
    next_director_id = 1
    film_genres_rows = []
    film_directors_rows = []
    next_fg_id = 1
    next_fd_id = 1
    for f in films:
        gid_film = f["id"]
        # genres
        genres = parse_comma_separated_list(f.get("genre") or "")
        for g in genres:
            if g not in genre_name_to_id:
                genre_name_to_id[g] = next_genre_id
                next_genre_id += 1
            film_genres_rows.append({
                "id": next_fg_id,
                "film_id": gid_film,
                "genre_id": genre_name_to_id[g],
            })
            next_fg_id += 1
        # directors (single value assumed)
        dname = (f.get("director") or "").strip()
        if dname:
            if dname not in director_name_to_id:
                director_name_to_id[dname] = next_director_id
                next_director_id += 1
            film_directors_rows.append({
                "id": next_fd_id,
                "film_id": gid_film,
                "director_id": director_name_to_id[dname],
            })
            next_fd_id += 1
    # write genres and directors
    genres_rows = [{"id": gid, "name": name} for name, gid in genre_name_to_id.items()]
    genres_rows.sort(key=lambda x: x["id"])
    write_csv(os.path.join(OUTPUT_DIR, "genres.csv"),
              ["id","name"], genres_rows)
    directors_rows = [{"id": did, "name": name} for name, did in director_name_to_id.items()]
    directors_rows.sort(key=lambda x: x["id"])
    write_csv(os.path.join(OUTPUT_DIR, "directors.csv"),
              ["id","name"], directors_rows)
    write_csv(os.path.join(OUTPUT_DIR, "film_genres.csv"),
              ["id","film_id","genre_id"], film_genres_rows)
    write_csv(os.path.join(OUTPUT_DIR, "film_directors.csv"),
              ["id","film_id","director_id"], film_directors_rows)

    # 5) Build posts from all user_data content - each content becomes a separate post
    posts_rows = []
    post_tags_rows = []
    film_ratings_rows = []
    next_post_id = 1
    next_post_tag_id = 1
    next_film_rating_id = 1

    for row in comments_raw:
        tmdb = (row.get("tmdb_id") or "").strip()
        if not tmdb:
            continue
        film_id = tmdb_to_id.get(tmdb)
        if not film_id:
            # skip comments for films not present in film_data.csv
            continue

        # create post for each content
        username = (row.get("username") or "").strip()
        user_id = username_to_id.get(username)
        content = row.get("content", "") or ""
        title = f"Review from {username}"
        created_at = row.get("created_at", "") or ""
        updated_at = row.get("updated_at", "") or ""

        posts_rows.append({
            "id": next_post_id,
            "user_id": user_id,
            "title": title,
            "content": content,
            "like_count": random.randint(0, 1000),
            "created_at": created_at,
            "updated_at": updated_at,
        })

        # attach tags to post - 使用竖线分隔符
        post_tags = parse_pipe_separated_list(row.get("tags") or "")
        for tag in post_tags:
            tid = tag_name_to_id.get(tag)
            if not tid:
                # create tag if missing
                tid = next_tag_id
                tag_name_to_id[tag] = tid
                next_tag_id += 1
                # Also update tags_rows with this new tag
                tags_rows.append({"id": tid, "name": tag})
            post_tags_rows.append({
                "id": next_post_tag_id,
                "post_id": next_post_id,
                "tag_id": tid,
            })
            next_post_tag_id += 1

        # create film rating for this post if rating exists
        rating_val = row.get("rating")
        try:
            rating_val_f = float(rating_val) if rating_val not in (None,"") else None
        except Exception:
            rating_val_f = None
        if rating_val_f is not None and user_id is not None:
            film_ratings_rows.append({
                "id": next_film_rating_id,
                "film_id": film_id,
                "user_id": user_id,
                "rating": rating_val_f,
            })
            next_film_rating_id += 1

        next_post_id += 1

    # Re-sort tags_rows after adding new tags during post processing
    tags_rows.sort(key=lambda x: x["id"])

    # Overwrite tags.csv with updated tags
    write_csv(os.path.join(OUTPUT_DIR, "tags.csv"),
              ["id","name"], tags_rows)

    # write posts and their mapping tables (comments are empty as requested)
    write_csv(os.path.join(OUTPUT_DIR, "posts.csv"),
              ["id","user_id","title","content","like_count","created_at","updated_at"],
              posts_rows)
    write_csv(os.path.join(OUTPUT_DIR, "comments.csv"),
              ["id","user_id","content","created_at","updated_at"],
              [])
    write_csv(os.path.join(OUTPUT_DIR, "post_tags.csv"),
              ["id","post_id","tag_id"],
              post_tags_rows)
    write_csv(os.path.join(OUTPUT_DIR, "post_comments.csv"),
              ["id","post_id","comment_id"],
              [])

    # 6) film_ratings and film_favorites (favorites empty as requested)
    write_csv(os.path.join(OUTPUT_DIR, "film_ratings.csv"),
              ["id","film_id","user_id","rating"],
              film_ratings_rows)
    # empty file for film_favorites with header only
    write_csv(os.path.join(OUTPUT_DIR, "film_favorites.csv"),
              ["id","film_id","user_id"],
              [])

    print("CSV generation completed. Output directory:", OUTPUT_DIR)

if __name__ == "__main__":
    generate_all_csvs()