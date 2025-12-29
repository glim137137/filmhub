<template>
    <div class="tag-posts">
      <div class="tag-header">
        <h1 class="tag-name">{{ tag }}</h1>
      </div>
      <PostsListRegular
        :posts="posts"
        :loading="loading"
        :has-more-posts="hasMorePosts"
        :loading-more="loadingMore"
        :empty-message="'No posts for this tag'"
        :context="'tag'"
        :context-value="tag"
        @load-more="loadMorePosts"
        @post-updated="onPostUpdated"
        @post-deleted="onPostDeleted"
        @post-created="onPostCreated"
        class="posts-list-component"
      />
    </div>

    <!-- Toast Component -->
    <Toast ref="toastRef" />
  </template>
  
  <script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth.js'
import PostsListRegular from '@/components/PostsListRegular.vue'
import Toast from '@/components/Toast.vue'
  
  const route = useRoute()
  // Decode route param (may be percent-encoded in the URL)
  const tag = decodeURIComponent(route.params.tag || '')
  const tagId = ref(null) // Store the tag ID after lookup
  const posts = ref([])
  const loading = ref(false)
  const loadingMore = ref(false)
const hasMorePosts = ref(true)
const currentPage = ref(0)
const pageSize = 10 // Number of posts to load per page
const authStore = useAuthStore()

// Toast component reference
const toastRef = ref(null)
  
  // Get tag ID by name
  const getTagId = async (tagName) => {
    try {
      const res = await http.get('/tags')
      const tags = res?.data?.tags || res?.tags || []
      console.log('Available tags:', tags)
      console.log('Searching for tag name:', tagName, 'type:', typeof tagName)
      const foundTag = tags.find(t => {
        console.log('Comparing', t.name, '===', tagName, 'result:', t.name === tagName)
        return t.name === tagName
      })
      console.log('Found tag for', tagName, ':', foundTag)
      // Backend returns tag_id, not id
      return foundTag && foundTag.tag_id ? foundTag.tag_id : null
    } catch (err) {
      console.error('Failed to get tag ID', err)
      return null
    }
  }

  // Event handlers for PostsList component
  const onPostUpdated = (post) => {
    // Post has been updated (liked/unliked), no need to do anything
    // as the component handles local state updates
    console.log('Post updated:', post.post_id)
  }

  const onPostDeleted = (post) => {
    // Remove post from local state
    posts.value = posts.value.filter(p => p.post_id !== post.post_id)
    console.log('Post deleted:', post.post_id)
  }

  const onPostCreated = (postData) => {
    // Refresh posts list after new post is created
    console.log('Post created:', postData)
    // Optionally reload the posts to show the new post
    loadPosts(0, false)
  }

  // Load posts data
  const loadPosts = async (page = 0, append = false) => {
    if (page === 0) {
      loading.value = true
    } else {
      loadingMore.value = true
    }

    try {
      // Validate tag parameter first
      if (!tag || tag.trim() === '') {
        console.error('No tag specified in route')
        return
      }

      // Get tag ID if not already cached
      if (tagId.value === null) {
        tagId.value = await getTagId(tag)
        if (!tagId.value) {
          console.error('Tag not found:', tag)
          return
        }
      }

      // Ensure tagId.value is valid before making API call
      if (!tagId.value) {
        console.error('Invalid tag ID:', tagId.value)
        return
      }

      console.log('Making API call to:', `/tags/${tagId.value}/posts`)
      const res = await http.post(`/tags/${tagId.value}/posts`, {
        page: page,
        page_size: pageSize
      })
      const newPosts = res?.data?.posts || res?.posts || []
      const hasMore = res?.data?.has_more || false

      if (append) {
        posts.value.push(...newPosts)
      } else {
        posts.value = newPosts
      }

      // Initialize empty comments array for new posts (comments will be loaded on demand)
      newPosts.forEach(post => {
        if (!post.comments) post.comments = []
      })

      // Update pagination status
      hasMorePosts.value = hasMore
      currentPage.value = page

      // Initialize like status (only for newly loaded posts)
      newPosts.forEach(p => {
        if (p.is_like || p.isLike || p.has_liked) {
          activeButtons.value.add(`like:${p.post_id}`)
        }
      })

    } catch (err) {
      console.error('Failed to load tag posts', err)
    } finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  // Load more posts
  const loadMorePosts = async () => {
    if (!hasMorePosts.value || loadingMore.value) return
    await loadPosts(currentPage.value + 1, true)
  }
  
  // Watch for route changes
  watch(() => route.params.tag, (newTag) => {
    if (newTag) {
      console.log('Route tag changed:', newTag)
      // Reset tagId when route changes
      tagId.value = null
      loadPosts()
    }
  })

  onMounted(() => {
    console.log('Component mounted, route params:', route.params)
    loadPosts(0, false) // Initial load of first page
  })
  </script>
  
  <style scoped>
   .tag-header .tag-name {
    font-size: 1.8rem;
    margin-bottom: 0.25rem;
    position: relative;
    padding-left: 20px;
   }
   .tag-header .tag-name::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 5px;
    background-color: #f5c518;
    border-radius: 3px;
   }
  .tag-header {
    padding: 2rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
    padding-bottom: 0;
  }

  .tag-name {
    font-size: 1.8rem;
    margin-bottom: 0.25rem;
    position: relative;
    padding-left: 20px;
  }
  .tag-name::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 5px;
    background-color: #f5c518;
    border-radius: 3px;
  }

  .posts-list-component {
    margin-top: 0;
    padding-top: 0;
  }
  
  </style>