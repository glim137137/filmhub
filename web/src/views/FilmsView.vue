<template>
  <div class="films-page">
    <!-- Search Section -->
    <section class="search-section">
      <div class="search-content">
        <div class="search-box" @click.stop>
          <label for="movie-search" class="sr-only">Search for movies</label>
          <input
            id="movie-search"
            type="text"
            class="search-input"
            placeholder="Search for movies..."
            v-model="searchQuery"
            @input="handleSearchInput"
            @focus="showSuggestions = searchSuggestions.length > 0"
            @keydown.enter="handleSearch"
            @keydown.escape="hideSuggestions"
            @keydown.down.prevent="navigateSuggestions(1)"
            @keydown.up.prevent="navigateSuggestions(-1)"
          />
          <button class="search-button" @click="handleSearch">Search</button>

          <!-- Search Suggestions Dropdown -->
          <div v-if="showSuggestions && (searchSuggestions.length > 0 || isSearching)" class="search-suggestions">
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

    <!-- Filters Section -->
    <section class="filters-section">
      <div class="filters-content">
        <div class="filters-grid">
          <!-- Genre Filter -->
          <div class="filter-group">
            <label class="filter-label">Genre</label>
            <div class="custom-select" @click.stop="toggleGenreDropdown" :class="{ 'active': showGenreDropdown }">
              <div class="select-display">
                <span>{{ getGenreDisplayText() }}</span>
                <span class="select-arrow">▼</span>
              </div>
              <div v-if="showGenreDropdown" class="select-dropdown">
                <div class="dropdown-item" @click.stop="selectGenre('')">All Genres</div>
                <div
                  v-for="genre in genres"
                  :key="genre.id"
                  class="dropdown-item"
                  @click.stop="selectGenre(genre.id)"
                >
                  {{ genre.name }}
                </div>
              </div>
            </div>
          </div>

          <!-- Year Filter -->
          <div class="filter-group">
            <label class="filter-label">Year</label>
            <div class="custom-select" @click.stop="toggleYearDropdown" :class="{ 'active': showYearDropdown }">
              <div class="select-display">
                <span>{{ getYearDisplayText() }}</span>
                <span class="select-arrow">▼</span>
              </div>
              <div v-if="showYearDropdown" class="select-dropdown">
                <div class="dropdown-item" @click.stop="selectYear('')">All Years</div>
                <div
                  v-for="year in years"
                  :key="year"
                  class="dropdown-item"
                  @click.stop="selectYear(year)"
                >
                  {{ year }}
                </div>
              </div>
            </div>
          </div>

          <!-- Language Filter -->
          <div class="filter-group">
            <label class="filter-label">Language</label>
            <div class="custom-select" @click.stop="toggleLanguageDropdown" :class="{ 'active': showLanguageDropdown }">
              <div class="select-display">
                <span>{{ getLanguageDisplayText() }}</span>
                <span class="select-arrow">▼</span>
              </div>
              <div v-if="showLanguageDropdown" class="select-dropdown">
                <div class="dropdown-item" @click.stop="selectLanguage('')">All Languages</div>
                <div
                  v-for="lang in languages"
                  :key="lang"
                  class="dropdown-item"
                  @click.stop="selectLanguage(lang)"
                >
                  {{ formatLanguage(lang) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Movies Grid Section -->
    <section class="movies-section">
      <div class="container">
        <div v-if="isLoading" class="loading-placeholder">
          <span>Loading movies...</span>
        </div>
        <div v-else-if="movies.length > 0" class="movies-grid">
          <MovieCard
            v-for="movie in movies"
            :key="movie.id"
            :movie="movie"
            @title-click="viewMovie"
            @star-click="onStarClick"
            @watchlist-added="onWatchlistAdded"
          />
        </div>
        <div v-else class="no-data">
          <span>No movies found matching your criteria</span>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreMovies && movies.length > 0" class="load-more-container">
          <button
            class="load-more-btn"
            @click="loadMoreMovies"
            :disabled="loadingMore"
            :class="{ loading: loadingMore }"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Movies' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import MovieCard from '@/components/MovieCard.vue'
import {
  searchFilms,
  getFilmByTitle,
  getAllGenres,
  getFilteredFilms
} from '@/api/film.js'

const router = useRouter()

// Search state
const searchQuery = ref('')
const searchSuggestions = ref([])
const isSearching = ref(false)
const showSuggestions = ref(false)
const highlightedIndex = ref(-1)
let searchTimeout = null

// Filters state
const filters = ref({
  genre: '',
  year: '',
  language: ''
})

// Custom select dropdown states
const showGenreDropdown = ref(false)
const showYearDropdown = ref(false)
const showLanguageDropdown = ref(false)

// Data state
const movies = ref([])
const genres = ref([])
const years = ref([])
const languages = ref([])
const isLoading = ref(false)
const loadingMore = ref(false)
const hasMoreMovies = ref(true)
const currentPage = ref(0)
const pageSize = 20

// Initialize filters and load initial data
const initializeFilters = () => {
  // Generate years from 1900 to current year
  const currentYear = new Date().getFullYear()
  years.value = []
  for (let year = currentYear; year >= 1900; year--) {
    years.value.push(year.toString())
  }

  // Common languages (using language codes)
  languages.value = [
    'en', 'es', 'fr', 'de', 'it',
    'pt', 'ru', 'ja', 'ko', 'zh'
  ]
}

const loadGenres = async () => {
  try {
    const response = await getAllGenres()
    if (response.code === 1) {
      genres.value = response.data || []
    }
  } catch (error) {
    console.error('Failed to load genres:', error)
  }
}

const loadMovies = async (page = 0, append = false) => {
  try {
    if (page === 0) {
      isLoading.value = true
    } else {
      loadingMore.value = true
    }

    const params = {
      page: page + 1,
      per_page: pageSize,
      genre_id: filters.value.genre || undefined,
      year: filters.value.year || undefined,
      language: filters.value.language || undefined
    }

    const response = await getFilteredFilms(params)

    if (response.code === 1) {
      const newMovies = response.data?.films || []

      if (append) {
        movies.value.push(...newMovies)
      } else {
        movies.value = newMovies
      }

      hasMoreMovies.value = newMovies.length === pageSize
      currentPage.value = page
    } else {
      movies.value = []
      hasMoreMovies.value = false
    }

  } catch (error) {
    console.error('Failed to load movies:', error)
    movies.value = []
    hasMoreMovies.value = false
  } finally {
    isLoading.value = false
    loadingMore.value = false
  }
}

const loadMoreMovies = () => {
  if (!hasMoreMovies.value || loadingMore.value) return
  loadMovies(currentPage.value + 1, true)
}

const applyFilters = () => {
  // Reset to first page when filters change
  currentPage.value = 0
  hasMoreMovies.value = true
  loadMovies(0, false)
}

// Custom select methods
const toggleGenreDropdown = () => {
  showGenreDropdown.value = !showGenreDropdown.value
  showYearDropdown.value = false
  showLanguageDropdown.value = false
}

const toggleYearDropdown = () => {
  showYearDropdown.value = !showYearDropdown.value
  showGenreDropdown.value = false
  showLanguageDropdown.value = false
}

const toggleLanguageDropdown = () => {
  showLanguageDropdown.value = !showLanguageDropdown.value
  showGenreDropdown.value = false
  showYearDropdown.value = false
}

const selectGenre = (genreId) => {
  filters.value.genre = genreId
  showGenreDropdown.value = false
  applyFilters()
}

const selectYear = (year) => {
  filters.value.year = year
  showYearDropdown.value = false
  applyFilters()
}

const selectLanguage = (language) => {
  filters.value.language = language
  showLanguageDropdown.value = false
  applyFilters()
}

const getGenreDisplayText = () => {
  if (!filters.value.genre) return 'All Genres'
  const genre = genres.value.find(g => g.id == filters.value.genre)
  return genre ? genre.name : 'All Genres'
}

const getYearDisplayText = () => {
  return filters.value.year || 'All Years'
}

const getLanguageDisplayText = () => {
  if (!filters.value.language) return 'All Languages'
  return formatLanguage(filters.value.language)
}

// Search functionality (copied from HomeView)
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

// Helper functions
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

const viewMovie = (movie) => {
  router.push(`/films/${movie.id}`)
}

const onStarClick = (movie) => {
  console.log(`Star clicked for movie: ${movie.title}`)
  // Handle star click - could be for favorites or ratings
}

const onWatchlistAdded = (movie) => {
  console.log(`Movie added to watchlist: ${movie.title}`)
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

// Format functions (copied from HomeView)
const formatReleaseYear = (releaseDate) => {
  if (!releaseDate) return ''
  try {
    return new Date(releaseDate).getFullYear().toString()
  } catch {
    return ''
  }
}

const formatDirectors = (directors) => {
  if (!directors || directors.length === 0) return ''
  return directors.slice(0, 2).join(', ')
}

const formatGenres = (genres) => {
  if (!genres || genres.length === 0) return ''
  return genres.slice(0, 3).join(', ')
}

// Initialize component
// Close dropdowns when clicking outside
const closeAllDropdowns = () => {
  showGenreDropdown.value = false
  showYearDropdown.value = false
  showLanguageDropdown.value = false
}

onMounted(async () => {
  initializeFilters()
  await loadGenres()
  await loadMovies(0, false)

  // Add click outside listener for search and dropdowns
  document.addEventListener('click', hideSuggestions)
  document.addEventListener('click', closeAllDropdowns)
})

// Cleanup
onUnmounted(() => {
  document.removeEventListener('click', hideSuggestions)
  document.removeEventListener('click', closeAllDropdowns)
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
.films-page {
  min-height: 100vh;
  background-color: #000000;
  color: #ffffff;
}

/* Search Section */
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
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.search-suggestions::-webkit-scrollbar {
  display: none;
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
  margin-right: 60px;
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

/* Filters Section */
.filters-section {
  background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
  padding: 1rem 2rem 2rem 2rem;
  border-bottom: 1px solid #333333;
}

.filters-content {
  max-width: 1200px;
  margin: 0 auto;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  color: #f5c518;
  font-size: 1rem;
  font-weight: 500;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #333333;
  border-radius: 8px;
  background-color: #1a1a1a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.filter-select:focus {
  border-color: #f5c518;
  box-shadow: 0 2px 8px rgba(245, 197, 24, 0.2);
}

.filter-select option {
  background-color: #1a1a1a;
  color: #ffffff;
}

/* Custom Select Styles - Inspired by suggestion-item */
.custom-select {
  position: relative;
  background-color: #1a1a1a;
  border: 1px solid #333333;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.custom-select.active {
  border-color: #f5c518;
  box-shadow: 0 2px 8px rgba(245, 197, 24, 0.2);
}

.select-display {
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ffffff;
  font-size: 1rem;
}

.select-arrow {
  font-size: 0.8rem;
  color: #cccccc;
  transition: transform 0.3s ease;
}

.custom-select.active .select-arrow {
  transform: rotate(180deg);
  color: #f5c518;
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #1a1a1a;
  border: 1px solid #333333;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  margin-top: 4px;
  /* Hide scrollbar */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.select-dropdown::-webkit-scrollbar {
  display: none;
}

.dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #333333;
  color: #ffffff;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #2a2a2a;
}

.more-item {
  color: #cccccc;
  font-style: italic;
  cursor: default !important;
}

.more-item:hover {
  background-color: transparent !important;
}

/* Movies Section */
.movies-section {
  padding: 3rem 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.movies-grid {
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

/* Responsive Design */
@media (max-width: 1024px) {
  .movies-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .search-section {
    padding: 1.5rem 1rem 0.75rem 1rem;
  }

  .filters-section {
    padding: 0.75rem 1rem 1.5rem 1rem;
  }

  .movies-section {
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

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .movies-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .search-suggestions {
    max-height: 300px;
  }

  .suggestion-item {
    padding: 0.5rem 0.75rem;
  }

  .suggestion-info {
    margin-right: 50px;
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

@media (max-width: 480px) {
  .search-section {
    padding: 1rem 0.5rem 0.5rem 0.5rem;
  }

  .filters-section {
    padding: 0.5rem 0.5rem 1rem 0.5rem;
  }

  .movies-section {
    padding: 1rem 0.5rem;
  }

  .movies-grid {
    grid-template-columns: 1fr;
  }

  .loading-placeholder, .no-data {
    padding: 2rem 1rem;
    font-size: 1rem;
  }
}
</style>
