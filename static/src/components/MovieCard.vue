<template>
  <div class="movie-card" tabindex="0" @keydown="handleCardKeydown" role="button" :aria-label="`View details for ${movie.title}`" @focus="onCardFocus" @blur="onCardBlur">
    <div class="movie-poster">
      <img
        :src="getPosterUrl(movie.poster_url)"
        :alt="movie.title"
        @error="onImageError"
        class="poster-image"
      />
    </div>
    <div class="movie-info">
      <div v-if="!adminMode" class="rating-section">
        <div class="rating-left">
          <img src="/star-yellow.svg" alt="star" class="star-icon" />
          <span class="rating-text">{{ movie.rating?.toFixed(1) || 'N/A' }}</span>
        </div>
        <div class="rating-right">
          <img src="/star-blue.svg" alt="Rate this movie" class="star-placeholder" @click="onStarClick" @keydown.enter="onStarClick" @keydown.space="onStarClick" tabindex="0" role="button" aria-label="Rate this movie"/>
        </div>
      </div>
      <h3 class="movie-title clickable" @click="onTitleClick">{{ movie.title }}</h3>
      <button
        class="watchlist-btn"
        :class="{ 'delete-btn': props.mode === 'delete' }"
        @click.stop="onWatchlistClick"
        :disabled="isAddingToWatchlist || isRemovingFromWatchlist"
      >
        <span v-if="props.mode === 'add'">
          {{ isAddingToWatchlist ? 'Adding...' : '+ Watchlist' }}
        </span>
        <span v-else>
          {{ isRemovingFromWatchlist ? 'Removing...' : 'Delete' }}
        </span>
      </button>
    </div>

    <!-- Rating Modal -->
    <div v-if="showRatingModal" class="rating-modal-overlay" @click="closeRatingModal">
      <div class="rating-modal" @click.stop @keydown="handleRatingKeydown" tabindex="-1">
        <h3 class="rating-modal-title">Rate this movie</h3>
        <p class="rating-instructions">Use ← → arrow keys to adjust rating, Enter to submit, Esc to cancel</p>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { getUserRating, submitRating as submitRatingApi, addFavorite, removeFavorite } from '@/api/user.js'
import Toast from '@/components/Toast.vue'

// Props
const props = defineProps({
  movie: {
    type: Object,
    required: true
  },
  mode: {
    type: String,
    // 'add' for adding to watchlist, 'delete' for removing from watchlist
    default: 'add', 
    validator: (value) => ['add', 'delete'].includes(value)
  },
  adminMode: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['title-click', 'star-click', 'watchlist-click', 'rating-submitted', 'watchlist-added', 'watchlist-removed', 'admin-delete'])

const authStore = useAuthStore()

// Rating modal state
const showRatingModal = ref(false)
const hoverRating = ref(0)
const userRating = ref(0)
const isSubmittingRating = ref(false)

// Watchlist state
const isAddingToWatchlist = ref(false)
const isRemovingFromWatchlist = ref(false)

// Toast component reference
const toastRef = ref(null)

// Helper function to get poster URL
const getPosterUrl = (posterUrl) => {
  if (!posterUrl) return '/film.jpg'
  return `/posters/${posterUrl}`
}

// Fallback handler when image fails to load
const onImageError = (e) => {
  try {
    e.target.src = '/film.jpg'
  } catch (err) {
    // ignore
  }
}

// Event handlers
const onTitleClick = () => {
  emit('title-click', props.movie)
}

const onCardFocus = () => {
  // Focus handler - could be used for additional focus behavior
}

const onCardBlur = () => {
  // Blur handler - could be used for additional blur behavior
}

const handleCardKeydown = (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    onTitleClick()
  }
}

const onStarClick = async () => {
  if (!authStore.isAuthenticated) {
    toastRef.value?.addToast('Please login to rate movies', 'warning')
    return
  }

  // Reset rating states
  hoverRating.value = 0
  userRating.value = 0

  // Load existing rating
  try {
    const response = await getUserRating(props.movie.id)
    if (response.code === 1 && response.data && response.data.rating) {
      userRating.value = response.data.rating
    }
  } catch (error) {
    console.error('Failed to load user rating:', error)
    // Continue with rating modal even if loading fails
  }

  // Show rating modal
  showRatingModal.value = true

  // Focus modal for keyboard navigation
  await nextTick()
  const modal = document.querySelector('.rating-modal')
  if (modal) {
    modal.focus()
  }
}

const onWatchlistClick = async () => {
  if (props.adminMode) {
    // In admin mode, show confirmation before delete
    const confirmed = await toastRef.value?.addConfirm(`Delete "${props.movie.title}"?`, {
      confirmText: 'Delete',
      cancelText: 'Cancel',
      type: 'warning'
    })

    if (!confirmed) return

    // Emit delete event after confirmation
    emit('admin-delete', props.movie)
    return
  }

  if (!authStore.isAuthenticated) {
    toastRef.value?.addToast('Please login to add movies to your watchlist', 'warning')
    return
  }

  if (props.mode === 'delete') {
    await onWatchlistRemove()
  } else {
    await onWatchlistAdd()
  }
}

const onWatchlistAdd = async () => {
  if (isAddingToWatchlist.value) return

  try {
    isAddingToWatchlist.value = true
    await addFavorite({ film_id: props.movie.id })
    toastRef.value?.addToast('Movie added to watchlist successfully!', 'success')
    emit('watchlist-added', props.movie)
  } catch (error) {
    console.error('Failed to add movie to watchlist:', error)
    toastRef.value?.addToast('Failed to add movie to watchlist. Please try again.', 'error')
  } finally {
    isAddingToWatchlist.value = false
  }
}

const onWatchlistRemove = async () => {
  if (isRemovingFromWatchlist.value) return

  // Show confirmation dialog
  const confirmed = await toastRef.value?.addConfirm(
    `Remove "${props.movie.title}" from your watchlist?`,
    {
      confirmText: 'Remove',
      cancelText: 'Cancel',
      type: 'warning'
    }
  )

  if (!confirmed) return

  try {
    isRemovingFromWatchlist.value = true
    await removeFavorite({ film_id: props.movie.id })
    toastRef.value?.addToast('Movie removed from watchlist successfully!', 'success')
    emit('watchlist-removed', props.movie)
  } catch (error) {
    console.error('Failed to remove movie from watchlist:', error)
    toastRef.value?.addToast('Failed to remove movie from watchlist. Please try again.', 'error')
  } finally {
    isRemovingFromWatchlist.value = false
  }
}

// Rating modal functions
const closeRatingModal = () => {
  showRatingModal.value = false
  hoverRating.value = 0
}

const submitRating = async (rating) => {
  if (isSubmittingRating.value) return

  try {
    isSubmittingRating.value = true
    await submitRatingApi({
      film_id: props.movie.id,
      rating: rating
    })

    // Update local rating state
    userRating.value = rating

    // Close modal
    closeRatingModal()

    // Show success toast
    toastRef.value?.addToast(`Successfully rated "${props.movie.title}" ${rating} stars!`, 'success')

    // Emit event to parent component
    emit('rating-submitted', { movie: props.movie, rating })

  } catch (error) {
    console.error('Failed to submit rating:', error)
    toastRef.value?.addToast('Failed to submit rating. Please try again.', 'error')
  } finally {
    isSubmittingRating.value = false
  }
}

// Keyboard navigation for rating modal
const handleRatingKeydown = (event) => {
  const currentRating = hoverRating.value || userRating.value || 0

  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      // Decrease rating (minimum 1)
      hoverRating.value = Math.max(1, currentRating - 1)
      break
    case 'ArrowRight':
      event.preventDefault()
      // Increase rating (maximum 10)
      hoverRating.value = Math.min(10, currentRating + 1)
      break
    case 'Enter':
      event.preventDefault()
      // Submit current rating
      if (hoverRating.value || userRating.value) {
        submitRating(hoverRating.value || userRating.value)
      }
      break
    case 'Escape':
      event.preventDefault()
      // Close modal
      closeRatingModal()
      break
  }
}
</script>

<style scoped>
.movie-card {
  background-color: #121212;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease, outline 0.2s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
  outline: none;
}

.movie-card:focus-visible,
.movie-card:focus {
  outline: 2px solid #ffffff;
  outline-offset: 2px;
}

.movie-poster {
  height: 300px;
  background-color: #1a1a1a;
  overflow: hidden;
}

.poster-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-info {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  justify-content: space-between;
}

.rating-section {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.rating-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-right {
  display: flex;
  align-items: center;
}

.star-icon {
  width: 20px;
  height: 20px;
  display: inline-block;
  margin-right: 0.5rem;
  filter: drop-shadow(0 1px 0 rgba(0,0,0,0.4));
}

.star-placeholder {
  width: 22px;
  height: 22px;
  cursor: pointer;
  transition: transform 0.15s ease, filter 0.15s ease;
}

.star-placeholder:hover {
  transform: scale(1.08);
  filter: brightness(0.85);
}

.rating-text {
  color: #ffffff;
  font-weight: bold;
  font-size: 0.9rem;
}

.movie-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 1rem;
  line-height: 1.4;
  text-align: center;
}

.movie-title.clickable {
  cursor: pointer;
  transition: text-decoration 0.3s ease;
}

.movie-title.clickable:hover {
  text-decoration: underline;
}

.watchlist-btn {
  background-color: #2a2a2a;
  border: none;
  color: #5799ef;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  padding: 0.5rem;
  text-align: center;
  border-radius: 6px;
}

.watchlist-btn:hover:not(:disabled) {
  background-color: #3a3a3a;
  color: #4682d6;
}

.watchlist-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
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
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.rating-modal-title {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1rem;
}

.rating-instructions {
  color: #cccccc;
  font-size: 0.7rem;
  text-align: center;
  margin-bottom: 1.5rem;
  font-style: italic;
  line-height: 1.4;
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
</style>
