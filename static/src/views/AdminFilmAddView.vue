<template>
  <div class="admin-page">
    <div class="admin-container">
      <div class="admin-header">
        <h1 class="admin-title">Add New Film</h1>
        <button class="back-btn" @click="goBack" aria-label="Back to Film Management">
          <img src="/arrow-left.svg" alt="Back" class="back-icon" />
        </button>
      </div>

      <div class="admin-content">
        <div class="add-film-container">
          <form @submit.prevent="handleAddFilm" class="add-film-form">
            <div class="form-group">
              <label for="film-title" class="form-label">Title *</label>
              <input
                id="film-title"
                v-model="newFilm.title"
                type="text"
                class="form-input"
                required
                placeholder="Enter film title"
              />
            </div>

            <div class="form-group">
              <label for="film-tmdb-id" class="form-label">TMDB ID</label>
              <input
                id="film-tmdb-id"
                v-model="newFilm.tmdb_id"
                type="number"
                class="form-input"
                placeholder="TMDB ID (optional)"
              />
            </div>

            <div class="form-group">
              <label for="film-overview" class="form-label">Overview</label>
              <textarea
                id="film-overview"
                v-model="newFilm.overview"
                class="form-textarea"
                rows="4"
                placeholder="Film description (optional)"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Genres</label>
              <div class="genres-selection">
                <div class="genres-list">
                  <div
                    v-for="genre in availableGenres"
                    :key="genre.id"
                    class="genre-chip"
                    :class="{ 'selected': selectedGenres.some(g => g.id === genre.id) }"
                    @click="toggleGenre(genre)"
                  >
                    {{ genre.name }}
                  </div>
                </div>
                <div v-if="selectedGenres.length === 0" class="no-genres">
                  <small>No genres selected</small>
                </div>
                <div v-else class="selected-genres">
                  <small>Selected: {{ selectedGenres.map(g => g.name).join(', ') }}</small>
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="film-release-date" class="form-label">Release Date</label>
                <input
                  id="film-release-date"
                  v-model="newFilm.release_date"
                  type="text"
                  class="form-input"
                  placeholder="2024-04-04"
                />
                <div class="file-hint">
                  <small>Format: YYYY-MM-DD (e.g., 2024-04-04)</small>
                </div>
              </div>

              <div class="form-group">
                <label for="film-duration" class="form-label">Duration (min)</label>
                <input
                  id="film-duration"
                  v-model="newFilm.duration"
                  type="number"
                  class="form-input"
                  placeholder="120"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="film-rating" class="form-label">Rating</label>
                <input
                  id="film-rating"
                  v-model="newFilm.rating"
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  class="form-input"
                  placeholder="8.5"
                />
              </div>

              <div class="form-group">
                <label for="film-vote-count" class="form-label">Vote Count</label>
                <input
                  id="film-vote-count"
                  v-model="newFilm.vote_count"
                  type="number"
                  class="form-input"
                  placeholder="1000"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="film-language" class="form-label">Language</label>
                <input
                  id="film-language"
                  v-model="newFilm.language"
                  type="text"
                  class="form-input"
                  placeholder="en"
                  maxlength="2"
                />
              </div>

            </div>

            <div class="form-group">
              <label for="film-poster-file" class="form-label">Or Upload Poster Image</label>
              <input
                ref="posterInput"
                type="file"
                id="film-poster-file"
                accept="image/*"
                @change="onPosterSelected"
                class="form-input"
              />
              <div class="file-hint">
                <small>Supported formats: PNG, JPG, JPEG, GIF, WebP. Max 5MB.</small>
              </div>
              <div v-if="selectedPosterFile" class="file-preview">
                <small>Selected: {{ selectedPosterFile.name }}</small>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="goBack">Cancel</button>
              <button
                type="submit"
                class="submit-btn"
                :disabled="isAddingFilm"
              >
                {{ isAddingFilm ? 'Adding...' : 'Add Film' }}
              </button>
            </div>
          </form>
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
import { addFilm } from '@/api/admin.js'
import { getAllGenres } from '@/api/film.js'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()

// Toast ref
const toastRef = ref(null)

// Add film modal
const isAddingFilm = ref(false)
const posterInput = ref(null)
const selectedPosterFile = ref(null)
const availableGenres = ref([])
const selectedGenres = ref([])
const newFilm = ref({
  title: '',
  tmdb_id: '',
  overview: '',
  release_date: '',
  duration: '',
  rating: '',
  vote_count: '',
  language: ''
})

// Methods
const goBack = () => {
  router.push('/admin/films')
}

const toggleGenre = (genre) => {
  const index = selectedGenres.value.findIndex(g => g.id === genre.id)
  if (index > -1) {
    selectedGenres.value.splice(index, 1)
  } else {
    selectedGenres.value.push(genre)
  }
}

const onPosterSelected = (event) => {
  const file = event.target.files[0]
  if (!file) {
    selectedPosterFile.value = null
    return
  }

  // Validate file type
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    toastRef.value?.addToast('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)', 'error')
    event.target.value = ''
    selectedPosterFile.value = null
    return
  }

  // Validate file size (5MB max)
  if (file.size > 5 * 1024 * 1024) {
    toastRef.value?.addToast('Image size must be less than 5MB', 'error')
    event.target.value = ''
    selectedPosterFile.value = null
    return
  }

  selectedPosterFile.value = file
}

const handleAddFilm = async () => {
  if (isAddingFilm.value) return

  // Validate required fields
  if (!newFilm.value.title.trim()) {
    toastRef.value?.addToast('Film title is required', 'error')
    return
  }

  // Validate release date format if provided
  if (newFilm.value.release_date.trim()) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/
    if (!dateRegex.test(newFilm.value.release_date.trim())) {
      toastRef.value?.addToast('Release date must be in YYYY-MM-DD format (e.g., 2024-04-04)', 'error')
      return
    }
  }


  try {
    isAddingFilm.value = true

    // Prepare data for API call
    const filmData = {
      title: newFilm.value.title.trim(),
      overview: newFilm.value.overview.trim() || '',
      language: newFilm.value.language.trim() || ''
    }

    // Add selected genres
    if (selectedGenres.value.length > 0) {
      filmData.genre_ids = selectedGenres.value.map(g => g.id)
    }

    // Add optional numeric fields only if they have values
    if (newFilm.value.tmdb_id) {
      filmData.tmdb_id = parseInt(newFilm.value.tmdb_id)
    }
    if (newFilm.value.duration) {
      filmData.duration = parseInt(newFilm.value.duration)
    }
    if (newFilm.value.rating) {
      filmData.rating = parseFloat(newFilm.value.rating)
    }
    if (newFilm.value.vote_count) {
      filmData.vote_count = parseInt(newFilm.value.vote_count)
    }
    if (newFilm.value.release_date) {
      filmData.release_date = newFilm.value.release_date
    }

    // Poster URL is now handled automatically by backend

    // Use the updated addFilm API function
    await addFilm(filmData, selectedPosterFile.value)

    toastRef.value?.addToast('Film added successfully!', 'success')

    // Redirect back to film management page
    setTimeout(() => {
      router.push('/admin/films')
    }, 1500)

  } catch (error) {
    console.error('Failed to add film:', error)
    toastRef.value?.addToast(error.response?.data?.msg || error.message || 'Failed to add film. Please try again.', 'error')
  } finally {
    isAddingFilm.value = false
  }
}

// Load available genres
const loadGenres = async () => {
  try {
    const response = await getAllGenres()
    availableGenres.value = response.data || []
  } catch (error) {
    console.error('Failed to load genres:', error)
    toastRef.value?.addToast('Failed to load genres', 'error')
  }
}

// Check admin access and load genres on mount
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  if (authStore.username !== 'admin') {
    router.push('/')
    return
  }

  await loadGenres()
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
  max-width: 800px;
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

.add-film-container {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* Add Film Form */
.add-film-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.file-hint {
  color: #888888;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.file-preview {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #0a0a0a;
  border-radius: 6px;
  border: 1px solid #333333;
}

.file-preview small {
  color: #f5c518;
  font-weight: 500;
}

.genres-selection {
  margin-top: 0.5rem;
}

.genres-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.genre-chip {
  padding: 0.5rem 1rem;
  background-color: #333333;
  color: #cccccc;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: 1px solid #333333;
}

.genre-chip:hover {
  background-color: #444444;
  color: #ffffff;
}

.genre-chip.selected {
  background-color: #3552b0;
  color: #ffffff;
  border-color: #3552b0;
}

.genre-chip.selected:hover {
  background-color: #2a4193;
}

.no-genres, .selected-genres {
  margin-top: 0.5rem;
}

.no-genres small {
  color: #888888;
}

.selected-genres small {
  color: #f5c518;
  font-weight: 500;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 2rem;
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

  .add-film-container {
    padding: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .cancel-btn,
  .submit-btn {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  .admin-title {
    font-size: 1.8rem;
  }

  .add-film-container {
    padding: 1rem;
  }
}
</style>
