import http from './http.js';

/**
 * Get authenticated user's information
 * @returns {Promise} Response containing user data
 */
export const getUserInfo = () => {
  return http.get('/users/me');
};

/**
 * Update authenticated user's information
 * @param {Object} userData - User data to update
 * @param {string} [userData.username] - New username
 * @param {string} [userData.email] - New email address
 * @param {string} [userData.bio] - New bio information
 * @param {File} [avatar] - New avatar file (optional)
 * @returns {Promise} Response from the server
 */
export const updateUserInfo = (userData, avatar = null) => {
  const formData = new FormData();

  // Add text fields
  Object.keys(userData).forEach(key => {
    if (userData[key] !== null && userData[key] !== undefined) {
      formData.append(key, userData[key]);
    }
  });

  // Add avatar file if provided
  if (avatar) {
    formData.append('avatar', avatar);
  }

  return http.put('/users/me', formData);
};

/**
 * Update authenticated user's password
 * @param {Object} passwordData - Password update data
 * @param {string} passwordData.old_password - Current password
 * @param {string} passwordData.new_password - New password
 * @returns {Promise} Response from the server
 */
export const updatePassword = (passwordData) => {
  return http.put('/users/me/password', passwordData);
};

/**
 * Delete authenticated user's account
 * @param {Object} deleteData - Account deletion data
 * @param {string} deleteData.password - User's password for confirmation
 * @returns {Promise} Response from the server
 */
export const deleteUserAccount = (deleteData) => {
  return http.delete('/users/me', { data: deleteData });
};

/**
 * Get authenticated user's tags
 * @returns {Promise} Response containing user's tags array
 */
export const getUserTags = () => {
  return http.get('/users/me/tags');
};

/**
 * Add a tag to authenticated user
 * @param {Object} tagData - Tag data
 * @param {string} tagData.name - Tag name to add
 * @returns {Promise} Response from the server
 */
export const addUserTag = (tagData) => {
  return http.post('/users/me/tags', tagData);
};

/**
 * Get popular tags ordered by usage count
 * @returns {Promise} Response containing popular tags array
 */
export const getPopularTags = () => {
  return http.get('/tags');
};

/**
 * Add a film to authenticated user's favorites
 * @param {Object} favoriteData - Favorite data
 * @param {number} favoriteData.film_id - Film ID to add to favorites
 * @returns {Promise} Response from the server
 */
export const addFavorite = (favoriteData) => {
  return http.post('/users/me/favorites', favoriteData);
};

/**
 * Remove a film from authenticated user's favorites
 * @param {Object} favoriteData - Favorite data
 * @param {number} favoriteData.film_id - Film ID to remove from favorites
 * @returns {Promise} Response from the server
 */
export const removeFavorite = (favoriteData) => {
  return http.delete('/users/me/favorites', { data: favoriteData });
};

/**
 * Get authenticated user's favorite films
 * @returns {Promise} Response containing user's favorite films array
 */
export const getFavorites = () => {
  return http.get('/users/me/favorites');
};

/**
 * Add or update rating for a film by authenticated user
 * @param {Object} ratingData - Rating data
 * @param {number} ratingData.film_id - Film ID to rate
 * @param {number} ratingData.rating - Rating value
 * @returns {Promise} Response from the server
 */
export const addRating = (ratingData) => {
  return http.post('/users/me/ratings', ratingData);
};

/**
 * Get authenticated user's rating for a specific film
 * @param {number} filmId - Film ID to get rating for
 * @returns {Promise} Response containing user's rating for the film
 */
export const getRating = (filmId) => {
  return http.get(`/users/me/ratings/${filmId}`);
};

/**
 * Get recommended tags for authenticated user based on keyword
 * @param {Object} keywordData - Keyword data
 * @param {string} keywordData.keyword - Keyword to search for tags
 * @returns {Promise} Response containing recommended tags array
 */
export const getRecommendedTags = (keywordData) => {
  return http.post('/users/me/tag-tips', keywordData);
};

/**
 * Get user's rating for a specific film
 * @param {number} filmId - Film ID
 * @returns {Promise} Response containing user's rating
 */
export const getUserRating = (filmId) => {
  return http.get(`/users/me/ratings/${filmId}`);
};

/**
 * Submit or update rating for a film
 * @param {Object} ratingData - Rating data
 * @param {number} ratingData.film_id - Film ID
 * @param {number} ratingData.rating - Rating value (1-10)
 * @returns {Promise} Response from the server
 */
export const submitRating = (ratingData) => {
  return http.post('/users/me/ratings', ratingData);
};

/**
 * Get authenticated user's profile information
 * @returns {Promise} Response containing user profile data
 */
export const getUserProfile = () => {
  return http.get('/users/me');
};

/**
 * Get authenticated user's watchlist (favorites)
 * @returns {Promise} Response containing user's watchlist
 */
export const getUserWatchlist = () => {
  return http.get('/users/me/favorites');
};

/**
 * Remove a tag from authenticated user
 * @param {number} tagId - Tag ID to remove
 * @returns {Promise} Response from the server
 */
export const removeUserTag = (tagId) => {
  return http.delete(`/users/me/tags/${tagId}`);
};

/**
 * Search for tags by keyword using tag-tips API
 * @param {string} keyword - Keyword to search for
 * @returns {Promise} Response containing matching tags
 */
export const searchTags = (keyword) => {
  return http.post('/users/me/tag-tips', { keyword });
};

/**
 * Update user profile (alias for updateUserInfo)
 * @param {Object} userData - User data to update
 * @returns {Promise} Response from the server
 */
export const updateUserProfile = updateUserInfo;

/**
 * Change user password (alias for updatePassword)
 * @param {Object} passwordData - Password data
 * @param {string} passwordData.current_password - Current password
 * @param {string} passwordData.new_password - New password
 * @returns {Promise} Response from the server
 */
export const changePassword = updatePassword;

/**
 * Get authenticated user's posts
 * @param {number} offset - Offset for pagination
 * @param {number} limit - Number of posts to fetch
 * @returns {Promise} Response containing user's posts
 */
export const getUserPosts = (offset = 0, limit = 20) => {
  return http.get(`/users/me/posts?offset=${offset}&limit=${limit}`);
};

/**
 * Get authenticated user's comments
 * @param {number} offset - Offset for pagination
 * @param {number} limit - Number of comments to fetch
 * @returns {Promise} Response containing user's comments
 */
export const getUserComments = (offset = 0, limit = 20) => {
  return http.get(`/users/me/comments?offset=${offset}&limit=${limit}`);
};

/**
 * Update authenticated user's post
 * @param {number} postId - Post ID to update
 * @param {Object} postData - Post data to update
 * @param {string} [postData.title] - New title
 * @param {string} [postData.content] - New content
 * @param {Array} [postData.tags] - New tags array
 * @returns {Promise} Response from the server
 */
export const updateUserPost = (postId, postData) => {
  return http.put(`/users/me/posts/${postId}`, postData);
};

/**
 * Update authenticated user's comment
 * @param {number} commentId - Comment ID to update
 * @param {Object} commentData - Comment data to update
 * @param {string} commentData.content - New content
 * @returns {Promise} Response from the server
 */
export const updateUserComment = (commentId, commentData) => {
  return http.put(`/users/me/comments/${commentId}`, commentData);
};

/**
 * Generic edit function for user content (posts, comments, etc.)
 * @param {string} type - Type of content to edit ('post' or 'comment')
 * @param {number} id - ID of the content to edit
 * @param {Object} data - Data to update
 * @returns {Promise} Response from the server
 */
export const editUserContent = (type, id, data) => {
  if (type === 'post') {
    return updateUserPost(id, data);
  } else if (type === 'comment') {
    return updateUserComment(id, data);
  } else {
    throw new Error(`Unsupported content type: ${type}`);
  }
};