<template>
  <div class="settings-page">
    <div class="settings-container">
      <div class="settings-header">
        <h1 class="settings-title">Settings</h1>
        <button class="back-btn" @click="goBack" aria-label="Back to Profile">
          <img src="/arrow-left.svg" alt="Back" class="back-icon" />
        </button>
      </div>

      <!-- Profile Settings -->
      <section class="settings-section">
        <h2 class="section-title">Profile Information</h2>
        <form @submit.prevent="updateProfile" class="settings-form">
          <!-- Avatar Upload -->
          <div class="form-group">
            <label class="form-label">Profile Picture</label>
            <div class="avatar-upload-section">
              <div class="current-avatar">
                <img
                  :src="currentAvatarUrl"
                  :alt="profileForm.username || 'Avatar'"
                  class="avatar-preview"
                  @error="onAvatarError"
                />
              </div>
              <div class="avatar-upload-controls">
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/*"
                  @change="onAvatarSelected"
                  style="display: none"
                  aria-label="Image Input"
                />
                <button
                  type="button"
                  class="upload-btn"
                  @click="$refs.avatarInput.click()"
                  alt="Choose Image"
                  aria-label="Choose Image"
                >
                  Choose Image
                </button>
                <div class="avatar-hint">
                  <small>Recommended: Square image, max 5MB</small>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="username" class="form-label">Username</label>
            <input
              id="username"
              v-model="profileForm.username"
              type="text"
              class="form-input"
              :class="{ 'input-error': validationErrors.username }"
              required
            />
            <div v-if="validationErrors.username" class="input-error-text">{{ validationErrors.username }}</div>
          </div>

          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <input
              id="email"
              v-model="profileForm.email"
              type="text"
              class="form-input"
              :class="{ 'input-error': validationErrors.email }"
              required
            />
            <div v-if="validationErrors.email" class="input-error-text">{{ validationErrors.email }}</div>
          </div>

          <div class="form-group">
            <label for="bio" class="form-label">Bio</label>
            <textarea
              id="bio"
              v-model="profileForm.bio"
              class="form-textarea"
              rows="4"
              placeholder="Tell us about yourself..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="isUpdatingProfile">
              {{ isUpdatingProfile ? 'Updating...' : 'Update Profile' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Password Settings -->
      <section class="settings-section">
        <h2 class="section-title">Change Password</h2>
        <form @submit.prevent="changePassword" class="settings-form">
          <div class="form-group">
            <label for="currentPassword" class="form-label">Current Password</label>
            <input
              id="currentPassword"
              v-model="passwordForm.currentPassword"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.currentPassword }"
              required
            />
            <div v-if="validationErrors.currentPassword" class="input-error-text">{{ validationErrors.currentPassword }}</div>
          </div>

          <div class="form-group">
            <label for="newPassword" class="form-label">New Password</label>
            <input
              id="newPassword"
              v-model="passwordForm.newPassword"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.newPassword }"
              required
              minlength="8"
            />
            <div v-if="passwordForm.newPassword && validationErrors.newPassword" class="password-hint">
              <span class="password-hint-text">{{ validationErrors.newPassword }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirm New Password</label>
            <input
              id="confirmPassword"
              v-model="passwordForm.confirmPassword"
              type="password"
              class="form-input"
              :class="{ 'input-error': validationErrors.confirmPassword }"
              @input="validateConfirmPassword"
              required
              minlength="8"
            />
            <div v-if="validationErrors.confirmPassword" class="input-error-text">{{ validationErrors.confirmPassword }}</div>
          </div>

          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="isChangingPassword">
              {{ isChangingPassword ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Account Actions -->
      <section class="settings-section">
        <h2 class="section-title">Account Actions</h2>
        <div class="account-actions">
          <button
            class="danger-btn"
            @click="confirmDeleteAccount"
          >
            Delete Account
          </button>
        </div>
      </section>
    </div>

    <!-- Password Confirmation Modal -->
    <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Confirm Account Deletion</h3>
        <p class="modal-text">Please enter your password to confirm account deletion.</p>

        <div class="form-group">
          <label for="deletePassword" class="form-label">Password</label>
          <input
            id="deletePassword"
            v-model="deletePassword"
            type="password"
            class="form-input"
            placeholder="Enter your password"
            required
          />
        </div>

        <div class="modal-actions">
          <button class="cancel-btn" @click="closePasswordModal">Cancel</button>
          <button
            class="danger-btn"
            @click="proceedWithDeletion"
            :disabled="!deletePassword.trim()"
          >
            Confirm Deletion
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { getUserProfile, updateUserProfile, changePassword as changePasswordApi, deleteUserAccount } from '@/api/user.js'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()

// Data
const profileForm = ref({
  username: '',
  email: '',
  bio: '',
  avatar_url: ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const isUpdatingProfile = ref(false)
const isChangingPassword = ref(false)

// Validation errors
const validationErrors = ref({
  username: '',
  email: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})


// Avatar related
const avatarInput = ref(null)
const selectedAvatarFile = ref(null)
const currentAvatarUrl = ref('/anonymous.png')

// Delete account modal
const showPasswordModal = ref(false)
const deletePassword = ref('')

// Toast component reference
const toastRef = ref(null)

// Validation helpers
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}


// Real-time validation
const validateField = (field, form = 'profile') => {
  const formData = form === 'profile' ? profileForm.value : passwordForm.value
  const value = formData[field]

  switch (field) {
    case 'username':
      if (!value.trim()) {
        validationErrors.value.username = 'Username is required'
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
        validationErrors.value.email = 'Email is required'
      } else if (!isValidEmail(value)) {
        validationErrors.value.email = 'Please enter a valid email address'
      } else {
        validationErrors.value.email = ''
      }
      break

    case 'currentPassword':
      if (!value) {
        validationErrors.value.currentPassword = 'Current password is required'
      } else {
        validationErrors.value.currentPassword = ''
      }
      break

    case 'newPassword':
      if (!value) {
        validationErrors.value.newPassword = ''
      } else if (value.length < 8) {
        validationErrors.value.newPassword = 'Password must be at least 8 characters long'
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])/.test(value)) {
        validationErrors.value.newPassword = 'Password must contain uppercase, lowercase, number and special character'
      } else {
        validationErrors.value.newPassword = ''
      }
      // Also validate confirm password when password changes
      validateField('confirmPassword', 'password')
      break

  }
}

// Watch for form changes (exclude currentPassword for submit-only validation)
import { watch } from 'vue'
watch(() => profileForm.value.username, () => validateField('username'))
watch(() => profileForm.value.email, () => validateField('email'))
watch(() => passwordForm.value.newPassword, () => validateField('newPassword'))

// Validate confirm password only when user types
const validateConfirmPassword = () => {
  const confirmValue = passwordForm.value.confirmPassword
  if (confirmValue && confirmValue !== passwordForm.value.newPassword) {
    validationErrors.value.confirmPassword = 'Passwords do not match'
  } else {
    validationErrors.value.confirmPassword = ''
  }
}

// Methods
const loadUserProfile = async () => {
  try {
    const response = await getUserProfile()
    if (response.code === 1) {
      const user = response.data
      profileForm.value = {
        username: user.username || '',
        email: user.email || '',
        bio: user.bio || '',
        avatar_url: user.avatar_url || ''
      }
      // Set current avatar URL for preview
      currentAvatarUrl.value = user.avatar_url ? `/avatars/${user.avatar_url}` : '/anonymous.png'
    }
  } catch (error) {
    console.error('Failed to load user profile:', error)
    toastRef.value?.addToast(error.response?.data || 'Failed to load profile information', 'error')
  }
}

const updateProfile = async () => {
  if (isUpdatingProfile.value) return

  // Check for validation errors
  const hasErrors = validationErrors.value.username || validationErrors.value.email

  if (hasErrors) {
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  try {
    isUpdatingProfile.value = true
    const response = await updateUserProfile(profileForm.value, selectedAvatarFile.value)
    if (response.code === 0) {
      console.log('Profile update failed:', response.msg)
    }
    toastRef.value?.addToast(response)

    if (response.code === 1) {
      // Only on success: reset avatar selection and reload page
    selectedAvatarFile.value = null
    window.location.reload()
    }
    // DON'T clear form on failure - keep user data
  } catch (error) {
    console.error('Failed to update profile:', error)
    toastRef.value?.addToast(error.response?.data || 'Failed to update profile. Please try again.', 'error')
  } finally {
    isUpdatingProfile.value = false
  }
}

const changePassword = async () => {
  if (isChangingPassword.value) return

  // Check current password only on submit
  if (!passwordForm.value.currentPassword.trim()) {
    validationErrors.value.currentPassword = 'Current password is required'
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  // Check for validation errors
  const hasErrors = validationErrors.value.newPassword ||
                   validationErrors.value.confirmPassword

  if (hasErrors) {
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  // Additional validation for confirm password
  if (passwordForm.value.confirmPassword && passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    validationErrors.value.confirmPassword = 'Passwords do not match'
    toastRef.value?.addToast('Please fix the errors in the form', 'error')
    return
  }

  try {
    isChangingPassword.value = true
    const response = await changePasswordApi({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })

    if (response.code === 1) {
      // Only clear form on success
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }

      // Reset validation errors
      validationErrors.value = {
        username: '',
        email: '',
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
    // DON'T clear form on failure

    if (response.code === 0) {
      console.log('Password change failed:', response.msg)
    }
    toastRef.value?.addToast(response)
  } catch (error) {
    console.error('Failed to change password:', error)
    toastRef.value?.addToast(error.response?.data || 'Failed to change password. Please check your current password.', 'error')
  } finally {
    isChangingPassword.value = false
  }
}

const confirmDeleteAccount = () => {
  // Show password modal first
  showPasswordModal.value = true
  deletePassword.value = ''
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  deletePassword.value = ''
}

const proceedWithDeletion = async () => {
  if (!deletePassword.value.trim()) {
    toastRef.value?.addToast('Password is required', 'warning')
    return
  }

  // Close password modal
  showPasswordModal.value = false

  try {
    const response = await deleteUserAccount({ password: deletePassword.value })

    // Check if the response indicates success
    if (response && response.code === 1) {
      toastRef.value?.addToast(response)

      // Only logout and redirect if deletion was successful
      setTimeout(() => {
        authStore.logout()
        router.push('/login')
      }, 2000)
    } else {
      // API returned success code but response indicates failure
      if (response && response.code === 0) {
        console.log('Account deletion failed:', response.msg)
      }
      toastRef.value?.addToast(response || 'Failed to delete account. Please try again.', 'error')
    }
  } catch (error) {
    console.error('Failed to delete account:', error)
    toastRef.value?.addToast(error.response?.data || 'Failed to delete account. Please try again.', 'error')
    // Do not logout or redirect on failure - user can try again
  }
}

// Avatar methods
const onAvatarSelected = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file type
  if (!file.type.startsWith('image/')) {
    toastRef.value?.addToast('Please select a valid image file', 'error')
    return
  }

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    toastRef.value?.addToast('Image size must be less than 5MB', 'error')
    return
  }

  selectedAvatarFile.value = file

  // Create preview URL
  const reader = new FileReader()
  reader.onload = (e) => {
    currentAvatarUrl.value = e.target.result
  }
  reader.readAsDataURL(file)
}

const onAvatarError = (e) => {
  e.target.src = '/anonymous.png'
}

const goBack = () => {
  router.push('/profile')
}

// Lifecycle
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  await loadUserProfile()
})
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
  padding: 2rem;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.settings-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}

.back-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #3552b0;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(53, 82, 176, 0.3);
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #2a4193;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(53, 82, 176, 0.4);
}

.back-icon {
  width: 24px;
  height: 24px;
  display: block;
}

/* Settings Sections */
.settings-section {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3552b0;
}

/* Forms */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
}

.form-input,
.form-textarea {
  padding: 0.75rem 1rem;
  border: 2px solid #333333;
  border-radius: 8px;
  background-color: #0a0a0a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #f5c518;
}

.form-input.input-error,
.form-textarea.input-error {
  border-color: #F5C518;
}

.form-input.input-error:focus,
.form-textarea.input-error:focus {
  border-color: #F5C518;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Avatar Upload Styles */
.avatar-upload-section {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
  background-color: #0a0a0a;
  border-radius: 8px;
  border: 2px solid #333333;
}

.current-avatar {
  flex-shrink: 0;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #3552b0;
  display: block;
}

.avatar-upload-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.upload-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  max-width: 120px;
  background-color: #3552b0;
  color: #ffffff;
}

.upload-btn:hover {
  background-color: #2a4193;
}

.avatar-hint {
  color: #888888;
  font-size: 0.8rem;
}

.avatar-hint small {
  color: #888888;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.submit-btn {
  padding: 0.75rem 2rem;
  background-color: #3552b0;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.submit-btn:disabled {
  background-color: #555555;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Account Actions */
.account-actions {
  padding: 1.5rem 0;
}

.danger-btn {
  padding: 0.75rem 2rem;
  background-color: #dc3545;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.danger-btn:hover {
  background-color: #c82333;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .settings-page {
    padding: 1rem;
  }

  .settings-container {
    margin: 0;
  }

  .settings-header {
    margin-bottom: 2rem;
  }

  .settings-title {
    font-size: 2rem;
  }

  .settings-section {
    padding: 1.5rem;
  }

  .avatar-upload-section {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .avatar-preview {
    width: 100px;
    height: 100px;
  }

  .avatar-upload-controls {
    align-items: center;
  }

  .upload-btn {
    max-width: none;
    width: 120px;
  }

  .form-actions {
    justify-content: center;
  }

  .submit-btn,
  .danger-btn {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .settings-title {
    font-size: 1.8rem;
  }

  .settings-section {
    padding: 1rem;
  }

  .section-title {
    font-size: 1.3rem;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.modal-title {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1rem;
}

.modal-text {
  color: #cccccc;
  text-align: center;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #333333;
  color: #cccccc;
}

.cancel-btn:hover {
  background-color: #444444;
  color: #ffffff;
}

/* Responsive */
@media (max-width: 480px) {
  .modal-content {
    padding: 1.5rem;
  }

  .modal-actions {
    flex-direction: column;
  }

  .cancel-btn,
  .danger-btn {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
}

/* Validation Styles */
.input-error-text {
  color: #F5C518;
  font-size: 0.85rem;
  margin-top: 0.25rem;
  font-weight: 500;
}

.password-hint {
  margin-top: 0.5rem;
}

.password-hint-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #F5C518;
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
</style>
