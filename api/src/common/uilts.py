import re
import difflib
import math
from datetime import timedelta
from flask_jwt_extended import create_access_token, decode_token
from flask import current_app as app



class PasswordUitls:

    @staticmethod
    def is_strong_password(password: str):
        """
        Check if the password is strong
        """

        # over 8, include uppercase, lowercase, number and special character
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            return False
        return True

class JWTUtils:

    @staticmethod
    def create_token(user: object, days: int = None):
        """Create access token using flask-jwt-extended.
        If days is None, use app config `JWT_ACCESS_TOKEN_EXPIRES` (timedelta) if set.
        """
        expires = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')

        additional_claims = {
            'username': getattr(user, 'username', None),
            'email': getattr(user, 'email', None)
        }
        # ensure subject is a string to satisfy JWT libraries expecting string 'sub'
        identity_value = getattr(user, 'id', None)
        if identity_value is not None:
            identity_value = str(identity_value)

        return create_access_token(
            identity=identity_value,
            additional_claims=additional_claims,
            expires_delta=expires
        )

    @staticmethod
    def decode_token(token: str):
        """Decode token payload using flask-jwt-extended helper."""

        try:
            return decode_token(token)
        except Exception:
            return None

class SearchUtils:
    # small English stopword list; extend as needed
    STOPWORDS = {
        'the', 'and', 'is', 'in', 'at', 'of', 'a', 'an', 'to', 'for', 'on', 'with', 'by', 'from', 'as', 'that', 'this'
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ''
        # lowercase and replace non-alphanumeric with spaces
        cleaned = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
        # collapse whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    @staticmethod
    def tokenize(text: str):
        """Return list of tokens after removing stopwords."""
        cleaned = SearchUtils.normalize_text(text or '')
        if not cleaned:
            return []
        tokens = [t for t in cleaned.split(' ') if t and t not in SearchUtils.STOPWORDS]
        return tokens

    @staticmethod
    def extract_years(text: str):
        """Find 4-digit years (1900-2099) in text and return as list of ints."""
        if not text:
            return []
        years = []
        for m in re.findall(r'\b(19|20)\d{2}\b', text):
            # re.findall with group returns the group; use a second findall for full match
            pass
        # simpler: use full-match findall
        for y in re.findall(r'\b(?:19|20)\d{2}\b', text):
            try:
                yi = int(y)
                years.append(yi)
            except Exception:
                continue
        return years

    @staticmethod
    def tokens_from_keyword(keyword: str):
        """Run full preprocessing: normalize, tokenize, extract years, return structure."""
        raw = (keyword or '').strip()
        normalized = SearchUtils.normalize_text(raw)
        tokens = SearchUtils.tokenize(raw)
        years = SearchUtils.extract_years(raw)
        return {
            'raw': raw,
            'normalized': normalized,
            'tokens': tokens,
            'years': years
        }

    @staticmethod
    def fuzzy_score(a: str, b: str) -> float:
        """Return fuzzy similarity between 0 and 1."""
        if not a or not b:
            return 0.0
        a_n = SearchUtils.normalize_text(a)
        b_n = SearchUtils.normalize_text(b)
        try:
            return difflib.SequenceMatcher(None, a_n, b_n).ratio()
        except Exception:
            return 0.0

    @staticmethod
    def token_overlap_score(query_tokens, target_text) -> float:
        """Compute token overlap ratio in [0,1]."""
        if not query_tokens:
            return 0.0
        target_tokens = set(SearchUtils.tokenize(target_text or ''))
        if not target_tokens:
            return 0.0
        matches = sum(1 for t in query_tokens if t in target_tokens)
        return matches / len(query_tokens)

    @staticmethod
    def score_candidate(candidate: dict, search_meta: dict, max_vote: int = 1) -> float:
        """
        Score a single candidate film.
        candidate: { title, directors: [..], genres: [..], year (int|None), rating (float|None), vote_count (int|None) }
        search_meta: result of tokens_from_keyword
        max_vote: used to normalize popularity
        Returns float score (higher better).
        """
        weights = {
            'title': 0.60,
            'director': 0.15,
            'genre': 0.15,
            'year': 0.10,
            'rating': 0.10,
            'popularity': 0.10
        }
        q_tokens = search_meta.get('tokens', [])
        raw = search_meta.get('raw', '')
        years = search_meta.get('years', [])

        # title score: fuzzy OR token overlap
        title = candidate.get('title') or ''
        title_fuzzy = SearchUtils.fuzzy_score(raw, title)
        title_overlap = SearchUtils.token_overlap_score(q_tokens, title)
        title_score = max(title_fuzzy, title_overlap)

        # director score: best match across directors
        director_score = 0.0
        for d in (candidate.get('directors') or []):
            director_score = max(director_score, SearchUtils.fuzzy_score(raw, d) or 0.0)

        # genre score: check overlap between query tokens and genre names
        genre_score = 0.0
        for g in (candidate.get('genres') or []):
            genre_score = max(genre_score, SearchUtils.token_overlap_score(q_tokens, g), SearchUtils.fuzzy_score(raw, g))

        # year score: if user provided any year and it matches candidate year
        year_score = 0.0
        cand_year = candidate.get('year')
        if cand_year and years:
            # if any extracted year equals candidate year, full match
            year_score = 1.0 if any(int(y) == int(cand_year) for y in years) else 0.0

        # rating normalized [0,1] assuming rating up to 10
        rating = candidate.get('rating') or 0.0
        rating_score = max(0.0, min(1.0, float(rating) / 10.0))

        # popularity normalized by max_vote
        vote = candidate.get('vote_count') or 0
        try:
            pop_score = (vote / max_vote) if max_vote and max_vote > 0 else 0.0
            # soften with sqrt
            pop_score = math.sqrt(pop_score) if pop_score > 0 else 0.0
        except Exception:
            pop_score = 0.0

        final = (
            title_score * weights['title'] +
            director_score * weights['director'] +
            genre_score * weights['genre'] +
            year_score * weights['year'] +
            rating_score * weights['rating'] +
            pop_score * weights['popularity']
        )
        return float(final)


class TrieNode:
    """Node for Trie data structure."""

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word = None  # Store the complete word at end nodes


class Trie:
    """Trie (prefix tree) with edit distance search capabilities."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """Insert a word into the trie."""
        if not word:
            return

        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.word = word

    def search_prefix(self, prefix: str, max_results: int = 10) -> list:
        """Search for words starting with the given prefix."""
        if not prefix:
            return []

        node = self.root
        # Navigate to the prefix end
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all words under this node
        results = []
        self._collect_words(node, results, max_results)
        return results

    def _collect_words(self, node: TrieNode, results: list, max_results: int):
        """Recursively collect words from the trie node."""
        if len(results) >= max_results:
            return

        if node.is_end_of_word and node.word:
            results.append(node.word)

        for child in node.children.values():
            self._collect_words(child, results, max_results)

    def search_with_edit_distance(self, word: str, max_distance: int = 3, max_results: int = 5) -> list:
        """
        Search for words within edit distance using weighted edit distance.
        Returns list of (word, distance) tuples.
        """
        if not word:
            return []

        candidates = []
        word_lower = word.lower()

        # Use a more efficient approach: DFS with pruning
        self._edit_distance_search(self.root, "", word_lower, candidates, max_distance, max_results)

        # Sort by distance, then alphabetically
        candidates.sort(key=lambda x: (x[1], x[0]))

        return [(word, dist) for word, dist in candidates[:max_results]]

    def _edit_distance_search(self, node: TrieNode, current_prefix: str, target: str,
                            candidates: list, max_distance: int, max_results: int):
        """DFS search with edit distance pruning."""
        if len(candidates) >= max_results:
            return

        # If we've reached a complete word, calculate its edit distance
        if node.is_end_of_word and node.word:
            distance = self._simple_edit_distance(current_prefix, target)
            if distance <= max_distance:
                candidates.append((node.word, distance))

        # Prune: if current prefix is already too different, don't continue
        if current_prefix:
            current_dist = self._simple_edit_distance(current_prefix, target[:len(current_prefix)])
            if current_dist > max_distance:
                return

        # Continue DFS
        for char, child_node in node.children.items():
            self._edit_distance_search(child_node, current_prefix + char, target,
                                    candidates, max_distance, max_results)

    def _simple_edit_distance(self, s1: str, s2: str) -> int:
        """Calculate simple Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._simple_edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]