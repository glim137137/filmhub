<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-title">Logs by {{ userInfo?.username || 'User' }}</h1>
        <button class="back-btn" @click="goBack" aria-label="Back to Users">
          <img src="/arrow-left.svg" alt="Back" class="back-icon" />
        </button>
      </div>

      <!-- Logs Section -->
      <div class="admin-content">
        <div class="logs-container">
        <div v-if="isLoading" class="loading-placeholder">
          <span>Loading user logs...</span>
        </div>

        <div v-else-if="logs.length > 0" class="logs-list">
          <div
            v-for="log in logs"
            :key="log.id"
            class="log-item"
          >
            <div class="log-content">
              <div class="log-info">
                <span class="log-action">{{ log.action }}</span>
              </div>
              <div class="log-time">{{ formatDateTime(log.created_at) }}</div>
            </div>
          </div>
        </div>

        <div v-else class="no-data">
          <span>No logs found for this user</span>
        </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Component -->
  <Toast />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter, useRoute } from 'vue-router'
import { getUserLogs } from '@/api/admin.js'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Route params
const userId = route.params.userId

// Data
const userInfo = ref(null)
const logs = ref([])
const isLoading = ref(false)

// Load user logs
const loadUserLogs = async () => {
  try {
    isLoading.value = true

    // Load user info and logs
    const [userResponse, logsResponse] = await Promise.all([
      // For now, we'll just get the logs. User info could be added later if needed
      Promise.resolve({ username: 'User ' + userId }),
      getUserLogs(userId, { limit: 100 })
    ])

    userInfo.value = userResponse

    if (logsResponse.code === 1 && logsResponse.data) {
      logs.value = logsResponse.data.logs || []
    } else {
      logs.value = []
    }
  } catch (error) {
    console.error('Failed to load user logs:', error)
    logs.value = []
  } finally {
    isLoading.value = false
  }
}

// Utility functions
const formatDateTime = (dateString) => {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return 'Unknown'
  }
}

const goBack = () => {
  router.push('/admin/users')
}

// Check admin access on mount
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (authStore.username !== 'admin') {
    router.push('/')
    return
  }

  if (!userId) {
    router.push('/admin/users')
    return
  }

  await loadUserLogs()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
  padding: 2rem;
}

.admin-container {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.admin-title {
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

.admin-content {
  display: flex;
  flex-direction: column;
}

.logs-container {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 3rem;
}

.log-item {
  background-color: #1a1a1a;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #333333;
  transition: background-color 0.3s ease;
}

.log-item:hover {
  background-color: #232323;
}

.log-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.log-action {
  color: #cccccc;
  font-size: 0.9rem;
  line-height: 1.4;
}

.log-time {
  color: #888888;
  font-size: 0.8rem;
  white-space: nowrap;
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

/* Responsive Design */
@media (max-width: 768px) {
  .admin-page {
    padding: 1rem;
  }

  .admin-header {
    margin-bottom: 2rem;
  }

  .admin-title {
    font-size: 2rem;
  }

  .logs-container {
    padding: 1.5rem;
  }

  .log-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .log-time {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .admin-title {
    font-size: 1.8rem;
  }
}
</style>
