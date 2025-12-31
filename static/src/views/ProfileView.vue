<template>
  <div class="profile-page">
    <!-- Profile Header Section -->
    <section class="profile-header">
      <div class="profile-content">
        <div class="profile-info">
          <div class="avatar-section">
            <img
              :src="user.avatar_url ? `/avatars/${user.avatar_url}` : '/anonymous.png'"
              :alt="user.username"
              class="profile-avatar"
              @error="onAvatarError"
            />
          </div>
          <div class="user-details">
            <h1 class="username">{{ user.username || 'Anonymous' }}</h1>
            <p class="user-email">{{ user.email || '' }}</p>
            <p class="user-bio" v-if="user.bio">{{ user.bio }}</p>
            <p class="user-bio empty" v-else>No bio yet</p>
          </div>
        </div>
        <button class="settings-btn" @click="goToSettings" aria-label="Settings (Alt+S)" title="Settings (Alt+S)">
          <img src="/settings.svg" alt="Settings" class="settings-icon" />
          <span class="shortcut-hint">(Alt+S)</span>
        </button>
      </div>
    </section>

    <!-- Watchlist Section -->
    <section class="watchlist-section">
      <div class="section-container">
        <h2 class="section-title">Watchlist</h2>
        <div v-if="isLoading.watchlist" class="loading-placeholder">
          <span>Loading watchlist...</span>
        </div>
        <div v-else-if="watchlist.length > 0" class="movies-grid">
          <MovieCard
            v-for="movie in watchlist"
            :key="movie.id"
            :movie="movie"
            :mode="'delete'"
            @title-click="viewMovie"
            @star-click="onStarClick"
            @watchlist-removed="onWatchlistRemoved"
          />
        </div>
        <div v-else class="no-data">
          <span>Your watchlist is empty</span>
        </div>
      </div>
    </section>

    <!-- My Posts Section -->
    <section class="posts-section">
      <div class="section-container">
        <h2 class="section-title">My Posts</h2>
        <PostsListUser
          :posts="userPosts"
          :loading="isLoading.posts"
          :has-more-posts="hasMorePosts"
          :loading-more="loadingMore"
          :empty-message="'You haven\'t posted anything yet'"
          mode="posts"
          :user-id="currentUserId"
          @load-more="loadMorePosts"
          @post-updated="onPostUpdated"
          @post-deleted="onPostDeleted"
        />
      </div>
    </section>

    <!-- My Comments Section -->
    <section class="comments-section">
      <div class="section-container">
        <h2 class="section-title">My Comments</h2>
        <PostsListUser
          :comments="userComments"
          :loading="isLoading.comments"
          :has-more-posts="hasMoreComments"
          :loading-more="loadingMoreComments"
          :empty-message="'You haven\'t commented on anything yet'"
          mode="comments"
          :user-id="currentUserId"
          @comment-deleted="onCommentDeleted"
        />
      </div>
    </section>

    <!-- My Tags Section -->
    <section class="tags-section">
      <div class="section-container">
        <h2 class="section-title">My Tags</h2>

        <!-- Tags Grid -->
        <div v-if="userTags.length > 0" class="tags-grid">
          <div
            v-for="tag in userTags"
            :key="tag.id"
            class="tag-item"
            :class="{ 'editing': isEditingTags }"
          >
            <span class="tag-name">#{{ tag.name }}</span>
            <button
              v-if="isEditingTags"
              class="remove-tag-btn"
              @click="removeTag(tag)"
              aria-label="Remove tag"
            >
              ×
            </button>
          </div>
        </div>
        <div v-else class="no-tags">
          <span>No tags yet</span>
        </div>

        <!-- Tag Input Section -->
        <div class="tag-input-section">
          <div class="tag-input-container">
            <input
              v-model="newTagInput"
              type="text"
              class="tag-input"
              placeholder="Add a new tag..."
              aria-label="Add a new tag"
              @input="handleTagInput"
              :disabled="!isEditingTags"
            />
            <div v-if="isEditingTags" class="tag-buttons">
              <button
                class="tag-action-btn add-btn"
                @click="addTag()"
                :disabled="!newTagInput.trim()"
                title="Add tag"
              >
                <img src="/plus.svg" alt="Add" class="btn-icon" />
              </button>
              <button
                class="tag-action-btn save-btn"
                @click="saveTags()"
                title="Save changes"
              >
                <img src="/save.svg" alt="Save" class="btn-icon" />
              </button>
            </div>
            <button
              v-else
              class="tag-action-btn edit-btn"
              @click="toggleEditMode()"
              title="Edit tags"
            >
              Edit
            </button>
          </div>

          <!-- Tag Suggestions -->
          <div v-if="showTagSuggestions && tagSuggestions.length > 0" class="tag-suggestions">
            <div
              v-for="suggestion in tagSuggestions"
              :key="suggestion.name"
              class="tag-suggestion-item"
              @click="addSuggestedTag(suggestion.name)"
            >
              #{{ suggestion.name }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import PostsListUser from '@/components/PostsListUser.vue'
import Toast from '@/components/Toast.vue'
import { getUserProfile, getUserWatchlist, removeFavorite, getUserTags, addUserTag, removeUserTag, searchTags, getUserPosts, getUserComments } from '@/api/user.js'

const authStore = useAuthStore()
const router = useRouter()

// Data
const user = ref({})
const watchlist = ref([])
const userPosts = ref([])
const userComments = ref([])
const userTags = ref([])
const originalTags = ref([]) // Store original tags for comparison
const tagSuggestions = ref([])
const isLoading = ref({
  profile: false,
  watchlist: false,
  posts: false,
  comments: false,
  tags: false
})
const hasMorePosts = ref(true)
const hasMoreComments = ref(true)
const loadingMore = ref(false)
const loadingMoreComments = ref(false)
const isEditingTags = ref(false)
const newTagInput = ref('')
const showTagSuggestions = ref(false)
let tagSearchTimeout = null

// Toast component reference
const toastRef = ref(null)

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId = computed(() => {
  return authStore.userId?.value || authStore.user?.id || null
})

// Keyboard shortcuts handler
const handleKeydown = (event) => {
  // Alt + S for settings
  if (event.altKey && event.key.toLowerCase() === 's') {
    event.preventDefault()
    goToSettings()
  }
}

// Methods
const loadUserProfile = async () => {
  try {
    isLoading.value.profile = true
    const response = await getUserProfile()
    if (response.code === 1) {
      user.value = response.data
    }
  } catch (error) {
    console.error('Failed to load user profile:', error)
  } finally {
    isLoading.value.profile = false
  }
}

const loadUserWatchlist = async () => {
  try {
    isLoading.value.watchlist = true
    const response = await getUserWatchlist()
    if (response.code === 1) {
      watchlist.value = response.data?.films || []
    }
  } catch (error) {
    console.error('Failed to load watchlist:', error)
  } finally {
    isLoading.value.watchlist = false
  }
}

const loadUserPosts = async (loadMore = false) => {
  try {
    if (!loadMore) {
      isLoading.value.posts = true
    } else {
      loadingMore.value = true
    }

    const currentLength = userPosts.value.length
    const response = await getUserPosts(currentLength, 20) // Load 20 posts at a time

    if (response.code === 1) {
      const posts = response.data?.posts || []
      if (loadMore) {
        userPosts.value = [...userPosts.value, ...posts]
      } else {
        userPosts.value = posts
      }

      // Check if there are more posts
      hasMorePosts.value = posts.length === 20
    }
  } catch (error) {
    console.error('Failed to load user posts:', error)
  } finally {
    isLoading.value.posts = false
    loadingMore.value = false
  }
}

const loadUserComments = async (loadMore = false) => {
  try {
    if (!loadMore) {
      isLoading.value.comments = true
    } else {
      loadingMoreComments.value = true
    }

    const currentLength = userComments.value.length
    const response = await getUserComments(currentLength, 20) // Load 20 comments at a time

    if (response.code === 1) {
      const comments = response.data?.comments || []
      if (loadMore) {
        userComments.value = [...userComments.value, ...comments]
      } else {
        userComments.value = comments
      }

      // Check if there are more comments
      hasMoreComments.value = comments.length === 20
    }
  } catch (error) {
    console.error('Failed to load user comments:', error)
  } finally {
    isLoading.value.comments = false
    loadingMoreComments.value = false
  }
}

const loadUserTags = async () => {
  try {
    isLoading.value.tags = true
    const response = await getUserTags()
    if (response.code === 1) {
      const tags = response.data || []
      userTags.value = [...tags] // Create a copy
      originalTags.value = [...tags] // Store original tags
    }
  } catch (error) {
    console.error('Failed to load user tags:', error)
  } finally {
    isLoading.value.tags = false
  }
}


const toggleEditMode = () => {
  isEditingTags.value = !isEditingTags.value
  if (isEditingTags.value) {
    // Entering edit mode - reset to original state
    userTags.value = [...originalTags.value]
  } else {
    // Exiting edit mode without saving - reset to original state
    userTags.value = [...originalTags.value]
    newTagInput.value = ''
    showTagSuggestions.value = false
  }
}

const saveTags = async () => {
  try {
    // Find tags to add (new tags that weren't in original list)
    const tagsToAdd = userTags.value.filter(tag =>
      !originalTags.value.some(originalTag => originalTag.id === tag.id)
    )

    // Find tags to remove (original tags that are no longer in the list)
    const tagsToRemove = originalTags.value.filter(originalTag =>
      !userTags.value.some(tag => tag.id === originalTag.id)
    )

    // Add new tags
    for (const tag of tagsToAdd) {
      await addUserTag({ name: tag.name })
    }

    // Remove deleted tags
    for (const tag of tagsToRemove) {
      await removeUserTag(tag.id)
    }

    // Update original tags to current state
    originalTags.value = [...userTags.value]

    // Exit edit mode
    isEditingTags.value = false
    newTagInput.value = ''
    showTagSuggestions.value = false

    toastRef.value?.addToast('Tags saved successfully!', 'success')
  } catch (error) {
    console.error('Failed to save tags:', error)
    toastRef.value?.addToast('Failed to save tags. Please try again.', 'error')
  }
}

const handleTagInput = async () => {
  if (!isEditingTags.value) return

  const query = newTagInput.value.trim()

  // Clear previous timeout
  if (tagSearchTimeout) {
    clearTimeout(tagSearchTimeout)
  }

  if (!query) {
    tagSuggestions.value = []
    showTagSuggestions.value = false
    return
  }

  // Debounce search
  tagSearchTimeout = setTimeout(async () => {
    try {
      const response = await searchTags(query)
      if (response.code === 1) {
        tagSuggestions.value = (response.data || []).slice(0, 5)
        showTagSuggestions.value = tagSuggestions.value.length > 0
      }
    } catch (error) {
      console.error('Failed to search tags:', error)
      tagSuggestions.value = []
      showTagSuggestions.value = false
    }
  }, 300)
}

const addTag = () => {
  const tagName = newTagInput.value.trim()
  if (!tagName) return

  // Check if tag already exists
  if (userTags.value.some(tag => tag.name === tagName)) {
    toastRef.value?.addToast('Tag already exists', 'warning')
    return
  }

  // Add tag locally
  userTags.value.push({
    id: Date.now(), // Temporary ID for local tags
    name: tagName
  })

  newTagInput.value = ''
  showTagSuggestions.value = false
}

const addSuggestedTag = (tagName) => {
  // Check if tag already exists
  if (userTags.value.some(tag => tag.name === tagName)) {
    toastRef.value?.addToast('Tag already exists', 'warning')
    return
  }

  // Add tag locally
  userTags.value.push({
    id: Date.now(), // Temporary ID for local tags
    name: tagName
  })

  newTagInput.value = ''
  showTagSuggestions.value = false
}

const removeTag = (tag) => {
  // Remove tag locally
  userTags.value = userTags.value.filter(t => t.id !== tag.id)
}

const getPosterUrl = (posterUrl) => {
  if (!posterUrl) return '/film.jpg'
  return `/posters/${posterUrl}`
}

const onImageError = (e) => {
  try {
    e.target.src = '/film.jpg'
  } catch (err) {
    // ignore
  }
}

const onAvatarError = (e) => {
  try {
    e.target.src = '/anonymous.png'
  } catch (err) {
    // ignore
  }
}

const goToSettings = () => {
  router.push('/settings')
}

const viewMovie = (movieId) => {
  router.push(`/films/${movieId}`)
}

const onStarClick = (movie) => {
  console.log(`Star clicked for movie: ${movie.title}`)
  // Handle star click - could be for favorites or ratings
}

const onWatchlistRemoved = (movie) => {
  // Remove from local watchlist when MovieCard emits watchlist-removed
  watchlist.value = watchlist.value.filter(m => m.id !== movie.id)
  console.log(`Movie removed from watchlist: ${movie.title}`)
}

const loadMorePosts = () => {
  loadUserPosts(true)
}

const onPostUpdated = (post) => {
  // Update post in the list
  const index = userPosts.value.findIndex(p => p.post_id === post.post_id)
  if (index !== -1) {
    userPosts.value[index] = post
  }
}

const onPostDeleted = (post) => {
  // Remove post from the list
  userPosts.value = userPosts.value.filter(p => p.post_id !== post.post_id)
}

const onCommentDeleted = (comment) => {
  // Remove comment from the list
  userComments.value = userComments.value.filter(c => c.comment_id !== comment.comment_id)
}

// Lifecycle
onMounted(async () => {
  // Add keyboard shortcuts
  window.addEventListener('keydown', handleKeydown)

  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  await Promise.all([
    loadUserProfile(),
    loadUserWatchlist(),
    loadUserPosts(),
    loadUserComments(),
    loadUserTags()
  ])
})

onUnmounted(() => {
  // Remove keyboard shortcuts
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
}

/* Profile Header */
.profile-header {
  padding: 3rem 2rem;
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
}

.profile-info {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.avatar-section {
  flex-shrink: 0;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.user-email {
  font-size: 1.1rem;
  color: #cccccc;
  margin-bottom: 0.5rem;
}

.user-bio {
  font-size: 1rem;
  color: #cccccc;
  line-height: 1.5;
  max-width: 600px;
}

.user-bio.empty {
  color: #cccccc;
  font-style: italic;
}

.settings-btn {
  position: absolute;
  top: 0;
  right: 0;
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

.settings-btn:hover {
  background: #2a4193;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(53, 82, 176, 0.4);
}

.settings-icon {
  width: 24px;
  height: 24px;
  display: block;
}

.shortcut-hint {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.6rem;
  color: #cccccc;
  opacity: 0.8;
  font-weight: normal;
  white-space: nowrap;
  background-color: rgba(0, 0, 0, 0.8);
  padding: 2px 4px;
  border-radius: 3px;
  pointer-events: none;
}

/* Sections */
.watchlist-section,
.posts-section,
.comments-section,
.tags-section {
  padding: 3rem 2rem;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 2rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 2rem;
  position: relative;
  padding-left: 20px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background-color: #f5c518;
  border-radius: 3px;
}

/* Watchlist */
.movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
}

.movie-card-watchlist {
  background-color: #121212;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.movie-card-watchlist:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.poster-container {
  height: 280px;
  background-color: #1a1a1a;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card-watchlist:hover .movie-poster {
  transform: scale(1.05);
}

.movie-info {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  justify-content: space-between;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.star-icon {
  width: 16px;
  height: 16px;
}

.rating-text {
  color: #f5c518;
  font-weight: bold;
  font-size: 0.9rem;
}

.delete-btn {
  background-color: transparent;
  color: #3552b0;
  border: none;
  padding: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.delete-btn:hover:not(:disabled) {
  background-color: #1a1a1a;
  border-radius: 4px;
}

.delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Tags */
.tags-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tag-item {
  background-color: #3552b0;
  color: #ffffff;
  padding: 0.75rem 1rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  min-width: fit-content;
  max-width: none;
  flex-shrink: 0;
}

.tag-item.editing {
  background-color: #3552b0;
}

.tag-name {
  flex: 1;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: #ffffff;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.5rem;
  line-height: 1;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.remove-tag-btn:hover {
  opacity: 1;
}

.no-tags {
  text-align: center;
  color: #cccccc;
  padding: 2rem;
  font-style: italic;
}

/* Tag Input */
.tag-input-section {
  margin-top: 2rem;
}

.tag-input-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.tag-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #333333;
  border-radius: 25px;
  background-color: #1a1a1a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.tag-input:focus {
  border-color: #f5c518;
}

.tag-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tag-action-btn {
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

.tag-action-btn:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.tag-action-btn:disabled {
  background-color: #555555;
  cursor: not-allowed;
  opacity: 0.6;
}

.tag-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.tag-action-btn.add-btn,
.tag-action-btn.save-btn {
  padding: 0.5rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-action-btn.add-btn {
  background-color: #3552b0;
}

.tag-action-btn.add-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.tag-action-btn.save-btn {
  background-color: #3552b0;
}

.tag-action-btn.save-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.btn-icon {
  width: 20px;
  height: 20px;
  display: block;
}

/* Tag Suggestions */
.tag-suggestions {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-suggestion-item {
  background-color: #1a1a1a;
  color: #cccccc;
  padding: 0.5rem 0.75rem;
  border-radius: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  white-space: nowrap;
  min-width: fit-content;
  max-width: none;
  flex-shrink: 0;
}

.tag-suggestion-item:hover {
  background-color: #2a2a2a;
  color: #ffffff;
}

/* Loading and empty states */
.loading-placeholder, .no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  color: #cccccc;
  font-size: 1.1rem;
}

.loading-placeholder {
  color: #f5c518;
}

.no-data {
  color: #cccccc;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .movies-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 992px) {
  .movies-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .profile-info {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }

  .profile-content {
    flex-direction: column;
    gap: 2rem;
  }

  .username {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .profile-header,
  .watchlist-section,
  .posts-section,
  .comments-section,
  .tags-section {
    padding: 2rem 1rem;
  }

  .movies-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .tags-grid {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .tag-item {
    font-size: 0.8rem;
    padding: 0.5rem 0.75rem;
  }

  .tag-input-container {
    flex-direction: column;
    gap: 0.5rem;
  }

  .tag-input {
    border-radius: 8px;
  }

  .tag-action-btn {
    border-radius: 8px;
    width: 100%;
  }

  .username {
    font-size: 1.8rem;
  }

  .profile-avatar {
    width: 100px;
    height: 100px;
  }
}

@media (max-width: 480px) {
  .movies-grid {
    grid-template-columns: 1fr;
  }

  .section-title {
    font-size: 1.5rem;
    padding-left: 15px;
  }

  .section-title::before {
    width: 4px;
  }

  .movie-card-watchlist {
    flex-direction: row;
    height: auto;
  }

  .poster-container {
    width: 120px;
    height: 180px;
    flex-shrink: 0;
  }

  .movie-info {
    flex: 1;
    padding: 0.75rem;
  }

  .movie-title {
    font-size: 1rem;
  }
}
</style>

