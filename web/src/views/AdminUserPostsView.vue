<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-title">Posts by {{ user?.username || 'User' }}</h1>
        <button class="back-btn" @click="goBack" aria-label="Back to Users">
          <img src="/arrow-left.svg" alt="Back" class="back-icon" />
        </button>
      </div>

      <!-- Posts Section -->
      <div class="admin-content">
        <div class="posts-container">
          <PostsListAdmin
            :posts="posts"
            :loading="isLoading"
            :has-more-posts="hasMorePosts"
            :loading-more="loadingMore"
            :empty-message="'No posts found for this user'"
            mode="posts"
            :user-id="userId"
            @load-more="loadMorePosts"
            @post-deleted="onPostDeleted"
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
import { getUserPosts } from '@/api/admin.js'
import PostsListAdmin from '@/components/PostsListAdmin.vue'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Route params
const userId = route.params.userId
const user = ref(null)

// Data state
const posts = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMorePosts = ref(true)
const currentPage = ref(0)
const pageSize = 20

// Toast ref
const toastRef = ref(null)

// Load posts
const loadPosts = async (reset = false) => {
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

    const response = await getUserPosts(userId, params)

    if (response.code === 1 && response.data) {
      if (reset) {
        posts.value = response.data.posts || []
        user.value = response.data.user || null
      } else {
        posts.value.push(...(response.data.posts || []))
      }

      hasMorePosts.value = (response.data.posts || []).length === pageSize
      currentPage.value = response.data.page || 1
    } else {
      if (reset) {
        posts.value = []
      }
      hasMorePosts.value = false
    }
  } catch (error) {
    console.error('Failed to load posts:', error)
    toastRef.value?.addToast('Failed to load posts', 'error')
    if (reset) {
      posts.value = []
    }
    hasMorePosts.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMorePosts = () => {
  if (!hasMorePosts.value || loadingMore.value) return
  loadPosts(false)
}

// Handle post deleted event from PostsList component
const onPostDeleted = (deletedPost) => {
  // Remove post from list
  const index = posts.value.findIndex(p => p.post_id === deletedPost.post_id)
  if (index > -1) {
    posts.value.splice(index, 1)
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

  loadPosts(true)
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

.posts-container {
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

  .posts-container {
    padding: 1.5rem;
  }
}
</style>