import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import ExploreView from '@/views/ExploreView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import TagPostsView from '@/views/TagPostsView.vue'
import FilmDetailView from '@/views/FilmDetailView.vue'
import FilmsView from '@/views/FilmsView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SettingsView from '@/views/SettingsView.vue'
import AdminView from '@/views/AdminView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import AdminUserPostsView from '@/views/AdminUserPostsView.vue'
import AdminUserCommentsView from '@/views/AdminUserCommentsView.vue'
import AdminFilmsView from '@/views/AdminFilmsView.vue'
import AdminFilmAddView from '@/views/AdminFilmAddView.vue'
import AdminLogsView from '@/views/AdminLogsView.vue'
import AdminUserLogsView from '@/views/AdminUserLogsView.vue'
import { useAuthStore } from '@/stores/auth.js'
import toastManager from '@/api/toastManager.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    // Always scroll to top for new routes
    return { top: 0, left: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/explore',
      name: 'explore',
      component: ExploreView,
      meta: { requiresAuth: true }
    },
    {
      path: '/explore/tag/:tag',
      name: 'explore-tag',
      component: TagPostsView,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/films',
      name: 'films',
      component: FilmsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/films/:id',
      name: 'film-detail',
      component: FilmDetailView,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: AdminUsersView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users/:userId/posts',
      name: 'admin-user-posts',
      component: AdminUserPostsView,
      props: true,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users/:userId/comments',
      name: 'admin-user-comments',
      component: AdminUserCommentsView,
      props: true,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users/:userId/logs',
      name: 'admin-user-logs',
      component: AdminUserLogsView,
      props: true,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/films',
      name: 'admin-films',
      component: AdminFilmsView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/films/add',
      name: 'admin-film-add',
      component: AdminFilmAddView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/logs',
      name: 'admin-logs',
      component: AdminLogsView,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ],
})

// Navigation guard for authentication and admin access
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth state if not already done
  authStore.initializeAuth()

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    // Check if token exists and is not expired
    if (!authStore.token || authStore.isTokenExpired()) {
      // Clear invalid token
      if (authStore.token && authStore.isTokenExpired()) {
        authStore.logout()
        toastManager.showWarning('Login expired, please login again')
      }
      // Only allow login/register pages when not authenticated
      if (to.name !== 'login' && to.name !== 'register') {
        next({ name: 'login' })
        return
      }
    }
  }

  // Check if route requires admin access
  if (to.meta.requiresAdmin && authStore.username !== 'admin') {
    // Redirect to home if not admin
    next({ name: 'home' })
    return
  }

  // If user is authenticated and trying to access login/register, redirect to home
  if (authStore.isAuthenticated && !authStore.isTokenExpired() &&
      (to.name === 'login' || to.name === 'register')) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
