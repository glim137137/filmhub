import axios from "axios";
import { useAuthStore } from '@/stores/auth.js'

const baseUrl = '/api'

export const http = axios.create({
  baseURL: baseUrl,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// request interceptor to add auth token
http.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // For FormData requests, let browser set Content-Type automatically
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// response interceptor
http.interceptors.response.use(
  (res) => {
    console.log('response', res)
    return res.data
  },
  (error) => {
    // Handle 401 unauthorized error (token expired or invalid)
    if (error.response?.status === 401) {
      console.warn('Token expired or invalid, logging out...')

      // Clear token from localStorage directly to avoid store issues in interceptor
      localStorage.removeItem('token')

      // Reload the page to reset the application state
      // This is safer than trying to use the store in an interceptor context
      window.location.href = '/login'
    }

    const message = error?.response?.data?.message || 'Request failed'
    return Promise.reject(new Error(message))
  }
)

export default http