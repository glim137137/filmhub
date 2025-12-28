<template>
  <nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <span class="brand-text" aria-label="Film Hub homepage">Film Hub</span>
      </div>
      <div class="nav-links" role="list">
        <!-- Admin mode navigation -->
        <template v-if="isAdminMode">
          <router-link to="/admin" class="nav-link" role="listitem" :aria-current="$route.path === '/admin' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin' }">Dashboard</router-link>
          <router-link to="/admin/users" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/users' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/users' }">Users</router-link>
          <router-link to="/admin/films" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/films' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/films' }">Films</router-link>
          <router-link to="/admin/logs" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/logs' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/logs' }">Logs</router-link>
          <span class="admin-badge" role="status" aria-label="Administrator mode active">ADMIN</span>
        </template>

        <!-- Regular user navigation -->
        <template v-else>
          <router-link to="/" class="nav-link" role="listitem" :aria-current="$route.path === '/' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/' }">Home</router-link>
          <router-link to="/films" class="nav-link" role="listitem" :aria-current="$route.path === '/films' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/films' }">Films</router-link>
          <router-link to="/explore" class="nav-link" role="listitem" :aria-current="$route.path === '/explore' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/explore' }">Explore</router-link>
          <router-link to="/about" class="nav-link" role="listitem" :aria-current="$route.path === '/about' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/about' }">About</router-link>
          <router-link v-if="authStore.isAuthenticated" to="/profile" class="nav-link" role="listitem" :aria-current="$route.path === '/profile' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/profile' }">Me</router-link>
        </template>

        <!-- Auth buttons (always show) -->
        <button v-if="authButton.action === 'logout'" @click="handleAuthClick" class="nav-link logout-button" role="listitem" aria-label="Sign out of your account">
          <img src="/log-out.svg" alt="Sign Out" class="logout-icon" aria-hidden="true" />
        </button>
        <router-link v-else :to="authButton.link" class="nav-link" role="listitem" :aria-label="`Navigate to ${authButton.text} page`">{{ authButton.text }}</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Check if we're in admin mode
const isAdminMode = computed(() => {
  return authStore.isAuthenticated && authStore.username === 'admin' && route.path.startsWith('/admin')
})

// Compute the button text and link based on auth state and current route
const authButton = computed(() => {
  if (authStore.isAuthenticated) {
    return {
      text: 'Sign Out',
      action: 'logout'
    }
  } else {
    // Not authenticated - check current route
    if (route.path === '/login') {
      return {
        text: 'Sign Up',
        link: '/register'
      }
    } else if (route.path === '/register') {
      return {
        text: 'Sign In',
        link: '/login'
      }
    } else {
      // Other pages - default to Sign In
      return {
        text: 'Sign In',
        link: '/login'
      }
    }
  }
})

const handleAuthClick = () => {
  if (authButton.value.action === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (authButton.value.link) {
    router.push(authButton.value.link)
  }
}
</script>

<style scoped>
/* Global styles based on design document */
.navbar {
  background-color: #000000;
  border-bottom: 2px solid #333333;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.brand-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ffffff;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.3s ease;
  cursor: pointer;
}

.nav-link:hover {
  color: #f5c518; /* Yellow on hover */
}

.nav-link.router-link-active {
  color: #f5c518;
}

.logout-icon {
  width: 20px;
  height: 20px;
  display: block;
  transition: opacity 0.3s ease;
}

.logout-icon:hover {
  opacity: 0.8;
}

.admin-badge {
  background: #3552b0;
  color: #ffffff;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
  }

  .nav-links {
    gap: 1rem;
  }

  .brand-text {
    font-size: 1.2rem;
  }
}
</style>
