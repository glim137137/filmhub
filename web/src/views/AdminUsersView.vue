<template>
  <div class="admin-page">
    <!-- Search Section -->
    <section class="search-section">
      <div class="search-content">
        <div class="search-box" @click.stop>
          <label for="user-search" class="sr-only">Search for users</label>
          <input
            id="user-search"
            type="text"
            class="search-input"
            placeholder="Search users by username..."
            v-model="searchQuery"
            @input="handleSearchInput"
            @keydown.enter="handleSearch"
          />
          <button class="search-button" @click="handleSearch">Search</button>
        </div>
      </div>
    </section>

    <!-- Users Section -->
    <section class="users-section">
      <div class="container">
        <div v-if="isLoading" class="loading-placeholder">
          <span>Loading users...</span>
        </div>
        <div v-else-if="users.length > 0" class="users-grid">
          <div class="user-card" v-for="user in users" :key="user.id">
            <div class="user-avatar">
              <img
                :src="user.avatar_url ? `/avatars/${user.avatar_url}` : '/anonymous.png'"
                :alt="user.username"
                class="avatar-img"
                @error="onAvatarError"
              />
            </div>
            <div class="user-info">
              <h3 class="user-name">{{ user.username }}</h3>
              <p class="user-email">{{ user.email }}</p>
              <div class="user-meta">
                <span class="user-date">Joined {{ formatDate(user.created_at) }}</span>
              </div>
            </div>
            <div class="user-actions">
              <button class="action-btn view-posts" @click="viewUserPosts(user)">
                <span>Posts</span>
              </button>
              <button class="action-btn view-comments" @click="viewUserComments(user)">
                <span>Comments</span>
              </button>
              <button class="action-btn view-logs" @click="viewUserLogs(user)">
                <span>Logs</span>
              </button>
              <button
                class="action-btn delete-user"
                @click="confirmDeleteUser(user)"
                :disabled="user.username === 'admin'"
              >
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <span>No users found</span>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreUsers && users.length > 0" class="load-more-container">
          <button
            class="load-more-btn"
            @click="loadMoreUsers"
            :disabled="loadingMore"
            :class="{ loading: loadingMore }"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Users' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Confirm User Deletion</h3>
        <p class="modal-text">
          Are you sure you want to delete user "{{ selectedUser?.username }}"?
          This action cannot be undone and will also delete all their posts and comments.
        </p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeDeleteModal">Cancel</button>
          <button
            class="danger-btn"
            @click="proceedWithDeletion"
            :disabled="isDeleting"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete User' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { getAdminUsers, deleteUserByAdmin } from '@/api/admin.js'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()

// Search state
const searchQuery = ref('')
let searchTimeout = null

// Data state
const users = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMoreUsers = ref(true)
const currentPage = ref(0)
const pageSize = 20

// Delete modal
const showDeleteModal = ref(false)
const selectedUser = ref(null)
const isDeleting = ref(false)

// Toast ref
const toastRef = ref(null)

// Search functionality
const handleSearchInput = () => {
  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  // Reset pagination when searching
  currentPage.value = 0
  hasMoreUsers.value = true

  // Debounce search
  searchTimeout = setTimeout(() => {
    loadUsers(true)
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 0
  hasMoreUsers.value = true
  loadUsers(true)
}

// Load users
const loadUsers = async (reset = false) => {
  try {
    if (reset) {
      isLoading.value = true
      currentPage.value = 0
    } else {
      loadingMore.value = true
    }

    const params = {
      page: currentPage.value + 1,
      per_page: pageSize
    }

    if (searchQuery.value.trim()) {
      params.username = searchQuery.value.trim()
    }

    const response = await getAdminUsers(params)

    if (response.code === 1 && response.data) {
      if (reset) {
        users.value = response.data.users || []
      } else {
        users.value.push(...(response.data.users || []))
      }

      hasMoreUsers.value = (response.data.users || []).length === pageSize
      currentPage.value = response.data.page || 1
    } else {
      if (reset) {
        users.value = []
      }
      hasMoreUsers.value = false
    }
  } catch (error) {
    console.error('Failed to load users:', error)
    if (reset) {
      users.value = []
    }
    hasMoreUsers.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMoreUsers = () => {
  if (!hasMoreUsers.value || loadingMore.value) return
  loadUsers(false)
}

// User actions
const viewUserPosts = (user) => {
  router.push(`/admin/users/${user.id}/posts`)
}

const viewUserComments = (user) => {
  router.push(`/admin/users/${user.id}/comments`)
}

const viewUserLogs = (user) => {
  router.push(`/admin/users/${user.id}/logs`)
}

const confirmDeleteUser = (user) => {
  selectedUser.value = user
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  selectedUser.value = null
}

const proceedWithDeletion = async () => {
  if (!selectedUser.value || isDeleting.value) return

  try {
    isDeleting.value = true
    await deleteUserByAdmin(selectedUser.value.id)

    // Remove user from list
    const index = users.value.findIndex(u => u.id === selectedUser.value.id)
    if (index > -1) {
      users.value.splice(index, 1)
    }

    // Show success message
    toastRef.value?.addToast(`User "${selectedUser.value.username}" has been successfully deleted`, 'success')

    closeDeleteModal()
  } catch (error) {
    console.error('Failed to delete user:', error)
    // Show error message
    toastRef.value?.addToast('Failed to delete user. Please try again.', 'error')
  } finally {
    isDeleting.value = false
  }
}

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return 'Unknown'
  }
}

const onAvatarError = (e) => {
  e.target.src = '/anonymous.png'
}

// Check admin access on mount
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (authStore.username !== 'admin') {
    router.push('/')
    return
  }

  loadUsers(true)
})

// Cleanup on unmount
onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
/* Search Section - Copied from FilmsView.vue */
.search-section {
  background-color: #000000;
  padding: 2rem 2rem 1rem 2rem;
}

.search-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.search-box {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #333333;
  border-radius: 25px;
  background-color: #1a1a1a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  max-width: 400px;
}

.search-input:focus {
  border-color: #f5c518;
}

.search-button {
  padding: 0.75rem 2rem;
  background-color: #3552b0;
  color: #ffffff;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #1d4ed8;
}

/* Users Section */
.users-section {
  padding: 3rem 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.user-card {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid #333333;
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0 0 0.25rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  color: #cccccc;
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-meta {
  display: flex;
  align-items: center;
}

.user-date {
  color: #888888;
  font-size: 0.8rem;
}

.user-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.action-btn span {
  color: #ffffff;
}

.view-posts,
.view-comments,
.view-logs,
.delete-user {
  background-color: #3552b0;
}

.view-posts:hover,
.view-comments:hover,
.view-logs:hover,
.delete-user:hover:not(:disabled) {
  background-color: #2a4193;
}

.delete-user:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* Load More Button */
.load-more-container {
  text-align: center;
  margin-top: 2rem;
  padding-bottom: 2rem;
}

.load-more-btn {
  background: #3552b0;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease, opacity 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: #2a4193;
}

.load-more-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.load-more-btn.loading {
  background: #555;
}

/* Loading and Empty States */
.loading-placeholder, .no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem 2rem;
  color: #666666;
  font-size: 1.2rem;
  text-align: center;
}

.loading-placeholder {
  color: #f5c518;
}

.no-data {
  color: #cccccc;
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

.cancel-btn, .danger-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.cancel-btn {
  background-color: #333333;
  color: #cccccc;
}

.cancel-btn:hover {
  background-color: #444444;
  color: #ffffff;
}

.danger-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.danger-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.danger-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

/* Utility Classes */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .search-section {
    padding: 1.5rem 1rem 0.75rem 1rem;
  }

  .users-section {
    padding: 1.5rem 1rem;
  }

  .search-box {
    flex-direction: column;
  }

  .search-input {
    max-width: none;
    border-radius: 8px;
  }

  .search-button {
    border-radius: 8px;
  }

  .users-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .user-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .user-actions {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }

  .action-btn {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .search-section {
    padding: 1rem 0.5rem 0.5rem 0.5rem;
  }

  .users-section {
    padding: 1rem 0.5rem;
  }

  .loading-placeholder, .no-data {
    padding: 2rem 1rem;
    font-size: 1rem;
  }

  .modal-content {
    padding: 1.5rem;
  }
}
</style>
