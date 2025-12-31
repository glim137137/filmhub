<template>
  <nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <span class="brand-text" aria-label="Film Hub homepage">Film Hub</span>
      </div>
      <div class="nav-links" role="list">
        <!-- Admin mode navigation -->
        <template v-if="isAdminMode">
          <router-link to="/admin" class="nav-link" role="listitem" :aria-current="$route.path === '/admin' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin' }" aria-label="Dashboard (Alt + 1)">
            <span class="nav-text">Dashboard</span>
            <span class="nav-shortcut">Alt+1</span>
          </router-link>
          <router-link to="/admin/users" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/users' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/users' }" aria-label="Users (Alt + 2)">
            <span class="nav-text">Users</span>
            <span class="nav-shortcut">Alt+2</span>
          </router-link>
          <router-link to="/admin/films" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/films' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/films' }" aria-label="Films (Alt + 3)">
            <span class="nav-text">Films</span>
            <span class="nav-shortcut">Alt+3</span>
          </router-link>
          <router-link to="/admin/logs" class="nav-link" role="listitem" :aria-current="$route.path === '/admin/logs' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/admin/logs' }" aria-label="Logs (Alt + 4)">
            <span class="nav-text">Logs</span>
            <span class="nav-shortcut">Alt+4</span>
          </router-link>
          <span class="admin-badge" role="status" aria-label="Administrator mode active">ADMIN</span>
        </template>

        <!-- Regular user navigation -->
        <template v-else>
          <router-link to="/" class="nav-link" role="listitem" :aria-current="$route.path === '/' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/' }" aria-label="Home (Alt + 1)">
            <span class="nav-text">Home</span>
            <span class="nav-shortcut">Alt+1</span>
          </router-link>
          <router-link to="/films" class="nav-link" role="listitem" :aria-current="$route.path === '/films' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/films' }" aria-label="Films (Alt + 2)">
            <span class="nav-text">Films</span>
            <span class="nav-shortcut">Alt+2</span>
          </router-link>
          <router-link to="/explore" class="nav-link" role="listitem" :aria-current="$route.path === '/explore' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/explore' }" aria-label="Explore (Alt + 3)">
            <span class="nav-text">Explore</span>
            <span class="nav-shortcut">Alt+3</span>
          </router-link>
          <router-link to="/about" class="nav-link" role="listitem" :aria-current="$route.path === '/about' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/about' }" aria-label="About (Alt + 4)">
            <span class="nav-text">About</span>
            <span class="nav-shortcut">Alt+4</span>
          </router-link>
          <router-link v-if="authStore.isAuthenticated" to="/profile" class="nav-link" role="listitem" :aria-current="$route.path === '/profile' ? 'page' : undefined" :class="{ 'router-link-active': $route.path === '/profile' }" aria-label="Profile (Alt + 5)">
            <span class="nav-text">Me</span>
            <span class="nav-shortcut">Alt+5</span>
          </router-link>
        </template>

        <!-- Auth buttons (always show) -->
        <button v-if="authButton.action === 'logout'" @click="handleAuthClick" class="nav-link logout-button" role="listitem" aria-label="Sign out of your account (Alt + 0)">
          <img src="/log-out.svg" alt="Sign Out" class="logout-icon" aria-hidden="true" />
          <span class="nav-shortcut logout-shortcut">Alt+0</span>
        </button>
        <router-link v-else :to="authButton.link" class="nav-link" role="listitem" :aria-label="`Navigate to ${authButton.text} page (Alt + 0)`">
          <span class="nav-text">{{ authButton.text }}</span>
          <span class="nav-shortcut">Alt+0</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter, useRoute } from 'vue-router'
import toastManager from '@/api/toastManager'

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

const handleAuthClick = async () => {
  if (authButton.value.action === 'logout') {
    const confirmed = await toastManager.addConfirm('Are you sure you want to sign out?', {
      confirmText: 'Sign Out',
      cancelText: 'Cancel',
      type: 'warning'
    })

    if (confirmed) {
      authStore.logout()
      router.push('/login')
    }
  } else if (authButton.value.link) {
    router.push(authButton.value.link)
  }
}

// Keyboard navigation handler
const handleKeydown = (event) => {
  // Only handle Alt + number combinations
  if (!event.altKey) return

  const key = event.key

  // Prevent default browser behavior for these shortcuts
  if (['1', '2', '3', '4', '5', '0'].includes(key)) {
    event.preventDefault()
  }

  if (isAdminMode.value) {
    // Admin mode navigation
    switch (key) {
      case '1':
        router.push('/admin')
        break
      case '2':
        router.push('/admin/users')
        break
      case '3':
        router.push('/admin/films')
        break
      case '4':
        router.push('/admin/logs')
        break
      case '0':
        handleAuthClick()
        break
    }
  } else {
    // Regular user navigation
    switch (key) {
      case '1':
        router.push('/')
        break
      case '2':
        router.push('/films')
        break
      case '3':
        router.push('/explore')
        break
      case '4':
        router.push('/about')
        break
      case '5':
        if (authStore.isAuthenticated) {
          router.push('/profile')
        }
        break
      case '0':
        handleAuthClick()
        break
    }
  }
}

// Lifecycle hooks for keyboard event listeners
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
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

/* Keyboard shortcut styles */
.nav-link {
  position: relative;
}

.nav-text {
  display: block;
}

.nav-shortcut {
  font-size: 0.6rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  white-space: nowrap;
  opacity: 0;
  transform: translateY(-2px);
  transition: all 0.2s ease;
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%) translateY(-2px);
}

.nav-link:hover .nav-shortcut {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.logout-button {
  position: relative;
}

.logout-shortcut {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%) translateY(-2px);
  opacity: 0;
  transition: all 0.2s ease;
}

.logout-button:hover .logout-shortcut {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
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

  /* Hide keyboard shortcuts on mobile for cleaner look */
  .nav-shortcut,
  .logout-shortcut {
    display: none;
  }
}
</style>
