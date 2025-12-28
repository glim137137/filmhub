<template>
  <div class="posts-list">
    <!-- User comments mode -->
    <div v-if="mode === 'comments'">
      <div v-if="loading" class="loading">Loading your comments...</div>
      <div v-else>
        <div v-if="comments.length === 0" class="no-data">{{ emptyMessage }}</div>
        <ul v-else class="post-list">
          <li class="post-item user-comment" v-for="comment in comments" :key="comment.comment_id">
            <div class="post-head">
              <img
                :src="comment.user_info?.avatar_url ? '/avatars/' + comment.user_info.avatar_url : '/anonymous.png'"
                :alt="comment.user_info?.username ? (comment.user_info.username + ' avatar') : 'Anonymous avatar'"
                class="avatar"
                @error="onImgError"
              />
              <div class="post-info">
                <div class="user-meta">
                  <div class="username">{{ comment.user_info?.username || 'Unknown' }}</div>
                  <div class="timestamp">{{ formatTimestamp(comment.created_at) }}</div>
                </div>
                <div class="post-tags">
                  <span class="post-tag" @click="viewPost && viewPost(comment.post_id)">
                    On post: {{ comment.post_title || 'Unknown Post' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="comment-content">
              <template v-if="editingComment === comment.comment_id">
                <textarea
                  v-model="editCommentData.content"
                  class="edit-input edit-comment-content"
                  placeholder="Comment content..."
                  rows="2"
                ></textarea>
              </template>
              <template v-else>
                {{ comment.content }}
              </template>
            </div>
            <div class="post-actions">
              <template v-if="editingComment === comment.comment_id">
                  <button class="action-btn save-btn" @click="saveEditedComment" aria-label="Save Comment">
                    Save
                  </button>
                  <button class="action-btn cancel-btn" @click="cancelEditComment" aria-label="Cancel Edit">
                    Cancel
                  </button>
              </template>
              <template v-else>
                <button class="action-btn edit-btn" @click="editCommentFromUser(comment)" aria-label="Edit comment">
                  <img src="/edit.svg" alt="Edit" class="icon" />
                </button>
                <button class="action-btn delete-btn" @click="deleteCommentFromUser(comment)" aria-label="Delete comment">
                  <img src="/trash.svg" alt="Delete" class="icon" />
                </button>
              </template>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- User posts mode -->
    <div v-else class="posts-container">
      <div v-if="loading" class="loading">Loading your posts...</div>
      <div v-else>
        <div v-if="posts.length === 0" class="no-data">{{ emptyMessage }}</div>
        <ul class="post-list">
          <li v-for="post in posts" :key="post.post_id" class="post-item">
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
              <template v-if="editingPost === post.post_id">
                <input
                  v-model="editPostData.title"
                  class="edit-input edit-title"
                  placeholder="Post title..."
                />
              </template>
              <template v-else>
                <h3 class="post-title">{{ post.title }}</h3>
              </template>
            </div>
            <div class="post-content-container">
              <template v-if="editingPost === post.post_id">
                <textarea
                  v-model="editPostData.content"
                  class="edit-input edit-content"
                  placeholder="Post content..."
                  rows="4"
                ></textarea>
              </template>
              <template v-else>
                <p class="post-content">{{ post.content }}</p>
              </template>
            </div>
            <div class="post-actions">
              <template v-if="editingPost === post.post_id">
                <button class="action-btn save-btn" @click="saveEditedPost" aria-label="Save Post">
                  Save
                </button>
                <button class="action-btn cancel-btn" @click="cancelEditPost" aria-label="Cancel Edit">
                  Cancel
                </button>
              </template>
              <template v-else>
                <button class="action-btn edit-btn" @click="editPostFromUser(post)" aria-label="Edit Post">
                  <img src="/edit.svg" alt="Edit" class="icon" />
                </button>
                <button class="action-btn delete-btn" @click="deletePostFromUser(post)" aria-label="Delete Post">
                  <img src="/trash.svg" alt="Delete" class="icon" />
                </button>
              </template>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import http from '@/api/http'
import { useAuthStore } from '@/stores/auth.js'
import { updateUserPost, updateUserComment, editUserContent } from '@/api/user.js'
import toastManager from '@/api/toastManager'

// Props
const props = defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  comments: {
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
  mode: {
    type: String,
    default: 'posts' // 'posts' or 'comments'
  },
  userId: {
    type: [String, Number],
    default: null
  },
  viewPost: {
    type: Function,
    default: null
  }
})

// Emits
const emit = defineEmits(['load-more', 'post-updated', 'post-deleted', 'comment-updated', 'comment-deleted'])

const authStore = useAuthStore()
const activeButtons = ref(new Set()) // Store keys like "like:123", "reply:123"
const openReplies = ref({})
const newCommentText = ref({})
const loadingComments = ref(new Set()) // Track which posts are loading comments

// Edit state
const editingPost = ref(null)
const editingComment = ref(null)
const editPostData = ref({
  title: '',
  content: '',
  tags: []
})
const editCommentData = ref({
  content: ''
})

// Helper functions using global toast manager
const showToast = (message, type = 'info', duration = 3000) => {
  return toastManager.addToast(message, type, duration)
}

const showConfirm = async (message, options = {}) => {
  return await toastManager.addConfirm(message, options)
}

// Computed property: current user ID
const currentUserId = computed(() => {
  return authStore.userId?.value || authStore.user?.id || null
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

// Check if user is comment author
const isCommentAuthor = (comment) => {
  return currentUserId.value && Number(currentUserId.value) === Number(comment.user_id)
}

// Edit user post
const editPostFromUser = (post) => {
  editingPost.value = post.post_id
  editPostData.value = {
    title: post.title,
    content: post.content,
    tags: [...(post.tags || [])]
  }
}

// Save edited post
const saveEditedPost = async () => {
  if (!editingPost.value) return

  try {
    const updateData = {
      title: editPostData.value.title.trim(),
      content: editPostData.value.content.trim(),
      tags: editPostData.value.tags
    }

    const response = await editUserContent('post', editingPost.value, updateData)

    if (response.code === 1) {
      // Update local post data
      const postIndex = props.posts.findIndex(p => p.post_id === editingPost.value)
      if (postIndex !== -1) {
        props.posts[postIndex] = response.data
      }

      emit('post-updated', response.data)
      showToast('Post updated successfully', 'success')
    }
  } catch (err) {
    console.error('Failed to update post', err)
    showToast('Failed to update post', 'error')
  } finally {
    editingPost.value = null
    editPostData.value = { title: '', content: '', tags: [] }
  }
}

// Cancel editing post
const cancelEditPost = () => {
  editingPost.value = null
  editPostData.value = { title: '', content: '', tags: [] }
}

// Delete user post
const deletePostFromUser = async (post) => {
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

// Edit user comment
const editCommentFromUser = (comment) => {
  editingComment.value = comment.comment_id
  editCommentData.value = {
    content: comment.content
  }
}

// Save edited comment
const saveEditedComment = async () => {
  if (!editingComment.value) return

  try {
    const updateData = {
      content: editCommentData.value.content.trim()
    }

    const response = await editUserContent('comment', editingComment.value, updateData)

    if (response.code === 1) {
      // Update local comment data
      const commentIndex = props.comments.findIndex(c => c.comment_id === editingComment.value)
      if (commentIndex !== -1) {
        props.comments[commentIndex] = response.data
      }

      emit('comment-updated', response.data)
      showToast('Comment updated successfully', 'success')
    }
  } catch (err) {
    console.error('Failed to update comment', err)
    showToast('Failed to update comment', 'error')
  } finally {
    editingComment.value = null
    editCommentData.value = { content: '' }
  }
}

// Cancel editing comment
const cancelEditComment = () => {
  editingComment.value = null
  editCommentData.value = { content: '' }
}

// Delete user comment
const deleteCommentFromUser = async (comment) => {
  const confirmed = await showConfirm('Delete this comment?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  if (!confirmed) return

  try {
    await http.delete(`/comments/${comment.comment_id}`)
    emit('comment-deleted', comment)
    showToast('Comment deleted successfully', 'success')
  } catch (err) {
    console.error('Failed to delete comment', err)
    showToast('Failed to delete comment', 'error')
  }
}

// Delete comment (local update)
const deleteComment = async (post, comment) => {
  const confirmed = await showConfirm('Delete this comment?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  if (!confirmed) return

  try {
    await http.delete(`/comments/${comment.comment_id}`)
    // Remove comment from local state
    post.comments = (post.comments || []).filter(c => c.comment_id !== comment.comment_id)
    // Update comment count
    post.comment_count = Math.max(0, (post.comment_count || 1) - 1)
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
.post-actions { display:flex; gap:0.5rem; margin-top:0.5rem; align-items:center; justify-content: end;}
.action-btn { background: transparent; border: none; padding: 0.25rem; cursor: pointer; display: inline-flex; align-items: center; }
.action-btn .icon { width:20px; height:20px; display:block; }
.action-btn:hover { opacity: 0.9; transform: translateY(-1px); }
.like-count {color:#ccc; font-weight:500; }
.comment-user { display:flex; justify-content:space-between; align-items:flex-start; gap:0.75rem; }
.comment-user-left { display:flex; flex-direction:column; }
.comment-username-text { font-weight:700; color:#fff; }

/* Edit input styles */
.edit-input {
  width: 100%;
  padding: 0.5rem;
  border: 2px solid #333333;
  border-radius: 8px;
  background-color: #1a1a1a;
  color: #ffffff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
  font-family: inherit;
  resize: vertical;
}

.edit-input:focus {
  border-color: #f5c518;
}

.edit-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.edit-content {
  margin-bottom: 0.5rem;
}

.edit-comment-content {
  margin-bottom: 0.5rem;
}

.post-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.action-btn.edit-btn .icon {
  width: 18px;
  height: 18px;
}

.action-btn.save-btn,
.action-btn.cancel-btn {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}

.action-btn.save-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.action-btn.save-btn:hover:not(:disabled) {
  background-color: #2a4193;
}

.action-btn.cancel-btn {
  background-color: #6c757d;
  color: #ffffff;
}

.action-btn.cancel-btn:hover:not(:disabled) {
  background-color: #545b62;
}
.comment-delete-btn { background: transparent; border: none; padding: 0; cursor: pointer; display: inline-flex; align-items: center; }
.comment-delete-btn .icon { width:16px; height:16px; }

.action-btn:hover .icon,
.comment-delete-btn:hover .icon {
  filter: invert(69%) sepia(89%) saturate(749%) hue-rotate(358deg) brightness(101%) contrast(101%);
}

/* User comment mode styles - same as posts */
.user-comment {
  padding:1rem 0;
  color:#fff;
  border-radius:0;
}
/* Apply 2px white separator except last item */
.user-comment:not(:last-child) {
  border-bottom: 2px solid #ffffff;
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

.post-link {
    cursor: pointer;
}
</style>
