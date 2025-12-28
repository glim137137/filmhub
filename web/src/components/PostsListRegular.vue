<template>
  <div class="posts-list">
    <div class="posts-container">
      <!-- Sorting Buttons - responsive positioning -->
      <div v-if="posts.length > 0" class="sorting-buttons-fixed">
        <button
          :class="['sort-btn time-btn', { active: currentSortBy === 'time' }]"
          @click="setSortBy('time')"
          title="Sort by time"
        >
          Time {{ currentSortBy === 'time' ? (currentSortOrder === 'desc' ? '↓' : '↑') : '' }}
        </button>
        <button
          :class="['sort-btn heat-btn', { active: currentSortBy === 'likes' }]"
          @click="setSortBy('likes')"
          title="Sort by likes"
        >
          Heat {{ currentSortBy === 'likes' ? (currentSortOrder === 'desc' ? '↓' : '↑') : '' }}
        </button>
      </div>

      <div v-if="loading" class="loading">Loading posts...</div>
      <div v-else>
        <div v-if="posts.length === 0" class="no-data">{{ emptyMessage }}</div>
        <ul class="post-list">
          <li v-for="post in sortedPosts" :key="post.post_id" class="post-item">
            <div class="post-head">
              <img
                :src="post.user_info?.avatar_url ? '/avatars/' + post.user_info.avatar_url : '/anonymous.png'"
                :alt="post.user_info?.username ? (post.user_info.username + ' avatar') : 'Anonymous avatar'"
                class="avatar"
                @error="onImgError"
              />
              <div class="post-info">
                <div class="user-meta">
                  <div class="username">{{ post.user_info?.username || 'Unknown' }}</div>
                  <div class="timestamp">{{ formatTimestamp(post.created_at) }}</div>
                </div>
                <div v-if="post.tags && post.tags.length > 0" class="post-tags">
                  <span
                    v-for="tag in post.tags.slice(0, 3)"
                    :key="tag"
                    class="post-tag"
                  >
                    #{{ tag }}
                  </span>
                  <span v-if="post.tags.length > 3" class="post-tag-more">
                    +{{ post.tags.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
            <div class="post-title-container">
            <h3 class="post-title">{{ post.title }}</h3>
            </div>
            <p class="post-content">{{ post.content }}</p>
            <div class="post-actions">
              <button :class="['action-btn','reply-btn', { active: activeButtons.has(`reply:${post.post_id}`) }]" @click="toggleCommentsArea(post)" aria-label="Reply">
                <img src="/message-square.svg" alt="Reply" class="icon" />
              </button>
              <span class="comment-count">{{ post.comment_count || 0 }}</span>
              <button :class="['action-btn','like-btn', { active: activeButtons.has(`like:${post.post_id}`) }]" @click="onLike(post)" aria-label="Like">
                <img src="/thumbs-up.svg" alt="Like" class="icon" />
              </button>
              <span class="like-count">{{ post.like_count || 0 }}</span>
              <button v-if="canDelete(post)" class="action-btn delete-btn" @click="onDelete(post)" aria-label="Delete">
                <img src="/trash.svg" alt="Delete" class="icon" />
              </button>
            </div>
            <!-- Comment input area -->
            <div v-if="openReplies[post.post_id]" class="comment-area">
              <textarea v-model="newCommentText[post.post_id]" class="comment-input" rows="3" placeholder="Write a comment..."></textarea>
              <div class="comment-actions">
                <button class="action-btn submit-comment" @click="submitComment(post)">Submit</button>
              </div>
            </div>
            <div v-if="openReplies[post.post_id]" class="comments">
              <div v-if="loadingComments.has(post.post_id)" class="loading-comments">
                Loading comments...
              </div>
              <div v-else-if="visibleComments(post).length === 0 && openReplies[post.post_id]" class="no-comments">
                No comments yet
              </div>
              <div v-for="(c, idx) in visibleComments(post)" :key="c.comment_id" class="comment">
                <img
                  :src="c.user_info?.avatar_url ? '/avatars/' + c.user_info.avatar_url : '/anonymous.png'"
                  :alt="c.user_info?.username ? (c.user_info.username + ' avatar') : 'Anonymous avatar'"
                  class="avatar-sm"
                  @error="onImgError"
                />
                <div class="comment-body">
                  <div class="comment-user">
                    <div class="comment-user-left">
                      <div class="comment-username-text">{{ c.user_info?.username || 'Unknown' }}</div>
                      <div class="comment-timestamp">{{ formatTimestamp(c.created_at) }}</div>
                    </div>
                    <button v-if="isCommentAuthor(c)" class="comment-delete-btn" @click="deleteComment(post, c)" aria-label="Delete comment">
                      <img src="/trash.svg" alt="Delete" class="icon" />
                    </button>
                  </div>
                  <div class="comment-text">{{ c.content }}</div>
                </div>
              </div>
            </div>
          </li>
        </ul>
        <!-- Load more button -->
        <div v-if="hasMorePosts && posts.length > 0" class="load-more-container">
          <button
            class="load-more-btn"
            @click="loadMorePosts"
            :disabled="loadingMore"
            :class="{ loading: loadingMore }"
          >
            {{ loadingMore ? 'Loading...' : 'Load More Posts' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Create Post Button -->
    <button class="floating-create-btn" @click="openCreatePostModal" aria-label="Create Post">
      <img src="/message-circle.svg" alt="Create Post" class="create-icon" />
    </button>

    <!-- Create Post Modal -->
    <div v-if="showCreatePostModal" class="create-post-modal-overlay" @click="closeCreatePostModal">
      <div class="create-post-modal" @click.stop>
        <h3 class="create-post-modal-title">Create New Post</h3>
        <form @submit.prevent="submitPost" class="create-post-form">
          <div class="form-group">
            <label for="post-title" class="form-label">Title</label>
            <input
              id="post-title"
              v-model="newPost.title"
              type="text"
              class="form-input"
              placeholder="Enter post title..."
              required
            />
          </div>
          <div class="form-group">
            <label for="post-content" class="form-label">Content</label>
            <textarea
              id="post-content"
              v-model="newPost.content"
              class="form-textarea"
              rows="4"
              placeholder="Write your post content..."
              required
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Tags</label>

            <!-- Display added tags -->
            <div v-if="newPost.tags.length > 0" class="tags-display">
              <span
                v-for="tag in newPost.tags"
                :key="tag.name"
                class="tag-chip"
                :class="{ 'default-tag': tag.isDefault }"
              >
                {{ tag.name }}
                <button
                  v-if="!tag.isDefault"
                  type="button"
                  class="tag-remove-btn"
                  @click="removeTag(tag.name)"
                  aria-label="Remove tag"
                >
                  ×
                </button>
              </span>
            </div>

            <!-- Add tag input -->
            <div class="tag-input-group">
              <input
                id="tag-input"
                v-model="currentTagInput"
                type="text"
                class="tag-input"
                placeholder="Enter a tag..."
                @keydown.enter.prevent="addTag"
              />
              <button
                type="button"
                class="add-tag-btn"
                @click="addTag"
                :disabled="!currentTagInput.trim()"
              >
                +
              </button>
            </div>
          </div>
          <div class="create-post-modal-actions">
            <button type="button" class="cancel-btn" @click="closeCreatePostModal">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="isSubmittingPost">
              {{ isSubmittingPost ? 'Creating...' : 'Create Post' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth.js'
import toastManager from '@/api/toastManager'

// Props
const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  hasMorePosts: {
    type: Boolean,
    default: true
  },
  loadingMore: {
    type: Boolean,
    default: false
  },
  emptyMessage: {
    type: String,
    default: 'No posts available'
  },
  // Context for default tags
  context: {
    type: String,
    default: '' // 'tag' for tag posts, 'film' for film posts
  },
  contextValue: {
    type: String,
    default: '' // tag name or film title
  }
})

// Emits
const emit = defineEmits(['load-more', 'post-updated', 'post-deleted', 'post-created', 'sort-changed'])

const authStore = useAuthStore()
console.log('PostsListRegular initialized, authStore:', {
  userId: authStore.userId,
  user: authStore.user
})

const activeButtons = ref(new Set()) // Store keys like "like:123", "reply:123"
const openReplies = ref({})
const newCommentText = ref({})
const loadingComments = ref(new Set()) // Track which posts are loading comments

// Create post modal state
const showCreatePostModal = ref(false)
const isSubmittingPost = ref(false)
const currentTagInput = ref('')
const newPost = ref({
  title: '',
  content: '',
  tags: [] // Array of {name: string, isDefault: boolean}
})

// Sorting state
const currentSortBy = ref('time') // 'time' or 'likes'
const currentSortOrder = ref('desc') // 'asc' or 'desc'

// Helper functions using global toast manager
const showToast = (message, type = 'info', duration = 3000) => {
  return toastManager.addToast(message, type, duration)
}

const showConfirm = async (message, options = {}) => {
  return await toastManager.addConfirm(message, options)
}

// Computed property: current user ID
const currentUserId = computed(() => {
  const result = authStore.userId?.value || authStore.user?.id || null
  console.log('currentUserId computed:', {
    authStoreUserId: authStore.userId,
    authStoreUserIdValue: authStore.userId?.value,
    authStoreUser: authStore.user,
    authStoreUserId: authStore.user?.id,
    result
  })
  return result
})

// Computed property: sorted posts
const sortedPosts = computed(() => {
  const posts = [...props.posts] // Create a copy to avoid mutating props

  return posts.sort((a, b) => {
    let comparison = 0

    if (currentSortBy.value === 'time') {
      // Sort by creation time
      const timeA = new Date(a.created_at || 0).getTime()
      const timeB = new Date(b.created_at || 0).getTime()
      comparison = timeA - timeB
    } else if (currentSortBy.value === 'likes') {
      // Sort by like count
      const likesA = a.like_count || 0
      const likesB = b.like_count || 0
      comparison = likesA - likesB
    }

    // Apply sort order
    return currentSortOrder.value === 'desc' ? -comparison : comparison
  })
})

// Load comments for a single post (on demand)
const loadCommentsForPost = async (post) => {
  const postId = post.post_id

  console.log(`loadCommentsForPost called for post ${postId}`)
  console.log(`post.comments:`, post.comments)
  console.log(`post.commentsLoaded:`, post.commentsLoaded)
  console.log(`loadingComments.has(${postId}):`, loadingComments.value.has(postId))

  // Skip if currently loading
  if (loadingComments.value.has(postId)) {
    console.log(`Comments for post ${postId} are currently loading`)
    return // Currently loading
  }

  // Skip if comments are already loaded (check if it's not just the initial empty array)
  // We use a special property to track if comments have been loaded
  if (post.commentsLoaded) {
    console.log(`Comments for post ${postId} already loaded`)
    return // Comments already loaded
  }

  console.log(`Loading comments for post ${postId}...`)
  loadingComments.value.add(postId)

  try {
    const res = await http.get(`/posts/${postId}/comments`)
    console.log('Comments API response:', res)
    // After http interceptor, res should be the data field (comments array)
    const comments = res.data
    post.comments = comments
    post.commentsLoaded = true // Mark as loaded
    console.log(`Successfully loaded ${comments.length} comments for post ${postId}`)
  } catch (err) {
    console.error(`Failed to load comments for post ${postId}:`, err)
    post.comments = [] // Set empty array on error
    post.commentsLoaded = true // Even on error, mark as loaded to avoid retrying
  } finally {
    loadingComments.value.delete(postId)
    console.log(`Finished loading comments for post ${postId}`)
  }
}

// UI operation: toggle comment area
const toggleCommentsArea = async (post) => {
  const id = post.post_id
  const wasOpen = openReplies.value[id]
  openReplies.value[id] = !openReplies.value[id]
  const key = `reply:${id}`
  if (activeButtons.value.has(key)) activeButtons.value.delete(key)
  else activeButtons.value.add(key)
  // Ensure there is an array for newCommentText
  if (!newCommentText.value[id]) newCommentText.value[id] = ''

  // Load comments when opening the reply area for the first time
  if (!wasOpen && openReplies.value[id]) {
    console.log('Opening reply area for post', id, 'loading comments...')
    await loadCommentsForPost(post)
    console.log('Comments loaded for post', id, 'comments:', post.comments)
  }
}

// Submit comment (local update)
const submitComment = async (post) => {
  const id = post.post_id
  const content = (newCommentText.value[id] || '').trim()
  if (!content) {
    showToast('Please enter a comment', 'warning')
    return
  }

  try {
    const res = await http.post(`/posts/${id}/comments`, { content })
    console.log('Comment submission response:', res)

    // After http interceptor, res should be Result structure: { code, msg, data: { comment: {...} } }
    const commentObj = res?.data?.comment

    console.log('Extracted comment object:', commentObj)

    // Ensure post has comments array
    if (!post.comments) post.comments = []

    if (commentObj && commentObj.comment_id) {
      // Use complete comment object returned by backend
      post.comments = [...post.comments, commentObj]
      // Update comment count
      post.comment_count = (post.comment_count || 0) + 1
      console.log('Comment added to post, new comments length:', post.comments.length, 'comment_count:', post.comment_count)
    } else {
      console.warn('No valid comment object received, using fallback')
      // Fallback: create a basic comment object
      const fallbackComment = {
        comment_id: Date.now(),
        user_id: currentUserId.value,
        user_info: {
          username: authStore.user?.username || 'You',
          avatar_url: authStore.user?.avatar_url || null
        },
        content,
        created_at: new Date().toISOString()
      }
      post.comments.push(fallbackComment)
      // Update comment count even for fallback
      post.comment_count = (post.comment_count || 0) + 1
      console.log('Fallback comment added, new comments length:', post.comments.length, 'comment_count:', post.comment_count)
    }

    // Clear input field
    newCommentText.value[id] = ''
  } catch (err) {
    console.error('Failed to submit comment', err)
    showToast('Failed to submit comment', 'error')
  }
}

// Check if user can delete post
const canDelete = (post) => {
  return currentUserId.value && Number(currentUserId.value) === Number(post.user_id)
}

const onImgError = (e) => {
  try {
    e.target.src = '/anonymous.png'
  } catch (err) {
    /* ignore */
  }
}

const visibleComments = (post) => {
  return post?.comments || []
}

// Extract post data from response (optimized)
const extractPostFromRes = (res) => {
  if (!res) return null
  const payload = res.data ?? res
  if (!payload) return null

  // Prioritize post in data
  if (payload.data?.post) return payload.data.post
  if (payload.data) return payload.data
  if (payload.post) return payload.post
  return payload
}

// Like/unlike operation (local update)
const onLike = async (post) => {
  const id = post.post_id
  const key = `like:${id}`
  const isActive = activeButtons.value.has(key)

  try {
    let res
    if (isActive) {
      // Unlike
      res = await http.delete('/posts/like', { data: { post_id: id } })
      activeButtons.value.delete(key)
      post.like_count = Math.max(0, (post.like_count || 1) - 1)
    } else {
      // Like
      res = await http.post(`/posts/${id}/like`)
      activeButtons.value.add(key)
      post.like_count = (post.like_count || 0) + 1
    }

    // If backend returns updated post data, use it to update local state
    const updated = extractPostFromRes(res)
    if (updated && updated.post_id === id) {
      Object.assign(post, updated)
    }

    // Emit post updated event
    emit('post-updated', post)
  } catch (err) {
    console.error('Failed to like/unlike post', err)
    showToast('Failed to update like', 'error')
  }
}

// Delete post (local update)
const onDelete = async (post) => {
  const confirmed = await showConfirm('Delete this post?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  if (!confirmed) return

  try {
    await http.delete('/posts', { data: { post_id: post.post_id } })
    emit('post-deleted', post)
    showToast('Post deleted successfully', 'success')
  } catch (err) {
    console.error('Failed to delete post', err)
    showToast('Failed to delete post', 'error')
  }
}

// Check if user is comment author
const isCommentAuthor = (comment) => {
  const result = currentUserId.value && Number(currentUserId.value) === Number(comment.user_id)
  console.log('isCommentAuthor check:', {
    currentUserId: currentUserId.value,
    commentUserId: comment.user_id,
    result
  })
  return result
}

// Delete comment (local update)
const deleteComment = async (post, comment) => {
  console.log('deleteComment called with:', { postId: post.post_id, commentId: comment.comment_id })

  const confirmed = await showConfirm('Delete this comment?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  console.log('User confirmation:', confirmed)
  if (!confirmed) return

  try {
    console.log('Making API call to delete comment:', comment.comment_id)
    await http.delete(`/comments/${comment.comment_id}`)
    console.log('API call successful')

    // Remove comment from local state
    const beforeCount = post.comments?.length || 0
    post.comments = (post.comments || []).filter(c => c.comment_id !== comment.comment_id)
    const afterCount = post.comments?.length || 0
    console.log(`Removed comment from local state: ${beforeCount} -> ${afterCount}`)

    // Update comment count
    const beforeCommentCount = post.comment_count || 0
    post.comment_count = Math.max(0, (post.comment_count || 1) - 1)
    console.log(`Updated comment count: ${beforeCommentCount} -> ${post.comment_count}`)

    showToast('Comment deleted successfully', 'success')
  } catch (err) {
    console.error('Failed to delete comment', err)
    showToast('Failed to delete comment', 'error')
  }
}

// Load more posts
const loadMorePosts = () => {
  emit('load-more')
}

// Sorting functions
const setSortBy = (sortType) => {
  if (currentSortBy.value === sortType) {
    // If clicking the same sort type, toggle order
    currentSortOrder.value = currentSortOrder.value === 'desc' ? 'asc' : 'desc'
  } else {
    // If clicking different sort type, set it and default to desc
    currentSortBy.value = sortType
    currentSortOrder.value = 'desc'
  }
  // Emit sort changed event for parent component
  emit('sort-changed', { sortBy: currentSortBy.value, sortOrder: currentSortOrder.value })
}

// Create post functions
const openCreatePostModal = () => {
  initializeDefaultTags()
  showCreatePostModal.value = true
}

const closeCreatePostModal = () => {
  showCreatePostModal.value = false
  newPost.value = {
    title: '',
    content: '',
    tags: []
  }
  currentTagInput.value = ''
}

const submitPost = async () => {
  if (isSubmittingPost.value) return

  const title = newPost.value.title.trim()
  const content = newPost.value.content.trim()

  if (!title || !content) {
    showToast('Please fill in both title and content', 'warning')
    return
  }

  try {
    isSubmittingPost.value = true

    // Extract tag names from tags array
    const tags = newPost.value.tags.map(tag => tag.name)

    const postData = {
      title,
      content,
      tags
    }

    const res = await http.post('/posts', postData)
    console.log('Post creation response:', res)

    // Close modal and reset form
    closeCreatePostModal()

    // Emit post created event
    emit('post-created', postData)

    // Optional: Show success message
    showToast('Post created successfully!', 'success')

  } catch (error) {
    console.error('Failed to create post:', error)
    showToast('Failed to create post. Please try again.', 'error')
  } finally {
    isSubmittingPost.value = false
  }
}

// Tag management functions
const addTag = () => {
  const tagName = currentTagInput.value.trim()
  if (!tagName) return

  // Check if tag already exists
  if (newPost.value.tags.some(tag => tag.name === tagName)) {
    showToast('Tag already added', 'warning')
    return
  }

  // Add tag
  newPost.value.tags.push({
    name: tagName,
    isDefault: false
  })

  // Clear input
  currentTagInput.value = ''
}

const removeTag = (tagName) => {
  newPost.value.tags = newPost.value.tags.filter(tag => tag.name !== tagName)
}

// Initialize default tags when modal opens
const initializeDefaultTags = () => {
  newPost.value.tags = []

  if (props.context === 'tag' && props.contextValue) {
    // For tag posts, add the tag as default
    newPost.value.tags.push({
      name: props.contextValue,
      isDefault: true
    })
  } else if (props.context === 'film' && props.contextValue) {
    // For film posts, add the film title as default tag
    newPost.value.tags.push({
      name: props.contextValue,
      isDefault: true
    })
  }
}

const formatTimestamp = (ts) => {
  if (!ts) return ''
  try {
    let s = String(ts)
    // Replace T with space
    s = s.replace('T', ' ')
    // Remove fractional seconds like .593545
    s = s.replace(/\.\d+/, '')
    // Remove trailing Z if present
    s = s.replace(/Z$/, '')
    return s
  } catch (err) {
    return ts
  }
}
</script>

<style scoped>
.post-list { list-style:none; padding:0; margin:0; display:block; padding-left:20px; }
.post-item {
    padding:1rem 0;
    color:#fff;
    border-radius:0;
}
/* Apply 2px white separator except last item */
.post-item:not(:last-child) {
  border-bottom: 2px solid #ffffff;
}
.post-head {
  display:flex;
  gap:0.75rem;
  align-items:flex-start;
  margin-bottom: 0.75rem; /* Space between user info and title */
}

.post-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.post-tags {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.post-tag {
  font-size: 0.7rem;
  color: #f5c518;
  background-color: rgba(245, 197, 24, 0.1);
  padding: 0.125rem 0.375rem;
  border-radius: 8px;
  font-weight: 500;
}

.post-tag-more {
  font-size: 0.7rem;
  color: #888888;
  font-weight: 500;
}
.avatar { width:48px; height:48px; border-radius:50%; object-fit:cover; }
.post-title {
  margin: 0 0 0.5rem 0; /* Spacing between title and content */
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}
.post-content {
  margin: 0 0 0.5rem 0;
  color: #ddd;
  line-height: 1.5;
}
.comment-area { margin-top: 0.5rem; display:flex; flex-direction:column; gap:0.5rem; }
.comment-input {
  width: 100%;
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #333333;
  border-radius: 25px;
  background-color: #1a1a1a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  max-width: 100%;
  resize: vertical;
}
.comment-input:focus { border-color: #f5c518; }
.comment-actions { display:flex; gap:0.5rem; justify-content:flex-end; }
.submit-comment { background:#3552b0; color:#fff; padding:0.5rem 0.75rem; border-radius:6px; border:none; cursor:pointer; }
.comment-count {color:#ccc; font-weight:500; }
.avatar-sm { width:32px; height:32px; border-radius:50%; object-fit:cover; }
.username { font-weight:700; }
.timestamp { color:#888; font-size:0.85rem; }
.comment { display:flex; gap:0.5rem; margin-top:0.5rem; }
.comment-body { color:#ddd; }
.comment-timestamp { color:#888; font-size:0.8rem; margin-top:0.125rem; }
.post-actions { display:flex; gap:0.5rem; margin-top:0.5rem; align-items:center; }
.action-btn { background: transparent; border: none; padding: 0.25rem; cursor: pointer; display: inline-flex; align-items: center; }
.action-btn .icon { width:20px; height:20px; display:block; }
.action-btn:hover { opacity: 0.9; transform: translateY(-1px); }
.like-count {color:#ccc; font-weight:500; }
.comment-user { display:flex; justify-content:space-between; align-items:flex-start; gap:0.75rem; }
.comment-user-left { display:flex; flex-direction:column; }
.comment-username-text { font-weight:700; color:#fff; }

.comment-delete-btn { background: transparent; border: none; padding: 0; cursor: pointer; display: inline-flex; align-items: center; }
.comment-delete-btn .icon { width:20px; height:20px; }

.action-btn:hover .icon,
.action-btn.active .icon,
.action-btn.liked .icon,
.comment-delete-btn:hover .icon {
  filter: invert(69%) sepia(89%) saturate(749%) hue-rotate(358deg) brightness(101%) contrast(101%);
}

.floating-create-btn:hover .create-icon {
  filter: invert(69%) sepia(89%) saturate(749%) hue-rotate(358deg) brightness(101%) contrast(101%);
}
.like-btn.active,
.like-btn.liked {
  color: #f5c518;
}
.submit-comment:hover { text-decoration: underline; }
.loading-comments {
  color: #888;
  font-style: italic;
  padding: 0.5rem 0;
  text-align: center;
}
.no-comments {
  color: #888;
  font-style: italic;
  padding: 0.5rem 0;
  text-align: center;
}
.posts-list {
  padding: 2rem;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}
.posts-list { font-family: Verdana, Geneva, sans-serif; }

/* Load more button styles */
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

.loading {
  color: #f5c518;
  text-align: center;
  padding: 2rem;
}

.no-data {
  color: #cccccc;
  text-align: center;
  padding: 2rem;
}

/* Sorting Buttons - Fixed at bottom right on desktop, below title on mobile */
.sorting-buttons-fixed {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

/* Desktop: fixed positioning */
@media (min-width: 769px) {
  .sorting-buttons-fixed {
    position: fixed;
    bottom: 7rem; /* Above the create post button */
    right: 2rem;
    z-index: 99; /* Below create post button */
  }
}

.sort-btn {
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.time-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.time-btn:hover {
  background-color: #2a4193;
  transform: translateY(-1px);
}

.time-btn.active {
  background-color: #3552b0;
  box-shadow: 0 0 0 2px rgba(53, 82, 176, 0.3);
}

.heat-btn {
  background-color: #F5C518;
  color: #000000;
}

.heat-btn:hover {
  background-color: #e6b800;
  transform: translateY(-1px);
}

.heat-btn.active {
  background-color: #d4a017;
  box-shadow: 0 0 0 2px rgba(245, 197, 24, 0.3);
}

/* Floating Create Post Button */
.floating-create-btn {
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
  box-shadow: 0 4px 12px rgba(53, 82, 176, 0.3);
  transition: all 0.3s ease;
  z-index: 100;
}

.floating-create-btn:hover {
  background: #2a4193;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(53, 82, 176, 0.4);
}

.create-icon {
  width: 24px;
  height: 24px;
}

/* Create Post Modal */
.create-post-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.create-post-modal {
  background-color: #1a1a1a;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 82vh;
  /* Hide scrollbar */
  scrollbar-width: none;
  -ms-overflow-style: none;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.create-post-modal::-webkit-scrollbar {
  display: none;
}

.create-post-modal-title {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1.5rem;
}

.create-post-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
  min-height: 120px;
}

.create-post-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 2rem;
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
  min-width: 80px;
}

.cancel-btn {
  background-color: #333333;
  color: #cccccc;
}

.cancel-btn:hover {
  background-color: #444444;
  color: #ffffff;
  transform: translateY(-1px);
}

.submit-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2a4193;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background-color: #555555;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Tags Styles */
.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background-color: #0a0a0a;
  border-radius: 6px;
  border: 1px solid #333333;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: #3552b0;
  color: #ffffff;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.tag-chip.default-tag {
  background-color: #f5c518;
  color: #000000;
}

.tag-remove-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 1.2em;
  line-height: 1;
  padding: 0;
  margin-left: 0.25rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.tag-remove-btn:hover {
  opacity: 1;
}

.tag-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.tag-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 2px solid #333333;
  border-radius: 6px;
  background-color: #0a0a0a;
  color: #ffffff;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.tag-input:focus {
  border-color: #f5c518;
}

.add-tag-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #3552b0;
  color: #ffffff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
  font-weight: bold;
  transition: all 0.3s ease;
}

.add-tag-btn:hover:not(:disabled) {
  background-color: #2a4193;
  transform: scale(1.1);
}

.add-tag-btn:disabled {
  background-color: #555555;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Mobile: below title positioning */
@media (max-width: 768px) {
  .sorting-buttons-fixed {
    flex-direction: row;
    justify-content: center;
    margin: 1rem 0;
  }

  .sort-btn {
    min-width: 70px;
    font-size: 0.8rem;
    flex: 1;
    max-width: 120px;
  }

  .create-post-modal {
    padding: 1.5rem;
    max-height: 70vh;
  }

  .tags-display {
    padding: 0.5rem;
  }

  .tag-chip {
    font-size: 0.75rem;
    padding: 0.2rem 0.4rem;
  }

  .tag-input-group {
    gap: 0.25rem;
  }

  .tag-input {
    padding: 0.4rem 0.6rem;
    font-size: 0.85rem;
  }

  .add-tag-btn {
    width: 28px;
    height: 28px;
    font-size: 1em;
  }
}
</style>
