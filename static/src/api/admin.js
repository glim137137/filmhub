import http from './http.js';

/**
 * Get admin statistics
 * @returns {Promise} Response containing admin stats
 */
export const getAdminStats = () => {
  return http.get('/admin/stats');
};

/**
 * Get total users count
 * @returns {Promise} Response containing total users
 */
export const getTotalUsers = () => {
  return http.get('/admin/stats/users');
};

/**
 * Get total posts count
 * @returns {Promise} Response containing total posts
 */
export const getTotalPosts = () => {
  return http.get('/admin/stats/posts');
};

/**
 * Get total comments count
 * @returns {Promise} Response containing total comments
 */
export const getTotalComments = () => {
  return http.get('/admin/stats/comments');
};

/**
 * Get total films count
 * @returns {Promise} Response containing total films
 */
export const getTotalFilms = () => {
  return http.get('/admin/stats/films');
};

/**
 * Add a new film with optional poster upload
 * @param {Object} filmData - Film data
 * @param {string} filmData.title - Film title (required)
 * @param {number} [filmData.tmdb_id] - TMDB ID
 * @param {string} [filmData.overview] - Film description
 * @param {string} [filmData.release_date] - Release date (YYYY-MM-DD)
 * @param {number} [filmData.duration] - Duration in minutes
 * @param {number} [filmData.rating] - Film rating
 * @param {number} [filmData.vote_count] - Vote count
 * @param {string} [filmData.language] - Language code
 * @param {string} [filmData.poster_url] - Poster URL
 * @param {number[]} [filmData.genre_ids] - Array of genre IDs
 * @param {number[]} [filmData.director_ids] - Array of director IDs
 * @param {File} [posterFile] - Poster image file to upload
 * @returns {Promise} Response containing created film
 */
export const addFilm = (filmData, posterFile = null) => {
  // If there's a poster file, use FormData for multipart upload
  if (posterFile) {
    const formData = new FormData();

    // Add film data as JSON string
    formData.append('film_data', JSON.stringify(filmData));

    // Add poster file
    formData.append('poster', posterFile);

    // Use http utility with FormData
    return http.post('/admin/films', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  } else {
    // No file upload, use regular JSON request
    return http.post('/admin/films', filmData);
  }
};

/**
 * Delete a film by ID
 * @param {number} filmId - Film ID to delete
 * @returns {Promise} Response from the server
 */
export const deleteFilm = (filmId) => {
  return http.delete(`/admin/films/${filmId}`);
};

/**
 * Get films with pagination for admin panel
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number
 * @param {number} [params.per_page=20] - Items per page
 * @param {string} [params.title] - Search by film title
 * @returns {Promise} Response containing paginated films
 */
export const getAdminFilms = (params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page);
  if (params.per_page) queryParams.append('per_page', params.per_page);
  if (params.title) queryParams.append('title', params.title);

  const queryString = queryParams.toString();
  const url = `/admin/films${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Get users with pagination for admin panel
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number
 * @param {number} [params.per_page=20] - Items per page
 * @param {string} [params.username] - Search by username
 * @returns {Promise} Response containing paginated users
 */
export const getAdminUsers = (params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page);
  if (params.per_page) queryParams.append('per_page', params.per_page);
  if (params.username) queryParams.append('username', params.username);

  const queryString = queryParams.toString();
  const url = `/admin/users${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Delete a user by admin
 * @param {number} userId - User ID to delete
 * @returns {Promise} Response from the server
 */
export const deleteUserByAdmin = (userId) => {
  return http.delete(`/admin/users/${userId}`);
};

/**
 * Get posts by a specific user with pagination
 * @param {number} userId - User ID
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number
 * @param {number} [params.per_page=20] - Items per page
 * @returns {Promise} Response containing paginated posts
 */
export const getUserPosts = (userId, params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page);
  if (params.per_page) queryParams.append('per_page', params.per_page);

  const queryString = queryParams.toString();
  const url = `/admin/users/${userId}/posts${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Delete a specific post by admin
 * @param {number} postId - Post ID to delete
 * @returns {Promise} Response from the server
 */
export const deletePostByAdmin = (postId) => {
  return http.delete(`/admin/posts/${postId}`);
};

/**
 * Get comments by a specific user with pagination
 * @param {number} userId - User ID
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number
 * @param {number} [params.per_page=20] - Items per page
 * @returns {Promise} Response containing paginated comments
 */
export const getUserComments = (userId, params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page);
  if (params.per_page) queryParams.append('per_page', params.per_page);

  const queryString = queryParams.toString();
  const url = `/admin/users/${userId}/comments${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Delete a specific comment by admin
 * @param {number} commentId - Comment ID to delete
 * @returns {Promise} Response from the server
 */
export const deleteCommentByAdmin = (commentId) => {
  return http.delete(`/admin/comments/${commentId}`);
};

/**
 * Get logs statistics
 * @returns {Promise} Response containing logs statistics
 */
export const getLogsStats = () => {
  return http.get('/admin/logs/stats');
};

/**
 * Get top active users based on log activity
 * @param {Object} params - Query parameters
 * @param {number} [params.limit=10] - Number of users to return
 * @returns {Promise} Response containing top active users
 */
export const getTopActiveUsers = (params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.limit) queryParams.append('limit', params.limit);

  const queryString = queryParams.toString();
  const url = `/admin/stats/top-active-users${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Get recent logs with pagination
 * @param {Object} params - Query parameters
 * @param {number} [params.page=1] - Page number
 * @param {number} [params.per_page=50] - Number of logs per page
 * @returns {Promise} Response containing paginated logs
 */
export const getRecentLogs = (params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page);
  if (params.per_page) queryParams.append('per_page', params.per_page);

  const queryString = queryParams.toString();
  const url = `/admin/logs/recent${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};

/**
 * Get logs for a specific user
 * @param {number} userId - User ID
 * @param {Object} params - Query parameters
 * @param {number} [params.limit=50] - Maximum number of logs to return
 * @returns {Promise} Response containing user logs
 */
export const getUserLogs = (userId, params = {}) => {
  const queryParams = new URLSearchParams();

  if (params.limit) queryParams.append('limit', params.limit);

  const queryString = queryParams.toString();
  const url = `/admin/logs/users/${userId}${queryString ? '?' + queryString : ''}`;

  return http.get(url);
};