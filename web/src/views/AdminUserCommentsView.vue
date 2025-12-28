<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-title">Comments by {{ user?.username || 'User' }}</h1>
        <button class="back-btn" @click="goBack" aria-label="Back to Users">
          <img src="/arrow-left.svg" alt="Back" class="back-icon" />
        </button>
      </div>

      <!-- Comments Section -->
      <div class="admin-content">
        <div class="comments-container">
          <PostsListAdmin
            :comments="comments"
            :loading="isLoading"
            :has-more-posts="hasMoreComments"
            :loading-more="loadingMore"
            :empty-message="'No comments found for this user'"
            mode="comments"
            :user-id="userId"
            @load-more="loadMoreComments"
            @comment-deleted="onCommentDeleted"
          />
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
import { useRouter, useRoute } from 'vue-router'
import { getUserComments } from '@/api/admin.js'
import PostsListAdmin from '@/components/PostsListAdmin.vue'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Route params
const userId = route.params.userId
const user = ref(null)

// Data state
const comments = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMoreComments = ref(true)
const currentPage = ref(0)
const pageSize = 20

// Toast ref
const toastRef = ref(null)

// Load comments
const loadComments = async (reset = false) => {
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

    const response = await getUserComments(userId, params)

    if (response.code === 1 && response.data) {
      if (reset) {
        comments.value = response.data.comments || []
        user.value = response.data.user || null
      } else {
        comments.value.push(...(response.data.comments || []))
      }

      hasMoreComments.value = (response.data.comments || []).length === pageSize
      currentPage.value = response.data.page || 1
    } else {
      if (reset) {
        comments.value = []
      }
      hasMoreComments.value = false
    }
  } catch (error) {
    console.error('Failed to load comments:', error)
    toastRef.value?.addToast('Failed to load comments', 'error')
    if (reset) {
      comments.value = []
    }
    hasMoreComments.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMoreComments = () => {
  if (!hasMoreComments.value || loadingMore.value) return
  loadComments(false)
}

// Handle comment deleted event from PostsList component
const onCommentDeleted = (deletedComment) => {
  // Remove comment from list
  const index = comments.value.findIndex(c => c.comment_id === deletedComment.comment_id)
  if (index > -1) {
    comments.value.splice(index, 1)
  }
}

// Navigation
const goBack = () => {
  router.push('/admin/users')
}

// Utility functions are handled by PostsList component

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

  loadComments(true)
})

// Cleanup on unmount
onUnmounted(() => {
  // Cleanup if needed
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

.comments-container {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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

  .comments-container {
    padding: 1.5rem;
  }
}
</style>
