import http from './http.js';

/**
 * Create a new post
 * @param {Object} postData - Post creation data
 * @param {string} postData.title - Post title
 * @param {string} postData.content - Post content
 * @param {Array<string>} [postData.tags] - Array of tag names
 * @returns {Promise} Response from the server
 */
export const createPost = (postData) => {
  return http.post('/posts', postData);
};

/**
 * Delete a post
 * @param {Object} deleteData - Post deletion data
 * @param {number} deleteData.post_id - Post ID to delete
 * @returns {Promise} Response from the server
 */
export const deletePost = (deleteData) => {
  return http.delete('/posts', { data: deleteData });
};

/**
 * Update a post
 * @param {Object} updateData - Post update data
 * @param {number} updateData.post_id - Post ID to update
 * @param {string} [updateData.title] - New post title
 * @param {string} [updateData.content] - New post content
 * @param {Array<string>} [updateData.tags] - New array of tag names
 * @returns {Promise} Response from the server
 */
export const updatePost = (updateData) => {
  return http.put('/posts', updateData);
};

/**
 * Get post by ID
 * @param {number} postId - Post ID to retrieve
 * @returns {Promise} Response containing post details
 */
export const getPostById = (postId) => {
  return http.get(`/posts/${postId}`);
};

/**
 * Get posts related to a specific film
 * @param {Object} filmData - Film data
 * @param {number} filmData.film_id - Film ID
 * @returns {Promise} Response containing posts array
 */
export const getFilmPosts = (filmId) => {
  return http.post(`/films/${filmId}/posts`);
};

/**
 * Get posts by tag
 * @param {number} tagId - Tag ID
 * @returns {Promise} Response containing posts array
 */
export const getTagPosts = (tagId) => {
  return http.post(`/tags/${tagId}/posts`, {});
};

/**
 * Create a comment on a post
 * @param {Object} commentData - Comment creation data
 * @param {number} commentData.post_id - Post ID to comment on
 * @param {string} commentData.content - Comment content
 * @returns {Promise} Response from the server
 */
export const createComment = (postId, commentData) => {
  return http.post(`/posts/${postId}/comments`, commentData);
};


/**
 * Delete a comment
 * @param {Object} deleteData - Comment deletion data
 * @param {number} deleteData.comment_id - Comment ID to delete
 * @returns {Promise} Response from the server
 */
export const deleteComment = (commentId) => {
  return http.delete(`/comments/${commentId}`);
};

/**
 * Like a post
 * @param {Object} likeData - Like data
 * @param {number} likeData.post_id - Post ID to like
 * @returns {Promise} Response from the server
 */
export const likePost = (postId) => {
  return http.post(`/posts/${postId}/like`);
};

/**
 * Unlike a post
 * @param {Object} unlikeData - Unlike data
 * @param {number} unlikeData.post_id - Post ID to unlike
 * @returns {Promise} Response from the server
 */
export const unlikePost = (unlikeData) => {
  return http.delete('/posts/like', { data: unlikeData });
};