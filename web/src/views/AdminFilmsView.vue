<template>
  <div class="admin-page">
    <!-- Search Section -->
    <section class="search-section">
      <div class="search-content">
        <div class="search-box" @click.stop>
          <label for="film-search" class="sr-only">Search for films</label>
          <input
            id="film-search"
            type="text"
            class="search-input"
            placeholder="Search films by title..."
            v-model="searchQuery"
            @input="handleSearchInput"
            @keydown.enter="handleSearch"
          />
          <button class="search-button" @click="handleSearch">Search</button>
        </div>
      </div>
    </section>

    <!-- Films Section -->
    <section class="films-section">
      <div class="container">
        <div v-if="isLoading" class="loading-placeholder">
          <span>Loading films...</span>
        </div>
        <div v-else-if="films.length > 0" class="films-grid">
          <MovieCard
            v-for="film in films"
            :key="film.id"
            :movie="film"
            mode="delete"
            :admin-mode="true"
            @admin-delete="onDeleteFilm"
          />
        </div>
        <div v-else class="no-data">
          <span>No films found</span>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreFilms && films.length > 0" class="load-more-container">
          <button
            class="load-more-btn"
            @click="loadMoreFilms"
            :disabled="loadingMore"
            :class="{ loading: loadingMore }"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Films' }}
          </button>
        </div>
      </div>
    </section>


    <!-- Floating Add Button -->
    <button class="floating-add-btn" @click="goToAddFilm" aria-label="Add new film">
      <img src="/plus.svg" alt="Add" class="add-icon" />
    </button>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import { getAdminFilms, deleteFilm, addFilm } from '@/api/admin.js'
import MovieCard from '@/components/MovieCard.vue'
import Toast from '@/components/Toast.vue'

const authStore = useAuthStore()
const router = useRouter()

// Search state
const searchQuery = ref('')
let searchTimeout = null

// Data state
const films = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMoreFilms = ref(true)
const currentPage = ref(0)
const pageSize = 20

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
  hasMoreFilms.value = true

  // Debounce search
  searchTimeout = setTimeout(() => {
    loadFilms(true)
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 0
  hasMoreFilms.value = true
  loadFilms(true)
}

// Load films
const loadFilms = async (reset = false) => {
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
      params.title = searchQuery.value.trim()
    }

    const response = await getAdminFilms(params)

    if (response.code === 1 && response.data) {
      if (reset) {
        films.value = response.data.films || []
      } else {
        films.value.push(...(response.data.films || []))
      }

      hasMoreFilms.value = (response.data.films || []).length === pageSize
      currentPage.value = response.data.page || 1
    } else {
      if (reset) {
        films.value = []
      }
      hasMoreFilms.value = false
    }
  } catch (error) {
    console.error('Failed to load films:', error)
    if (reset) {
      films.value = []
    }
    hasMoreFilms.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMoreFilms = () => {
  if (!hasMoreFilms.value || loadingMore.value) return
  loadFilms(false)
}

// Delete film
const onDeleteFilm = async (film) => {
  try {
    await deleteFilm(film.id)
    // Reload films after successful deletion
    await loadFilms(true)
    toastRef.value?.addToast(`Film "${film.title}" has been successfully deleted`, 'success')
  } catch (error) {
    console.error('Failed to delete film:', error)
    toastRef.value?.addToast('Failed to delete film. Please try again.', 'error')
  }
}

// Navigation methods
const goToAddFilm = () => {
  router.push('/admin/films/add')
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

  loadFilms(true)
})

// Cleanup on unmount
onUnmounted(() => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
/* Search Section - Copied from AdminUsersView.vue */
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

/* Films Section */
.films-section {
  padding: 3rem 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.films-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
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

/* Floating Add Button */
.floating-add-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #3552b0;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(53, 82, 176, 0.4);
  transition: all 0.3s ease;
  z-index: 100;
}

.floating-add-btn:hover {
  background: #2a4193;
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(53, 82, 176, 0.5);
}

.add-icon {
  width: 24px;
  height: 24px;
  display: block;
}


/* Responsive Design */
@media (max-width: 1200px) {
  .films-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 992px) {
  .search-section {
    padding: 1.5rem 1rem 0.75rem 1rem;
  }

  .films-section {
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

  .films-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }

  .modal-content {
    padding: 1.5rem;
    max-width: 95vw;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .floating-add-btn {
    bottom: 1.5rem;
    right: 1.5rem;
    width: 56px;
    height: 56px;
  }

  .add-icon {
    width: 20px;
    height: 20px;
  }
}

@media (max-width: 768px) {
  .search-section {
    padding: 1rem 0.5rem 0.5rem 0.5rem;
  }

  .films-section {
    padding: 1rem 0.5rem;
  }

  .loading-placeholder, .no-data {
    padding: 2rem 1rem;
    font-size: 1rem;
  }

  .films-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .modal-content {
    padding: 1rem;
  }

  .modal-actions {
    flex-direction: column;
  }

  .cancel-btn,
  .submit-btn {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
}
</style>
