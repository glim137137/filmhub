import http from './http.js';

/**
 * Film API - Movie related operations
 */

/**
 * Get top rated films
 * @returns {Promise} Response with top rated films
 */
export const getTopRatedFilms = () => {
  return http.get('/films/top-rated');
};

/**
 * Get latest films
 * @returns {Promise} Response with latest films
 */
export const getLatestFilms = () => {
  return http.get('/films/latest');
};

/**
 * Get recommended films for the current user
 * @returns {Promise} Response with recommended films
 */
export const getRecommendedFilms = () => {
  return http.get('/films/recommend');
};

/**
 * Search films by keyword
 * @param {string} keyword - Search keyword
 * @returns {Promise} Response with search results
 */
export const searchFilms = (keyword) => {
  return http.post('/films', { keyword });
};

/**
 * Get film details by ID
 * @param {number} filmId - Film ID
 * @returns {Promise} Response with film details
 */
export const getFilmById = (filmId) => {
  return http.get(`/films/${filmId}`);
};

/**
 * Get film details by title
 * @param {string} title - Film title
 * @returns {Promise} Response with film details
 */
export const getFilmByTitle = (title) => {
  return http.get(`/films/title/${encodeURIComponent(title)}`);
};

/**
 * Get posts related to a film
 * @param {number} filmId - Film ID
 * @param {Object} params - Pagination parameters
 * @param {number} params.page - Page number (default: 1)
 * @param {number} params.per_page - Items per page (default: 10)
 * @returns {Promise} Response with film posts
 */
export const getFilmPosts = (filmId, params = {}) => {
  const { page = 1, per_page = 10 } = params;
  return http.post(`/films/${filmId}/posts`, { page, per_page });
};

/**
 * Get filtered films with multiple criteria
 * @param {Object} filters - Filter criteria
 * @param {number} filters.genre_id - Genre ID (optional)
 * @param {string} filters.year - Release year (optional)
 * @param {string} filters.language - Language (optional)
 * @param {number} filters.page - Page number (default: 1)
 * @param {number} filters.per_page - Items per page (default: 20)
 * @returns {Promise} Response with filtered films
 */
export const getFilteredFilms = (filters = {}) => {
  return http.post('/films/filter', filters);
};

/**
 * Get all genres
 * @returns {Promise} Response with all genres
 */
export const getAllGenres = () => {
  return http.get('/genres');
};
