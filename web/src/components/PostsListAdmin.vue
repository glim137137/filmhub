<template>
  <div class="posts-list">
    <!-- Admin comments mode -->
    <div v-if="mode === 'comments'">
      <div v-if="loading" class="loading">Loading comments...</div>
      <div v-else>
        <div v-if="comments.length === 0" class="no-data">{{ emptyMessage }}</div>
        <ul class="post-list">
          <li class="post-item admin-comment" v-for="comment in comments" :key="comment.comment_id">
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
            <div class="comment-content">{{ comment.content }}</div>
            <div class="post-actions">
              <button class="action-btn delete-btn" @click="onAdminDeleteComment(comment)" aria-label="Delete comment">
                <img src="/trash.svg" alt="Delete" class="icon" />
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <!-- Admin posts mode -->
    <div v-else class="posts-container">
      <div v-if="loading" class="loading">Loading posts...</div>
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
            <h3 class="post-title">{{ post.title }}</h3>
            </div>
            <p class="post-content">{{ post.content }}</p>
            <div class="post-actions">
              <button class="action-btn delete-btn" @click="onAdminDeletePost(post)" aria-label="Delete Post">
                <img src="/trash.svg" alt="Delete" class="icon" />
              </button>
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
import { ref } from 'vue'
import { deletePostByAdmin, deleteCommentByAdmin } from '@/api/admin.js'
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
  viewPost: {
    type: Function,
    default: null
  }
})

// Emits
const emit = defineEmits(['load-more', 'post-deleted', 'comment-deleted'])

// Helper functions using global toast manager
const showToast = (message, type = 'info', duration = 3000) => {
  return toastManager.addToast(message, type, duration)
}

const showConfirm = async (message, options = {}) => {
  return await toastManager.addConfirm(message, options)
}

const onImgError = (e) => {
  try {
    e.target.src = '/anonymous.png'
  } catch (err) {
    /* ignore */
  }
}

// Admin delete post
const onAdminDeletePost = async (post) => {
  const confirmed = await showConfirm('Delete this post?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  if (!confirmed) return

  try {
    await deletePostByAdmin(post.post_id)
    emit('post-deleted', post)
    showToast('Post deleted successfully', 'success')
  } catch (err) {
    console.error('Failed to delete post', err)
    showToast('Failed to delete post', 'error')
  }
}

// Admin delete comment
const onAdminDeleteComment = async (comment) => {
  const confirmed = await showConfirm('Delete this comment?', {
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
  })

  if (!confirmed) return

  try {
    await deleteCommentByAdmin(comment.comment_id)
    emit('comment-deleted', comment)
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
.post-content, .comment-content {
  margin: 0 0 0.5rem 0;
  color: #ddd;
  line-height: 1.5;
}
.post-actions { display:flex; gap:0.5rem; margin-top:0.5rem; align-items:center; justify-content: end; }
.action-btn { background: transparent; border: none; padding: 0.25rem; cursor: pointer; display: inline-flex; align-items: center; }
.action-btn .icon { width:20px; height:20px; display:block; }
.action-btn:hover { opacity: 0.9; transform: translateY(-1px); }

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

/* Admin comment mode styles - same as user comments */
.admin-comment {
  padding:1rem 0;
  color:#fff;
  border-radius:0;
}
/* Apply 2px white separator except last item */
.admin-comment:not(:last-child) {
  border-bottom: 2px solid #ffffff;
}
.comment-delete-btn { background: transparent; border: none; padding: 0; cursor: pointer; display: inline-flex; align-items: center; }
.comment-delete-btn .icon { width:16px; height:16px; }

.action-btn:hover .icon,
.comment-delete-btn:hover .icon {
  filter: invert(69%) sepia(89%) saturate(749%) hue-rotate(358deg) brightness(101%) contrast(101%);
}
</style>
