import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { signin as apiSignin, signup as apiSignup } from '@/api/sign.js'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)

  // Computed properties
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value
  })

  const username = computed(() => {
    return user.value?.username || ''
  })

  const userId = computed(() => {
    return user.value?.id || null
  })

  // Parse JWT token to get user info (simplified, no signature verification)
  const parseToken = (tokenStr) => {
    if (!tokenStr) return null

    try {
      const payload = tokenStr.split('.')[1]
      const decodedPayload = JSON.parse(atob(payload))
      return {
        id: parseInt(decodedPayload.sub),
        username: decodedPayload.username,
        email: decodedPayload.email
      }
    } catch (error) {
      console.error('Failed to parse token:', error)
      return null
    }
  }

  // Login
  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await apiSignin(credentials)

      // Check backend response format: code 1 = success, 0 = failure
      if (response.code === 1 && response.data) {
        const { token: newToken, user: userData } = response.data

        // Save token to localStorage and state
        token.value = newToken
        localStorage.setItem('token', newToken)

        // Save user info
        user.value = userData

        // Check if user is admin and redirect to admin panel
        if (userData.username === 'admin') {
          // Use setTimeout to ensure navigation happens after login process completes
          setTimeout(() => {
            window.location.href = '/admin'
          }, 100)
        }

        return { success: true }
      } else {
        throw new Error(response.msg || 'Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // Register
  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await apiSignup(userData)

      if (response.code === 1) {
        return { success: true }
      } else {
        throw new Error(response.msg || 'Registration failed')
      }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.message }
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // Initialize - check localStorage token
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      const userData = parseToken(storedToken)
      if (userData) {
        token.value = storedToken
        user.value = userData
      } else {
        // Invalid token, clear it
        localStorage.removeItem('token')
      }
    }
  }

  // Check if token is expired (simplified)
  const isTokenExpired = () => {
    if (!token.value) return true

    try {
      const payload = token.value.split('.')[1]
      const decodedPayload = JSON.parse(atob(payload))
      const currentTime = Date.now() / 1000

      return decodedPayload.exp < currentTime
    } catch (error) {
      return true
    }
  }

  return {
    // State
    user,
    token,
    isLoading,

    // Computed properties
    isAuthenticated,
    username,
    userId,

    // Methods
    login,
    register,
    logout,
    initializeAuth,
    isTokenExpired
  }
})
