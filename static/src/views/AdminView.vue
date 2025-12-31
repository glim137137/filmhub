<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-title">Admin Panel</h1>
      </div>

      <div class="admin-content">
        <div class="welcome-section">
          <h2>Admin Dashboard</h2>
          <p>Monitor users, posts, comments, and films from here.</p>
        </div>

        <!-- Admin Statistics -->
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Total Users</h3>
            <div class="stat-number">{{ isLoadingStats ? '...' : stats.total_users }}</div>
          </div>
          <div class="stat-card">
            <h3>Total Posts</h3>
            <div class="stat-number">{{ isLoadingStats ? '...' : stats.total_posts }}</div>
          </div>
          <div class="stat-card">
            <h3>Total Comments</h3>
            <div class="stat-number">{{ isLoadingStats ? '...' : stats.total_comments }}</div>
          </div>
          <div class="stat-card">
            <h3>Total Films</h3>
            <div class="stat-number">{{ isLoadingStats ? '...' : stats.total_films }}</div>
          </div>
        </div>

        <!-- Logs Statistics -->
        <div class="logs-stats-section">
          <h2>Access Statistics</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <h3>Today's Access</h3>
              <div class="stat-number">{{ isLoadingLogsStats ? '...' : logsStats.today }}</div>
            </div>
            <div class="stat-card">
              <h3>This Week</h3>
              <div class="stat-number">{{ isLoadingLogsStats ? '...' : logsStats.week }}</div>
            </div>
            <div class="stat-card">
              <h3>This Month</h3>
              <div class="stat-number">{{ isLoadingLogsStats ? '...' : logsStats.month }}</div>
            </div>
            <div class="stat-card">
              <h3>This Year</h3>
              <div class="stat-number">{{ isLoadingLogsStats ? '...' : logsStats.year }}</div>
            </div>
          </div>
        </div>

        <!-- Top Active Users -->
        <div class="active-users-section">
          <h2>Top Active Users</h2>
          <div v-if="isLoadingActiveUsers" class="loading-placeholder">
            <span>Loading active users...</span>
          </div>
          <div v-else-if="topActiveUsers.length > 0" class="active-users-list">
            <div
              v-for="(user, index) in topActiveUsers"
              :key="user.user_id"
              class="active-user-item"
            >
              <div class="user-rank">#{{ index + 1 }}</div>
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-activity">{{ user.log_count }} activities</div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <span>No activity data available</span>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="statsError" class="error-message">
          <p>{{ statsError }}</p>
          <button class="retry-btn" @click="loadAdminStats" :disabled="isLoadingStats">
            {{ isLoadingStats ? 'Loading...' : 'Retry' }}
          </button>
        </div>

      </div>
    </div>
  </div>

  <!-- Toast Component -->
  <Toast />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { getAdminStats, getLogsStats, getTopActiveUsers } from '@/api/admin.js'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()

// Admin stats
const stats = ref({
  total_users: 0,
  total_posts: 0,
  total_comments: 0,
  total_films: 0
})
const isLoadingStats = ref(false)
const statsError = ref('')

// Logs stats
const logsStats = ref({
  today: 0,
  week: 0,
  month: 0,
  year: 0
})
const isLoadingLogsStats = ref(false)
const logsStatsError = ref('')

// Top active users
const topActiveUsers = ref([])
const isLoadingActiveUsers = ref(false)
const activeUsersError = ref('')

// Load admin statistics
const loadAdminStats = async () => {
  try {
    isLoadingStats.value = true
    statsError.value = ''
    const response = await getAdminStats()
    if (response.code === 1 && response.data) {
      stats.value = {
        total_users: response.data.total_users || 0,
        total_posts: response.data.total_posts || 0,
        total_comments: response.data.total_comments || 0,
        total_films: response.data.total_films || 0
      }
    } else {
      statsError.value = 'Failed to load statistics'
    }
  } catch (error) {
    console.error('Failed to load admin stats:', error)
    statsError.value = 'Failed to load statistics'
    // Keep default values (0) on error
  } finally {
    isLoadingStats.value = false
  }
}

// Load logs statistics
const loadLogsStats = async () => {
  try {
    isLoadingLogsStats.value = true
    logsStatsError.value = ''
    const response = await getLogsStats()
    if (response.code === 1 && response.data) {
      logsStats.value = {
        today: response.data.today || 0,
        week: response.data.week || 0,
        month: response.data.month || 0,
        year: response.data.year || 0
      }
    } else {
      logsStatsError.value = 'Failed to load logs statistics'
    }
  } catch (error) {
    console.error('Failed to load logs stats:', error)
    logsStatsError.value = 'Failed to load logs statistics'
    // Keep default values (0) on error
  } finally {
    isLoadingLogsStats.value = false
  }
}

// Load top active users
const loadTopActiveUsers = async () => {
  try {
    isLoadingActiveUsers.value = true
    activeUsersError.value = ''
    const response = await getTopActiveUsers({ limit: 10 })
    if (response.code === 1 && response.data) {
      topActiveUsers.value = response.data.top_users || []
    } else {
      activeUsersError.value = 'Failed to load active users'
      topActiveUsers.value = []
    }
  } catch (error) {
    console.error('Failed to load top active users:', error)
    activeUsersError.value = 'Failed to load active users'
    topActiveUsers.value = []
  } finally {
    isLoadingActiveUsers.value = false
  }
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

  // Load admin statistics
  await loadAdminStats()

  // Load logs statistics
  await loadLogsStats()

  // Load top active users
  await loadTopActiveUsers()
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
  justify-content: center;
  align-items: center;
  margin-bottom: 3rem;
}

.admin-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}


.admin-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-section {
  text-align: center;
  padding: 2rem;
  background-color: #1a1a1a;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.welcome-section h2 {
  font-size: 2rem;
  color: #ffffff;
  margin-bottom: 1rem;
}

.welcome-section p {
  color: #cccccc;
  font-size: 1.1rem;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid #333333;
}

.stat-card h3 {
  color: #cccccc;
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #5799EF;
}

.error-message {
  background-color: #dc3545;
  color: #ffffff;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 1rem;
}

.error-message p {
  margin: 0 0 1rem 0;
  font-weight: 500;
}

.retry-btn {
  background-color: #ffffff;
  color: #dc3545;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover:not(:disabled) {
  background-color: #f8f9fa;
}

.retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.logs-stats-section h2 {
    padding-bottom: 20px;
}

.active-users-section h2 {
    padding-bottom: 20px;
}

.active-users-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.active-user-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: #1a1a1a;
    border-radius: 8px;
    border: 1px solid #333333;
    transition: background-color 0.3s ease;
}

.active-user-item:hover {
    background-color: #232323;
}

.user-rank {
    font-size: 1.2rem;
    font-weight: bold;
    color: #f5c518;
    min-width: 50px;
    text-align: center;
}

.user-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.user-name {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
}

.user-activity {
    font-size: 0.85rem;
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

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .welcome-section {
    padding: 1.5rem;
  }

  .welcome-section h2 {
    font-size: 1.5rem;
  }

  .active-user-item {
    padding: 0.75rem;
    gap: 0.75rem;
  }

  .user-rank {
    font-size: 1.1rem;
    min-width: 40px;
  }

  .user-name {
    font-size: 0.95rem;
  }

  .user-activity {
    font-size: 0.8rem;
  }

}
</style>
