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


class FilmTrieNode:
    """Node for Film Trie data structure."""

    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.films = []  # Store film IDs that match this word/prefix


class FilmTrie:
    """Trie for film search with title, director, and year matching."""

    def __init__(self):
        self.root = FilmTrieNode()
        self.films_data = {}  # Store film data by ID

    def insert_film(self, film_data: dict):
        """Insert a film into the trie with its searchable fields."""
        film_id = film_data.get('id')
        if not film_id:
            return

        # Store film data
        self.films_data[film_id] = film_data

        # Index searchable fields
        searchable_fields = []

        # Title
        title = film_data.get('title', '')
        if title:
            searchable_fields.append(('title', title))

        # Directors
        directors = film_data.get('directors', [])
        for director in directors:
            if director:
                searchable_fields.append(('director', director))

        # Year
        year = film_data.get('year')
        if year:
            searchable_fields.append(('year', str(year)))

        # Insert each field into trie
        for field_type, text in searchable_fields:
            self._insert_text(text.lower(), film_id, field_type)

    def _insert_text(self, text: str, film_id: int, field_type: str):
        """Insert text into trie with film reference."""
        if not text:
            return

        node = self.root
        for char in text:
            if char not in node.children:
                node.children[char] = FilmTrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        if film_id not in node.films:
            node.films.append(film_id)

    def search_films(self, keyword: str, max_edit_distance: int = 2, max_results: int = 10) -> list:
        """
        Search films using Trie + edit distance.
        Returns list of film data sorted by relevance.
        """
        if not keyword:
            return []

        keyword_lower = keyword.lower()
        candidates = set()

        # Find exact prefix matches
        exact_matches = self._find_exact_matches(keyword_lower)
        candidates.update(exact_matches)

        # Find edit distance matches
        edit_matches = self._find_edit_distance_matches(keyword_lower, max_edit_distance)
        candidates.update(edit_matches)

        # Get film data and score results
        results = []
        for film_id in candidates:
            if film_id in self.films_data:
                film_data = self.films_data[film_id].copy()
                score = self._calculate_relevance_score(film_data, keyword_lower)
                if score > 0:
                    film_data['search_score'] = score
                    results.append(film_data)

        # Sort by relevance score
        results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
        return results[:max_results]

    def _find_exact_matches(self, keyword: str) -> set:
        """Find films with exact prefix matches."""
        candidates = set()

        # Navigate to keyword end
        node = self.root
        for char in keyword:
            if char not in node.children:
                return candidates
            node = node.children[char]

        # Collect all films from this prefix
        self._collect_films_from_node(node, candidates)
        return candidates

    def _find_edit_distance_matches(self, keyword: str, max_distance: int) -> set:
        """Find films using edit distance search."""
        candidates = set()
        self._edit_distance_search(self.root, "", keyword, candidates, max_distance)
        return candidates

    def _edit_distance_search(self, node: FilmTrieNode, current_prefix: str, target: str,
                            candidates: set, max_distance: int):
        """DFS search with edit distance pruning."""
        # If we've reached a complete word, add its films
        if node.is_end_of_word:
            distance = self._simple_edit_distance(current_prefix, target)
            if distance <= max_distance:
                candidates.update(node.films)

        # Prune: if current prefix is already too different, don't continue
        if current_prefix:
            current_dist = self._simple_edit_distance(current_prefix, target[:len(current_prefix)])
            if current_dist > max_distance:
                return

        # Continue DFS
        for char, child_node in node.children.items():
            self._edit_distance_search(child_node, current_prefix + char, target,
                                    candidates, max_distance)

    def _collect_films_from_node(self, node: FilmTrieNode, candidates: set):
        """Recursively collect all films from trie node and its children."""
        candidates.update(node.films)

        for child in node.children.values():
            self._collect_films_from_node(child, candidates)

    def _calculate_relevance_score(self, film_data: dict, keyword: str) -> float:
        """Calculate relevance score for a film based on keyword match."""
        score = 0.0
        keyword_lower = keyword.lower()

        # Title match (highest weight)
        title = film_data.get('title', '').lower()
        if keyword_lower in title:
            score += 1.0  # Exact substring match
        elif self._simple_edit_distance(keyword_lower, title[:len(keyword_lower)]) <= 1:
            score += 0.8  # Close match

        # Director match (medium weight)
        directors = film_data.get('directors', [])
        for director in directors:
            director_lower = director.lower()
            if keyword_lower in director_lower:
                score += 0.6
                break

        # Year match (lower weight)
        year = str(film_data.get('year', ''))
        if keyword_lower == year:
            score += 0.4

        # Popularity bonus
        rating = film_data.get('rating', 0)
        vote_count = film_data.get('vote_count', 0)
        popularity_bonus = min(0.3, (rating * vote_count) / 10000)  # Cap at 0.3
        score += popularity_bonus

        return score

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