<template>
  <div class="film-detail">
    <!-- Movie Information Section -->
    <section class="movie-info-section" v-if="film">
      <div class="movie-info-container">
        <!-- Movie Poster -->
        <div class="movie-poster">
          <img
            :src="getPosterUrl(film.poster_url)"
            :alt="film.title"
            @error="onImageError"
            class="poster-image"
          />
        </div>

        <!-- Movie Details -->
        <div class="movie-details">
          <div class="movie-header">
            <h1 class="movie-title">{{ film.title }}</h1>
            <button
              class="watchlist-btn-header"
              @click="addToWatchlist"
              :disabled="!isAuthenticated"
            >
              + Watchlist
              <span class="shortcut-hint">(Alt+W)</span>
            </button>
          </div>

          <!-- Movie Meta Information -->
          <div class="movie-meta">
            <div class="meta-item" v-if="film.genres && film.genres.length > 0">
              <span class="meta-label">Genres:</span>
              <span class="meta-value">{{ film.genres.join(', ') }}</span>
            </div>
            <div class="meta-item" v-if="film.release_date">
              <span class="meta-label">Release Date:</span>
              <span class="meta-value">{{ formatReleaseDate(film.release_date) }}</span>
            </div>
            <div class="meta-item" v-if="film.duration">
              <span class="meta-label">Duration:</span>
              <span class="meta-value">{{ film.duration }} minutes</span>
            </div>
            <div class="meta-item" v-if="film.language">
              <span class="meta-label">Language:</span>
              <span class="meta-value">{{ formatLanguage(film.language) }}</span>
            </div>
          </div>

          <!-- Rating Block -->
          <div class="rating-block">
            <div class="rating-stars" @click="openRatingModal">
              <img src="/star-yellow.svg" alt="star" class="star-icon" />
              <span class="rating-value">{{ film.rating?.toFixed(1) || 'N/A' }}</span>
            </div>
            <div class="rating-placeholder" @click="openRatingModal">
              <img src="/star-blue.svg" alt="rate" class="star-placeholder-icon" />
              <span class="placeholder-text">Rate this movie <span class="shortcut-hint">(Alt+S)</span></span>
            </div>
          </div>

          <!-- Plot Summary -->
          <div class="plot-section" v-if="film.overview">
            <h3 class="plot-title">Plot Summary</h3>
            <p class="plot-text">{{ film.overview }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Posts and Comments Section -->
    <section class="posts-section">
      <div class="posts-container">
        <h2 class="section-title">Reviews</h2>
        <PostsListRegular
          :posts="posts"
          :loading="loading"
          :has-more-posts="hasMorePosts"
          :loading-more="loadingMore"
          :empty-message="'No discussions yet. Be the first to start a conversation!'"
          :context="'film'"
          :context-value="film?.title"
          @load-more="loadMorePosts"
          @post-updated="onPostUpdated"
          @post-deleted="onPostDeleted"
          @post-created="onPostCreated"
          class="posts-list-component"
        />
      </div>
    </section>

    <!-- Rating Modal -->
    <div v-if="showRatingModal" class="rating-modal-overlay" @click="closeRatingModal">
      <div class="rating-modal" @click.stop>
        <h3 class="rating-modal-title">Rate this movie</h3>
        <div class="stars-container">
          <div
            v-for="star in 10"
            :key="star"
            class="star-rating"
            :class="{ 'active': star <= hoverRating || star <= userRating }"
            @mouseenter="hoverRating = star"
            @mouseleave="hoverRating = 0"
            @click="submitRating(star)"
          >
            <img :src="star <= hoverRating || star <= userRating ? '/star-yellow.svg' : '/star-blue.svg'" alt="star" />
          </div>
        </div>
        <div class="rating-modal-actions">
          <button class="cancel-btn" @click="closeRatingModal">Cancel</button>
          <button
            class="submit-btn"
            @click="submitRating(hoverRating || userRating)"
            :disabled="isSubmittingRating || (!hoverRating && !userRating)"
          >
            {{ isSubmittingRating ? 'Submitting...' : 'Submit' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { getFilmById, getFilmPosts } from '@/api/film.js'
import { addFavorite as addToWatchlistApi, getUserRating, submitRating as submitRatingApi } from '@/api/user.js'
import PostsListRegular from '@/components/PostsListRegular.vue'
import Toast from '@/components/Toast.vue'

// Route and store
const route = useRoute()
const authStore = useAuthStore()

// Data
const film = ref(null)
const posts = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const hasMorePosts = ref(true)
const currentPage = ref(0)
const pageSize = 10

// Rating modal state
const showRatingModal = ref(false)
const hoverRating = ref(0)
const userRating = ref(0)
const isSubmittingRating = ref(false)

// Toast component reference
const toastRef = ref(null)

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Keyboard shortcuts handler
const handleKeydown = (event) => {
  // Alt + S for rating
  if (event.altKey && event.key.toLowerCase() === 's') {
    event.preventDefault()
    openRatingModal()
  }
  // Alt + W for adding to watchlist
  if (event.altKey && event.key.toLowerCase() === 'w') {
    event.preventDefault()
    addToWatchlist()
  }
}

// Methods
const loadFilmData = async () => {
  try {
    loading.value = true
    const filmId = route.params.id

    if (!filmId) {
      console.error('No film ID provided')
      return
    }

    const response = await getFilmById(filmId)
    if (response.code === 1) {
      film.value = response.data
      console.log('Film data loaded:', film.value)
    } else {
      console.error('Failed to load film data:', response)
    }
  } catch (error) {
    console.error('Error loading film data:', error)
  } finally {
    loading.value = false
  }
}

const loadPosts = async (page = 0, append = false) => {
  try {
    if (page === 0) {
      loading.value = true
    } else {
      loadingMore.value = true
    }

    const filmId = route.params.id
    const response = await getFilmPosts(filmId, {
      page: page + 1, // API uses 1-based pagination
      per_page: pageSize
    })

    if (response.code === 1) {
      const newPosts = response.data?.posts || []

      if (append) {
        posts.value.push(...newPosts)
      } else {
        posts.value = newPosts
      }

      hasMorePosts.value = newPosts.length === pageSize
      currentPage.value = page
    } else {
      // Handle error case
      posts.value = []
      hasMorePosts.value = false
    }

  } catch (error) {
    console.error('Error loading posts:', error)
    posts.value = []
    hasMorePosts.value = false
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMorePosts = () => {
  if (!hasMorePosts.value || loadingMore.value) return
  loadPosts(currentPage.value + 1, true)
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

// Language code mapping
const languageMap = {
  'en': 'English',
  'ko': 'Korean',
  'fi': 'Finnish',
  'fr': 'French',
  'es': 'Spanish',
  'zh': 'Chinese',
  'ja': 'Japanese',
  'no': 'Norwegian',
  'kn': 'Kannada',
  'hi': 'Hindi',
  'ru': 'Russian',
  'te': 'Telugu',
  'ml': 'Malayalam',
  'fa': 'Persian',
  'de': 'German',
  'it': 'Italian',
  'pt': 'Portuguese'
}

const formatLanguage = (languageCode) => {
  if (!languageCode) return ''
  return languageMap[languageCode] || languageCode
}

const formatReleaseDate = (dateString) => {
  if (!dateString) return ''
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

const addToWatchlist = async () => {
  if (!isAuthenticated.value) {
    toastRef.value?.addToast('Please login to add movies to your watchlist', 'warning')
    return
  }

  try {
    await addToWatchlistApi({ film_id: film.value.id })
    toastRef.value?.addToast('Movie added to watchlist!', 'success')
  } catch (error) {
    console.error('Failed to add to watchlist:', error)
    toastRef.value?.addToast('Failed to add movie to watchlist. Please try again.', 'error')
  }
}

// Rating modal functions
const openRatingModal = async () => {
  if (!isAuthenticated.value) {
    toastRef.value?.addToast('Please login to rate movies', 'warning')
    return
  }

  // Reset rating states
  hoverRating.value = 0
  userRating.value = 0

  // Load existing rating
  try {
    const response = await getUserRating(film.value.id)
    if (response.code === 1 && response.data && response.data.rating) {
      userRating.value = response.data.rating
    }
  } catch (error) {
    console.error('Failed to load user rating:', error)
    // Continue with rating modal even if loading fails
  }

  // Show rating modal
  showRatingModal.value = true
}

const closeRatingModal = () => {
  showRatingModal.value = false
  hoverRating.value = 0
}

const submitRating = async (rating) => {
  if (isSubmittingRating.value) return

  try {
    isSubmittingRating.value = true
    await submitRatingApi({
      film_id: film.value.id,
      rating: rating
    })

    // Update local rating state
    userRating.value = rating

    // Close modal
    closeRatingModal()

    toastRef.value?.addToast('Rating submitted successfully!', 'success')

  } catch (error) {
    console.error('Failed to submit rating:', error)
    toastRef.value?.addToast('Failed to submit rating. Please try again.', 'error')
  } finally {
    isSubmittingRating.value = false
  }
}

// Event handlers for PostsList
const onPostUpdated = (post) => {
  console.log('Post updated:', post.post_id)
}

const onPostDeleted = (post) => {
  posts.value = posts.value.filter(p => p.post_id !== post.post_id)
  console.log('Post deleted:', post.post_id)
}

const onPostCreated = (postData) => {
  console.log('Post created:', postData)
  // Optionally reload posts to show the new post
  loadPosts(0, false)
}

// Lifecycle
onMounted(() => {
  // Force scroll to top immediately and after a short delay to ensure it works
  window.scrollTo(0, 0)
  setTimeout(() => window.scrollTo(0, 0), 0)

  // Add keyboard shortcuts
  window.addEventListener('keydown', handleKeydown)

  loadFilmData()
  loadPosts(0, false)
})

onUnmounted(() => {
  // Remove keyboard shortcuts
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.film-detail {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
}

/* Movie Information Section */
.movie-info-section {
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
}

.movie-info-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 3rem;
  align-items: start;
}

.movie-poster {
  position: relative;
}

.poster-image {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  max-width: 300px;
}

.movie-details {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.movie-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
  line-height: 1.2;
}

.movie-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.meta-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.meta-label {
  color: #f5c518;
  font-weight: 600;
  min-width: 100px;
}

.meta-value {
  color: #cccccc;
}

/* Rating Block */
.rating-block {
  display: flex;
  gap: 2rem;
  align-items: center;
  background-color: #1a1a1a;
  padding: 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
}

.rating-stars,
.rating-placeholder {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.star-icon {
  width: 24px;
  height: 24px;
}

.rating-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #f5c518;
}

.star-placeholder-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
}

.placeholder-text {
  color: #5799ef;
  font-size: 0.9rem;
  opacity: 0.8;
}

.shortcut-hint {
  color: #cccccc;
  font-size: 0.75rem;
  opacity: 0.7;
  font-weight: normal;
}

/* Movie Header */
.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

/* Watchlist Button */
.watchlist-btn-header {
  background-color: #2a2a2a;
  color: #5799ef;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.watchlist-btn-header:hover:not(:disabled) {
  background-color: #3a3a3a;
  color: #4682d6;
}

.watchlist-btn-header:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.watchlist-btn-header .shortcut-hint {
  display: block;
  font-size: 0.7rem;
  margin-top: 2px;
  opacity: 0.8;
}

/* Rating Block */
.rating-block {
  display: flex;
  gap: 2rem;
  align-items: center;
  background-color: #1a1a1a;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.rating-stars,
.rating-placeholder {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.rating-stars:hover,
.rating-placeholder:hover {
  opacity: 0.8;
}

.star-icon {
  width: 20px;
  height: 20px;
}

.rating-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #f5c518;
}

.star-placeholder-icon {
  width: 18px;
  height: 18px;
}

.placeholder-text {
  color: #ffffff;
  font-size: 0.9rem;
}

/* Plot Summary */
.plot-section {
  margin-top: 1rem;
}

.plot-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 1rem;
}

.plot-text {
  color: #cccccc;
  line-height: 1.6;
  font-size: 1rem;
}

/* Posts Section */
.posts-section {
  padding: 2rem;
}

.posts-container {
  padding: 2rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  padding-top: 0;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 0.25rem;
  text-align: left;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .movie-info-container {
    grid-template-columns: 250px 1fr;
    gap: 2rem;
  }

  .movie-title {
    font-size: 2rem;
  }
}

@media (max-width: 768px) {
  .movie-info-section,
  .posts-section {
    padding: 2rem 1rem;
  }

  .movie-info-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .movie-poster {
    text-align: center;
  }

  .poster-image {
    max-width: 250px;
  }

  .movie-title {
    font-size: 1.75rem;
    text-align: center;
  }

  .rating-block {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .watchlist-btn {
    align-self: center;
  }

  .section-title {
    font-size: 1.5rem;
    padding-left: 15px;
  }

  .section-title::before {
    width: 4px;
  }
}

@media (max-width: 480px) {
  .movie-info-section,
  .posts-section {
    padding: 1rem 0.5rem;
  }

  .movie-title {
    font-size: 1.5rem;
  }

  .rating-block {
    padding: 1rem;
  }

  .plot-text {
    font-size: 0.9rem;
  }

  .movie-header {
    flex-direction: column;
    gap: 1rem;
  }

  .watchlist-btn-header {
    align-self: flex-end;
  }

  .rating-block {
    padding: 0.75rem;
  }

  .rating-value {
    font-size: 1rem;
  }
}

/* Rating Modal Styles */
.rating-modal-overlay {
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

.rating-modal {
  background-color: #121212;
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.rating-modal-title {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1.5rem;
}

.stars-container {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.star-rating {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.star-rating:hover {
  transform: scale(1.1);
}

.star-rating img {
  width: 32px;
  height: 32px;
  display: block;
}

.star-rating.active img {
  filter: brightness(1.2);
}

.rating-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #333333;
  color: #cccccc;
}

.cancel-btn:hover {
  background-color: #444444;
  color: #ffffff;
}

.submit-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.submit-btn:disabled {
  background-color: #555555;
  cursor: not-allowed;
  opacity: 0.6;
}

.posts-list-component {
  margin-top: 0;
  padding-top: 0;
}
</style>
