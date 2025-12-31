<template>
  <div class="explore-container">
    <div class="explore-header">
      <h1>Explore</h1>
    </div>

    <div class="explore-body">
      <div v-if="loading" class="loading">Loading tags...</div>
      <div v-else class="tag-grid">
        <button
          v-for="tag in tags"
          :key="tag.name"
          class="tag-btn"
          @click="goTag(tag.name)"
        >
          <span class="tag-label">{{ tag.name }}</span>
          <span class="tag-count">({{ tag.count }})</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Toast Component -->
  <Toast />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/api/http'
import { useRouter } from 'vue-router'
import Toast from '@/components/Toast.vue'

const tags = ref([])
const loading = ref(false)
const router = useRouter()

const loadTags = async () => {
  loading.value = true
  try {
    const res = await http.get('/tags')
    if (res?.code === 1 && Array.isArray(res.data?.tags)) {
      tags.value = res.data.tags
    } else if (Array.isArray(res?.tags)) {
      tags.value = res.tags
    } else {
      tags.value = []
    }
  } catch (err) {
    console.error('Failed to load tags', err)
    tags.value = []
  } finally {
    loading.value = false
  }
}

const goTag = (tag) => {
  // let router handle encoding of params
  router.push({ name: 'explore-tag', params: { tag } })
}

onMounted(loadTags)
</script>

<style scoped>
.explore-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.explore-header h1 {
  font-size: 2rem;
  margin-bottom: 0.25rem;
  position: relative;
  padding-left: 20px;
}
.explore-header h1::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 5px;
  background-color: #f5c518;
  border-radius: 3px;
}
.explore-body {
  margin-top: 1rem;
}
.tag-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
}
.tag-btn {
  display: inline-flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.45rem 0.6rem;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #ffffff;
  font-weight: 600;
  white-space: nowrap; /* prevent internal wrap */
  /* allow long names to expand; let flex-wrap move to next line when needed */
  max-width: 100%;
}
.tag-label { margin-right: 0.5rem; color: #ffffff; }
.tag-count { color: rgba(255,255,255,0.7); font-weight: 500; }
.tag-btn:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .tag-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>



