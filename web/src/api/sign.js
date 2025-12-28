import http from './http.js';

/**
 * Sign up API - Register a new user account
 * @param {Object} userData - User registration data
 * @param {string} userData.username - Username for the new account
 * @param {string} userData.email - Email address for the new account
 * @param {string} userData.password - Password for the new account
 * @returns {Promise} Response from the server
 */
export const signup = (userData) => {
  return http.post('/signup', userData);
};

/**
 * Sign in API - Authenticate user and get access token
 * @param {Object} credentials - User login credentials
 * @param {string} credentials.uid - Username or email address
 * @param {string} credentials.password - User password
 * @returns {Promise} Response containing access token
 */
export const signin = (credentials) => {
  return http.post('/signin', credentials);
};
