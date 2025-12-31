<template>
  <div class="home-container">
    <section class="search-section">
      <div class="search-content">
        <div class="search-box" @click.stop>
          <label for="movie-search" class="sr-only">Search for movies (Alt+S)</label>
          <input
            id="movie-search"
            ref="searchInput"
            type="text"
            class="search-input"
            placeholder="Search for movies..."
            v-model="searchQuery"
            @input="handleSearchInput"
            @focus="showSuggestions = searchSuggestions.length > 0"
            @keydown.enter="highlightedIndex >= 0 ? selectHighlightedSuggestion() : handleSearch()"
            @keydown.escape="hideSuggestions"
            @keydown.down.prevent="navigateSuggestions(1)"
            @keydown.up.prevent="navigateSuggestions(-1)"
            aria-expanded="false"
            :aria-expanded="showSuggestions.toString()"
            aria-haspopup="listbox"
            aria-autocomplete="list"
            role="combobox"
            aria-describedby="search-help"
          />
          <button class="search-button" @click="handleSearch" aria-label="Search for movies">Search</button>
          <div class="search-shortcut-hint">(Alt+S)</div>
          <div id="search-help" class="sr-only">Type to search for movies. Use arrow keys to navigate suggestions, Enter to select, Escape to close.</div>

          <!-- Search Suggestions Dropdown -->
          <div
            v-if="showSuggestions && (searchSuggestions.length > 0 || isSearching)"
            class="search-suggestions"
            role="listbox"
            aria-label="Movie search suggestions"
          >
            <div v-if="isSearching" class="search-loading">
              <span>Searching...</span>
            </div>
            <div v-else-if="searchSuggestions.length === 0" class="no-suggestions">
              <span>No results found</span>
            </div>
            <div
              v-for="(movie, index) in searchSuggestions"
              :key="movie.id"
              class="suggestion-item"
              :class="{ 'highlighted': index === highlightedIndex }"
              role="option"
              :aria-selected="(index === highlightedIndex).toString()"
              :aria-label="`${movie.title} (${formatReleaseYear(movie.release_date)}), directed by ${formatDirectors(movie.directors)}, rated ${movie.rating?.toFixed(1) || 'N/A'}`"
              @click="selectSuggestion(movie)"
              @mouseenter="highlightedIndex = index"
            >
              <img
                :src="getPosterUrl(movie.poster_url)"
                :alt="movie.title"
                class="suggestion-poster"
                @error="onImageError"
              />
              <div class="suggestion-info">
                <div class="suggestion-title">{{ movie.title }}</div>
                <div class="suggestion-meta">
                  <div class="suggestion-year">{{ formatReleaseYear(movie.release_date) }}</div>
                  <div class="suggestion-director" v-if="movie.directors && movie.directors.length > 0">
                    {{ formatDirectors(movie.directors) }}
                  </div>
                  <div class="suggestion-genres" v-if="movie.genres && movie.genres.length > 0">
                    {{ formatGenres(movie.genres) }}
                  </div>
                </div>
                <div class="suggestion-rating">
                  <img src="/star-yellow.svg" alt="star" class="star-icon" />
                  <span>{{ movie.rating?.toFixed(1) || 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="recommendations.length > 0" class="recommendations-section" aria-labelledby="recommendations-heading">
      <div class="recommendations-content">
        <h2 class="section-title" id="recommendations-heading">Recommended for you</h2>
        <!-- Wide screen: Carousel layout -->
        <div v-if="isWideScreen" class="accordion-container" role="tablist" aria-label="Movie recommendations carousel">
          <div
            v-for="(movie, index) in displayedRecommendations"
            :key="movie.id"
            class="accordion-item"
            :class="{
              'default-active': index === activeIndex && hoveredIndex === -1,
              'hovered': index === hoveredIndex
            }"
            role="tab"
            :aria-selected="((index === activeIndex && hoveredIndex === -1) || index === hoveredIndex).toString()"
            :aria-label="`${movie.title} (${formatReleaseYear(movie.release_date)}), rated ${movie.rating?.toFixed(1) || 'N/A'}`"
            tabindex="0"
            @mouseenter="setHoveredIndex(index)"
            @mouseleave="clearHoveredIndex()"
            @keydown.enter="viewMovie(movie)"
            @keydown.space.prevent="viewMovie(movie)"
          >
            <div class="poster-wrapper">
              <img
                :src="getPosterUrl(movie.poster_url)"
                :alt="movie.title"
                @error="onImageError"
                class="accordion-poster"
              />
              <div class="poster-info">
                <h3 class="movie-title clickable" @click.stop="viewMovie(movie)">{{ movie.title }}</h3>
                <div class="movie-rating">
                  <img src="/star-yellow.svg" alt="star" class="star-icon" />
                  <span class="rating-text">{{ movie.rating?.toFixed(1) || 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Small screen: Card grid layout -->
        <div v-else class="recommendations-grid">
          <MovieCard
            v-for="movie in displayedRecommendations"
            :key="movie.id"
            :movie="movie"
            @title-click="viewMovie"
            @star-click="onStarClick"
            @watchlist-click="addToWatchlist"
          />
        </div>
        <div v-if="isLoading.recommendations" class="loading-placeholder">
          <span>Loading recommendations...</span>
        </div>
        <div v-else-if="recommendations.length === 0" class="no-data">
          <span>No recommendations available</span>
        </div>
      </div>
    </section>

    <section class="content-section" aria-labelledby="main-content">
      <h1 id="main-content" class="sr-only">Film Hub - Discover Movies</h1>
      <div class="container">
        <div class="movie-section">
          <h2 class="section-title" id="top-rated-heading">Top rated</h2>
          <div v-if="isLoading.topRated" class="loading-placeholder">
            <span>Loading top rated movies...</span>
          </div>
          <div v-else-if="topRatedMovies.length > 0" class="movies-grid">
            <MovieCard
              v-for="movie in topRatedMovies"
              :key="movie.id"
              :movie="movie"
              @title-click="viewMovie"
              @star-click="onStarClick"
              @watchlist-click="addToWatchlist"
            />
          </div>
          <div v-else class="no-data">
            <span>No top rated movies available</span>
          </div>
        </div>

        <div class="movie-section">
          <h2 class="section-title" id="newly-released-heading">Newly released</h2>
          <div v-if="isLoading.latest" class="loading-placeholder">
            <span>Loading latest movies...</span>
          </div>
          <div v-else-if="newlyReleasedMovies.length > 0" class="movies-grid">
            <MovieCard
              v-for="movie in newlyReleasedMovies"
              :key="movie.id"
              :movie="movie"
              @title-click="viewMovie"
              @star-click="onStarClick"
              @watchlist-click="addToWatchlist"
            />
          </div>
          <div v-else class="no-data">
            <span>No latest movies available</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import Toast from '@/components/Toast.vue'
import {
  getTopRatedFilms,
  getLatestFilms,
  getRecommendedFilms,
  searchFilms,
  getFilmByTitle
} from '@/api/film.js'

const authStore = useAuthStore()
const router = useRouter()
const searchQuery = ref('')
const currentIndex = ref(0)
const hoveredIndex = ref(-1)
const activeIndex = ref(2)
let autoRotateInterval = null

// Search suggestions
const searchSuggestions = ref([])
const isSearching = ref(false)
const showSuggestions = ref(false)
const highlightedIndex = ref(-1)
let searchTimeout = null

// Search input ref
const searchInput = ref(null)

// Reactive data for API responses
const recommendations = ref([])
const topRatedMovies = ref([])
const newlyReleasedMovies = ref([])
const isLoading = ref({
  recommendations: false,
  topRated: false,
  latest: false
})

// User stats (mock data - in real app from API)
const userStats = ref({
  watchlist: 12,
  reviews: 8,
  favoriteGenre: 'Drama'
})

// Toast component reference
const toastRef = ref(null)

// Keyboard shortcuts handler
const handleKeydown = async (event) => {
  // Alt + S for search input focus
  if (event.altKey && event.key.toLowerCase() === 's') {
    event.preventDefault()
    if (searchInput.value) {
      searchInput.value.focus()
      await nextTick()
      // Optionally clear any existing text
      // searchQuery.value = ''
    }
  }
}

// Check if screen is wide enough for carousel
const isWideScreen = ref(window.innerWidth >= 1200)
const updateScreenSize = () => {
  isWideScreen.value = window.innerWidth >= 1200
}
onMounted(() => {
  window.addEventListener('resize', updateScreenSize)
})
onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
})

const loadData = async () => {
  try {
    isLoading.value.recommendations = true
    if (authStore.isAuthenticated) {
      const recommendResponse = await getRecommendedFilms()
      if (recommendResponse.code === 1) {
        recommendations.value = recommendResponse.data || []
      }
    } else {
      const topRatedResponse = await getTopRatedFilms()
      if (topRatedResponse.code === 1) {
        recommendations.value = topRatedResponse.data || []
      }
    }
  } catch (error) {
    console.error('Failed to load recommendations:', error)
  } finally {
    isLoading.value.recommendations = false
  }

  try {
    isLoading.value.topRated = true
    const topRatedResponse = await getTopRatedFilms()
    if (topRatedResponse.code === 1) {
      topRatedMovies.value = topRatedResponse.data || []
    }
  } catch (error) {
    console.error('Failed to load top rated films:', error)
  } finally {
    isLoading.value.topRated = false
  }

  try {
    isLoading.value.latest = true
    const latestResponse = await getLatestFilms()
    if (latestResponse.code === 1) {
      newlyReleasedMovies.value = latestResponse.data || []
    }
  } catch (error) {
    console.error('Failed to load latest films:', error)
  } finally {
    isLoading.value.latest = false
  }
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

const displayedRecommendations = computed(() =>
  recommendations.value.slice(0, 5)
)

// Handle search input with debouncing
const handleSearchInput = async () => {
  const query = searchQuery.value.trim()

  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  if (!query) {
    searchSuggestions.value = []
    showSuggestions.value = false
    return
  }

  // Debounce search requests
  searchTimeout = setTimeout(async () => {
    try {
      isSearching.value = true
      showSuggestions.value = true

      const response = await searchFilms(query)
      if (response.code === 1) {
        // Limit suggestions to 5 items
        searchSuggestions.value = (response.data || []).slice(0, 5)
      } else {
        searchSuggestions.value = []
      }
    } catch (error) {
      console.error('Search failed:', error)
      searchSuggestions.value = []
    } finally {
      isSearching.value = false
    }
  }, 300) // 300ms debounce
}

const handleSearch = async () => {
  const query = searchQuery.value.trim()
  if (!query) return

  // Hide suggestions
  showSuggestions.value = false

  try {
    const response = await getFilmByTitle(query)
    if (response.code === 1 && response.data && response.data.id) {
      // Found the movie, navigate to its detail page
      router.push(`/films/${response.data.id}`)
    } else {
      // Movie not found, go to search results page
      router.push(`/films?search=${encodeURIComponent(query)}`)
    }
  } catch (error) {
    console.error('Search failed:', error)
    // On error, go to search results page
    router.push(`/films?search=${encodeURIComponent(query)}`)
  }
}

const selectSuggestion = (movie) => {
  searchQuery.value = movie.title
  showSuggestions.value = false
  router.push(`/films/${movie.id}`)
}

// Navigate suggestions with keyboard
const navigateSuggestions = (direction) => {
  if (!showSuggestions.value || searchSuggestions.value.length === 0) return

  const maxIndex = searchSuggestions.value.length - 1
  highlightedIndex.value = Math.max(-1, Math.min(maxIndex, highlightedIndex.value + direction))
}

// Select highlighted suggestion
const selectHighlightedSuggestion = () => {
  if (highlightedIndex.value >= 0 && highlightedIndex.value < searchSuggestions.value.length) {
    selectSuggestion(searchSuggestions.value[highlightedIndex.value])
  }
}

// Hide suggestions when clicking outside
const hideSuggestions = () => {
  showSuggestions.value = false
  highlightedIndex.value = -1
}

const startAutoRotate = () => {
  if (autoRotateInterval) {
    clearInterval(autoRotateInterval)
  }

  if (recommendations.value.length <= 1) return

  autoRotateInterval = setInterval(() => {
    if (hoveredIndex.value === -1) {
      const count = displayedRecommendations.value.length
      if (count > 0) {
        activeIndex.value = (activeIndex.value + 1) % count
      }
    }
  }, 3000)
}

const stopAutoRotate = () => {
  if (autoRotateInterval) {
    clearInterval(autoRotateInterval)
    autoRotateInterval = null
  }
}

const setHoveredIndex = (index) => {
  hoveredIndex.value = index
  stopAutoRotate()
}

const clearHoveredIndex = () => {
  hoveredIndex.value = -1
  startAutoRotate()
}

const setCurrentMovie = (index) => {
  currentIndex.value = index
}

const viewMovie = (movie) => {
  router.push(`/films/${movie.id}`)
}

const addToWatchlist = (movie) => {
  if (authStore.isAuthenticated) {
    // MovieCard component handles the actual API call
    // Here we can show a toast confirmation
    toastRef.value?.addToast(`Added ${movie.title} to watchlist`, 'success')
  } else {
    toastRef.value?.addToast('Please login to add movies to your watchlist', 'warning')
    router.push('/login')
  }
}

const onStarClick = (movie) => {
  if (authStore.isAuthenticated) {
    toastRef.value?.addToast(`Rate ${movie.title}`, 'info')
  } else {
    toastRef.value?.addToast('Please login to rate movies', 'warning')
  }
}

// Format release year
const formatReleaseYear = (releaseDate) => {
  if (!releaseDate) return ''
  try {
    return new Date(releaseDate).getFullYear().toString()
  } catch {
    return ''
  }
}

// Format directors (show up to 2 directors)
const formatDirectors = (directors) => {
  if (!directors || directors.length === 0) return ''
  return directors.slice(0, 2).join(', ')
}

// Format genres (show up to 3 genres)
const formatGenres = (genres) => {
  if (!genres || genres.length === 0) return ''
  return genres.slice(0, 3).join(', ')
}

// Load data on component mount
onMounted(() => {
  loadData()

  // Add click outside listener
  document.addEventListener('click', hideSuggestions)

  // Add keyboard shortcuts
  window.addEventListener('keydown', handleKeydown)
})

// Cleanup on component unmount
onUnmounted(() => {
  stopAutoRotate()

  // Remove click outside listener
  document.removeEventListener('click', hideSuggestions)

  // Remove keyboard shortcuts
  window.removeEventListener('keydown', handleKeydown)

  // Clear search timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})

// Watch for authentication changes
import { watch } from 'vue'
watch(() => authStore.isAuthenticated, () => {
  loadData() // Reload data when auth status changes
})

// Watch for recommendations data to start auto-rotate
watch(() => recommendations.value, (newRecommendations) => {
  if (newRecommendations && newRecommendations.length > 0) {
    startAutoRotate()
  } else {
    stopAutoRotate()
  }
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
}

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

.search-section {
  background-color: #000000;
  padding: 2rem;
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

.search-shortcut-hint {
  font-size: 0.6rem;
  color: #cccccc;
  opacity: 0.8;
  font-weight: normal;
  white-space: nowrap;
  background-color: rgba(0, 0, 0, 0.8);
  padding: 2px 4px;
  border-radius: 3px;
  align-self: center;
  margin-left: 0.5rem;
}

.search-box {
  position: relative;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #1a1a1a;
  border: 1px solid #333333;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
  margin-top: 4px;
  /* Hide scrollbar */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.search-suggestions::-webkit-scrollbar {
  display: none; /* Chrome, Safari, and Opera */
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #333333;
  position: relative;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background-color: #2a2a2a;
}

.suggestion-poster {
  width: 40px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 0.75rem;
}

.suggestion-info {
  flex: 1;
  min-width: 0;
  margin-right: 60px; /* Space for rating */
}

.suggestion-title {
  font-size: 1rem;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-meta {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  margin-bottom: 0.25rem;
}

.suggestion-year {
  font-size: 0.8rem;
  color: #f5c518;
  font-weight: 500;
}

.suggestion-director,
.suggestion-genres {
  font-size: 0.75rem;
  color: #aaaaaa;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-rating {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9rem;
  color: #cccccc;
}

.suggestion-rating .star-icon {
  width: 14px;
  height: 14px;
}

.search-loading,
.no-suggestions {
  padding: 1rem;
  text-align: center;
  color: #888888;
  font-size: 0.9rem;
}

.search-loading {
  color: #f5c518;
}

.recommendations-section {
  background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
  margin-top: -3rem;
  padding: 4rem 2rem;
}

.recommendations-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Show recommendations on all screen sizes */

.accordion-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
  align-items: flex-end;
  height: 500px;
  justify-content: center;
}

.accordion-container::-webkit-scrollbar {
  display: none;
}

.accordion-item {
  flex: 0 0 200px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  transform-origin: bottom center;
}

.accordion-item.default-active,
.accordion-item.hovered {
  transform: scale(1.5);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  z-index: 2; 
}

.poster-wrapper {
  position: relative;
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.accordion-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.poster-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  padding: 0.5rem;
  color: #ffffff;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.accordion-item.default-active .poster-info,
.accordion-item.hovered .poster-info {
  opacity: 1;
}

.movie-title {
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  line-height: 1.3;
  transition: font-size 0.3s ease;
}

.accordion-item.default-active .movie-title,
.accordion-item.hovered .movie-title {
  font-size: 1.2rem;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.star-icon {
  width: 20px;
  height: 20px;
  display: inline-block;
}

.content-section {
  padding: 4rem 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.movie-section {
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2rem;
  font-weight: bold;
  color: #ffffff;
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

/* Recommendations grid - same as movies grid */
.recommendations-grid,
.movies-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
  margin-top: 2rem;
}

.movie-card {
  background-color: #121212;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
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
  justify-content: space-between;
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

.star {
  color: #f5c518;
  font-size: 1.1rem;
}

.star-placeholder {
  color: #5799ef;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.star-placeholder:hover {
  background-color: #2a2a2a;
  color: #666666;
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

.watchlist-btn:hover {
  background-color: #3a3a3a;
  color: #4682d6;
}

.user-section {
  padding: 4rem 2rem;
  background-color: #0a0a0a;
}

.user-greeting {
  font-size: 2rem;
  font-weight: bold;
  color: #f5c518;
  margin-bottom: 2rem;
  text-align: center;
}

/* Loading and empty states */
.loading-placeholder, .no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
  color: #666666;
  font-size: 1.1rem;
}

.loading-placeholder {
  color: #f5c518;
}

.no-data {
  color: #cccccc;
}

.user-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.stat-card {
  background-color: #121212;
  padding: 2rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #333333;
}

.stat-card h3 {
  color: #f5c518;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.stat-card p {
  color: #cccccc;
  font-size: 1.1rem;
  font-weight: bold;
}

@media (max-width: 1200px) {
  .recommendations-grid,
  .movies-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 992px) {
  .recommendations-grid,
  .movies-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .recommendations-section {
    padding: 2rem 1rem;
  }

  .recommendations-grid,
  .movies-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 768px) {
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

  .search-suggestions {
    max-height: 300px;
  }

  .suggestion-item {
    padding: 0.5rem 0.75rem;
  }

  .suggestion-info {
    margin-right: 50px; /* Adjusted for mobile */
  }

  .suggestion-poster {
    width: 30px;
    height: 45px;
  }

  .suggestion-title {
    font-size: 0.9rem;
  }

  .suggestion-rating {
    right: 0.75rem;
    font-size: 0.8rem;
  }

  .suggestion-year {
    font-size: 0.75rem;
  }

  .suggestion-director,
  .suggestion-genres {
    font-size: 0.7rem;
  }
}

  .recommendations-showcase {
    height: 400px;
  }

  .main-poster {
    width: 80%;
  }

  .poster-title {
    font-size: 1.5rem;
  }

  .side-poster {
    width: 120px;
    height: 160px;
  }

  .section-title {
    font-size: 1.8rem;
    padding-left: 15px;
  }

  .section-title::before {
    width: 4px;
  }


  .movie-title {
    font-size: 1rem;
  }

  .user-stats {
    grid-template-columns: 1fr;
  }

</style>
