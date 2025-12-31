<template>
  <div class="register-container">
    <!-- Login Form -->
    <div class="register-content">
      <div class="register-card">
        <h1 class="register-title">Sign Up</h1>

        <!-- Register Form -->
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              id="username"
              v-model="registerForm.username"
              type="text"
              class="form-input"
              :class="{ 'input-error': validationErrors.username }"
              placeholder="Choose a username"
              required
              minlength="3"
              maxlength="50"
            />
            <div v-if="validationErrors.username" class="input-error-text">{{ validationErrors.username }}</div>
          </div>

          <div class="form-group">
            <label for="email" class="form-label">Email Address</label>
            <input
              id="email"
              v-model="registerForm.email"
              type="email"
              class="form-input"
              :class="{ 'input-error': validationErrors.email }"
              placeholder="Enter your email"
              required
            />
            <div v-if="validationErrors.email" class="input-error-text">{{ validationErrors.email }}</div>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <input
              id="password"
              v-model="registerForm.password"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.password }"
              placeholder="Create a password"
              required
              minlength="8"
            />
            <div v-if="validationErrors.password" class="input-error-text">{{ validationErrors.password }}</div>
            <div v-else-if="passwordStrength.level > 0" class="password-strength">
              <div class="strength-meter">
                <div
                  class="strength-bar"
                  :class="passwordStrength.class"
                  :style="{ width: passwordStrength.width }"
                ></div>
              </div>
              <span class="strength-text">{{ passwordStrength.text }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="registerForm.confirmPassword"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.confirmPassword }"
              placeholder="Confirm your password"
              required
            />
            <div v-if="validationErrors.confirmPassword" class="input-error-text">{{ validationErrors.confirmPassword }}</div>
          </div>

          <button
            type="submit"
            class="register-button"
            :disabled="authStore.isLoading"
          >
            {{ authStore.isLoading ? 'Creating Account...' : 'Sign Up' }}
          </button>
        </form>

        <!-- Sign In Link -->
        <div class="signin-link">
          <span>Already have an account? </span>
          <router-link to="/login" class="signin-text">Sign in here</router-link>
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
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// Toast component reference
const toastRef = ref(null)

// Validation errors
const validationErrors = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// Password strength
const passwordStrength = ref({
  level: 0,
  text: '',
  class: '',
  width: '0%'
})

// Email validation helper
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Password strength validation
const validatePasswordStrength = (password) => {
  if (!password) {
    return { level: 0, text: '', class: '', width: '0%' }
  }

  let score = 0
  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]/.test(password)
  }

  score = Object.values(checks).filter(Boolean).length

  if (score <= 2) {
    return { level: 1, text: 'Weak', class: 'weak', width: '33%' }
  } else if (score <= 4) {
    return { level: 2, text: 'Medium', class: 'medium', width: '66%' }
  } else {
    return { level: 3, text: 'Strong', class: 'strong', width: '100%' }
  }
}

// Real-time validation
const validateField = (field) => {
  const value = registerForm.value[field]

  switch (field) {
    case 'username':
      if (!value.trim()) {
        validationErrors.value.username = ''
      } else if (value.trim().length < 3) {
        validationErrors.value.username = 'Username must be at least 3 characters long'
      } else if (value.trim().length > 50) {
        validationErrors.value.username = 'Username must be less than 50 characters'
      } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
        validationErrors.value.username = 'Username can only contain letters, numbers, underscores and hyphens'
      } else {
        validationErrors.value.username = ''
      }
      break

    case 'email':
      if (!value.trim()) {
        validationErrors.value.email = ''
      } else if (!isValidEmail(value)) {
        validationErrors.value.email = 'Please enter a valid email address'
      } else {
        validationErrors.value.email = ''
      }
      break

    case 'password':
      passwordStrength.value = validatePasswordStrength(value)
      if (!value) {
        validationErrors.value.password = ''
      } else if (value.length < 8) {
        validationErrors.value.password = 'Password must be at least 8 characters long'
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])/.test(value)) {
        validationErrors.value.password = 'Password must contain uppercase, lowercase, number and special character'
      } else {
        validationErrors.value.password = ''
      }
      // Also validate confirm password when password changes
      validateField('confirmPassword')
      break

    case 'confirmPassword':
      if (!value) {
        validationErrors.value.confirmPassword = ''
      } else if (value !== registerForm.value.password) {
        validationErrors.value.confirmPassword = 'Passwords do not match'
      } else {
        validationErrors.value.confirmPassword = ''
      }
      break
  }
}

// Watch for form changes
import { watch } from 'vue'
watch(() => registerForm.value.username, () => validateField('username'))
watch(() => registerForm.value.email, () => validateField('email'))
watch(() => registerForm.value.password, () => validateField('password'))
watch(() => registerForm.value.confirmPassword, () => validateField('confirmPassword'))

// Form validation - basic validation for button enablement
const isFormValid = computed(() => {
  return registerForm.value.username.trim().length >= 3 &&
         registerForm.value.email.trim() &&
         registerForm.value.password.trim() &&
         registerForm.value.confirmPassword.trim() &&
         !validationErrors.value.username &&
         !validationErrors.value.email &&
         !validationErrors.value.password &&
         !validationErrors.value.confirmPassword
})

// Handle register submission
const handleRegister = async () => {
  // Use real-time validation errors
  const hasErrors = Object.values(validationErrors.value).some(error => error !== '')

  if (hasErrors) {
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  // Additional validation
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    toastRef.value?.addToast('Passwords do not match', 'error')
    return
  }

  const result = await authStore.register({
    username: registerForm.value.username.trim(),
    email: registerForm.value.email.trim(),
    password: registerForm.value.password
  })

  if (result.success) {
    toastRef.value?.addToast('Account created successfully! You can now sign in.', 'success')
    // Clear form only on success
    registerForm.value = {
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    }
    // Reset validation errors
    validationErrors.value = {
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    }
    passwordStrength.value = { level: 0, text: '', class: '', width: '0%' }

    // Redirect to login after a delay
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } else {
    // Display error message from backend using Toast
    // DON'T clear the form on failure
    toastRef.value?.addToast(result.error || 'Registration failed', 'error')
  }
}

// Component mounted
onMounted(() => {
  // No additional setup needed
})
</script>

<style scoped>
/* Global styles based on design document */
.register-container {
  min-height: 100vh;
  background-color: #000000; /* Black background */
  color: #ffffff; /* White font */
  font-family: 'Verdana', sans-serif;
}

.register-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: 2rem;
}

.register-card {
  background-color: #121212; /* Dark card background */
  border-radius: 8px;
  padding: 3rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.register-title {
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 2rem;
  position: relative;
}

.register-title::before {
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
.register-form {
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

/* Button Styles */
.register-button {
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

.register-button:hover:not(:disabled) {
  background-color: #4682d6; /* Darker blue on hover */
}

.register-button:disabled {
  background-color: #666666;
  cursor: not-allowed;
}


/* Sign In Link */
.signin-link {
  text-align: center;
  margin-top: 2rem;
  color: #cccccc;
  font-size: 0.9rem;
}

.signin-text {
  color: #5799ef; /* Light blue */
  text-decoration: none;
  font-weight: 500;
}

.signin-text:hover {
  text-decoration: underline;
}

/* Validation Styles */
.input-error-text {
  color: #F5C518;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

.password-strength {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.strength-meter {
  flex: 1;
  height: 4px;
  background-color: #333333;
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-bar.weak {
  background-color: #F5C518;
}

.strength-bar.medium {
  background-color: #ffc107;
}

.strength-bar.strong {
  background-color: #28a745;
}

.strength-text {
  font-size: 0.85rem;
  font-weight: 500;
  min-width: 50px;
}

.strength-text[data-strength="weak"] {
  color: #dc3545;
}

.strength-text[data-strength="medium"] {
  color: #ffc107;
}

.strength-text[data-strength="strong"] {
  color: #28a745;
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
  .register-card {
    padding: 2rem;
    margin: 1rem;
  }

  .register-title {
    font-size: 1.5rem;
  }
}
</style>
