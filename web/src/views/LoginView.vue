<template>
  <div class="login-container">

    <!-- Login Form -->
    <div class="login-content">
      <div class="login-card">
        <h1 class="login-title">Sign In</h1>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="username" class="form-label">Username or Email</label>
            <input
              id="username"
              v-model="credentials.uid"
              type="text"
              class="form-input"
              :class="{ 'input-error': validationErrors.uid }"
              placeholder="Enter your username or email"
              required
            />
            <div v-if="validationErrors.uid" class="input-error-text">{{ validationErrors.uid }}</div>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input
              id="password"
              v-model="credentials.password"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.password }"
              placeholder="Enter your password"
              required
            />
            <div v-if="validationErrors.password" class="input-error-text">{{ validationErrors.password }}</div>
          </div>

          <button
            type="submit"
            class="login-button"
            :disabled="authStore.isLoading"
          >
            {{ authStore.isLoading ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>

        <!-- Sign Up Link -->
        <div class="signup-link">
          <span>Don't have an account? </span>
          <router-link to="/register" class="signup-text">Sign up here</router-link>
        </div>
      </div>
    </div>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import Toast from '@/components/Toast.vue'

// Initialize auth store and router
const authStore = useAuthStore()
const router = useRouter()

// Form data
const credentials = ref({
  uid: '',
  password: ''
})

// Toast component reference
const toastRef = ref(null)

// Validation errors
const validationErrors = ref({
  uid: '',
  password: ''
})

// Real-time validation
const validateField = (field) => {
  const value = credentials.value[field]

  switch (field) {
    case 'uid':
      if (!value.trim()) {
        validationErrors.value.uid = 'Username or email is required'
      } else {
        validationErrors.value.uid = ''
      }
      break

    case 'password':
      if (!value) {
        validationErrors.value.password = 'Password is required'
      } else {
        validationErrors.value.password = ''
      }
      break
  }
}

// Watch for form changes
import { watch } from 'vue'
watch(() => credentials.value.uid, () => validateField('uid'))
watch(() => credentials.value.password, () => validateField('password'))

// Form validation
const isFormValid = computed(() => {
  return credentials.value.uid.trim() &&
         credentials.value.password &&
         !validationErrors.value.uid &&
         !validationErrors.value.password
})

// Handle login submission
const handleLogin = async () => {
  // Check for validation errors
  const hasErrors = Object.values(validationErrors.value).some(error => error !== '')

  if (hasErrors) {
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  const result = await authStore.login(credentials.value)

  if (result.success) {
    // Redirect to home page or previous page after successful login
    router.push('/')
  } else {
    // Display error message from backend using Toast
    // DON'T clear the form on failure
    toastRef.value?.addToast(result.error || 'Login failed', 'error')
  }
}

// Component mounted
onMounted(() => {
  // No additional setup needed
})
</script>

<style scoped>
/* Global styles based on design document */
.login-container {
  min-height: 100vh;
  background-color: #000000; /* Black background */
  color: #ffffff; /* White font */
  font-family: 'Verdana', sans-serif;
}

/* Login Content */
.login-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: 2rem;
}

.login-card {
  background-color: #121212; /* Dark card background */
  border-radius: 8px;
  padding: 3rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.login-title {
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 2rem;
  position: relative;
}

.login-title::before {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -10px;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background-color: #f5c518; /* Yellow decorative bar */
}

/* Form Styles */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  color: #ffffff;
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-input {
  background-color: #1a1a1a;
  border: 1px solid #333333;
  border-radius: 4px;
  padding: 0.75rem;
  color: #ffffff;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border: 2px solid #f5c518;
}

.form-input.input-error {
  border-color: #F5C518;
}

.form-input.input-error:focus {
  border-color: #F5C518;
}

.form-input::placeholder {
  color: #888888;
}

/* Password input container */
.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container .form-input {
  padding-right: 50px; /* Space for the toggle button */
}

.password-toggle-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.password-toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.password-icon {
  width: 20px;
  height: 20px;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.password-toggle-btn:hover .password-icon {
  opacity: 1;
}

/* Button Styles */
.login-button {
  background-color: #3552b0;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 0.5rem;
}

.login-button:hover:not(:disabled) {
  background-color: #4682d6; /* Darker blue on hover */
}

.login-button:disabled {
  background-color: #666666;
  cursor: not-allowed;
}


/* Sign Up Link */
.signup-link {
  text-align: center;
  margin-top: 2rem;
  color: #cccccc;
  font-size: 0.9rem;
}

.signup-text {
  color: #5799ef; /* Light blue */
  text-decoration: none;
  font-weight: 500;
}

.signup-text:hover {
  text-decoration: underline;
}

/* Validation Styles */
.input-error-text {
  color: #F5C518;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Password Visibility Toggle Button Styles */
.form-input[type="password"]::-webkit-password-toggle-button {
  -webkit-appearance: none;
  background-color: #cccccc !important;
  color: #000000 !important;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.form-input[type="password"]::-webkit-password-toggle-button:hover {
  background-color: #aaaaaa !important;
}

/* Firefox password reveal button */
.form-input[type="password"]::-moz-reveal-button {
  background-color: #cccccc !important;
  color: #000000 !important;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.form-input[type="password"]::-moz-reveal-button:hover {
  background-color: #aaaaaa !important;
}

/* Microsoft Edge password reveal */
.form-input[type="password"]::-ms-reveal {
  background-color: #cccccc !important;
  color: #000000 !important;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.form-input[type="password"]::-ms-reveal:hover {
  background-color: #aaaaaa !important;
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-card {
    padding: 2rem;
    margin: 1rem;
  }

  .login-title {
    font-size: 1.5rem;
  }
}
</style>
