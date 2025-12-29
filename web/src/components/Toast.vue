<template>
  <Teleport to="body">
    <div v-if="isVisible" class="toast-container">
      <div
        v-for="(toast, index) in toasts"
        :key="toast.id"
        class="toast-item"
        :class="[
          `toast-${toast.type}`,
          { 'toast-confirm': toast.confirm },
          { 'toast-enter': toast.entering },
          { 'toast-leave': toast.leaving }
        ]"
        :style="{ top: `${index * 70 + 20}px` }"
      >
        <div class="toast-content">
          <div class="toast-message">{{ toast.message }}</div>
          <div v-if="toast.confirm" class="toast-actions">
            <button
              class="toast-btn toast-cancel"
              @click="handleCancel(toast)"
            >
              {{ toast.cancelText || 'Cancel' }}
            </button>
            <button
              class="toast-btn toast-confirm-btn"
              @click="handleConfirm(toast)"
            >
              {{ toast.confirmText || 'Confirm' }}
            </button>
          </div>
        </div>
        <button
          v-if="!toast.confirm"
          class="toast-close"
          @click="removeToast(toast.id)"
        >
          ×
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import toastManager from '@/api/toastManager'

let toastId = 0
const toasts = ref([])
const isVisible = computed(() => toasts.value.length > 0)

const emit = defineEmits(['confirm', 'cancel', 'close'])

// Define clearAllToasts function first
const clearAllToasts = () => {
  // Mark all toasts as leaving and remove them after animation
  toasts.value.forEach(toast => {
    toast.leaving = true
  })

  setTimeout(() => {
    toasts.value.splice(0, toasts.value.length)
  }, 300)
}

// Register with global toast manager on mount
onMounted(() => {
  // Clear any stale toasts from previous navigation
  clearAllToasts()
  toastManager.register({
    addToast,
    addConfirm,
    removeToast,
    clearAllToasts
  })
})

// Unregister on unmount
onUnmounted(() => {
  // Clear all toasts before unregistering to prevent stale toasts
  clearAllToasts()
  toastManager.unregister()
})

const addToast = (message, type = 'info', duration = 3000) => {
  const id = ++toastId

  let finalMessage = message
  let finalType = type

  if (typeof message === 'object' && message !== null && 'code' in message && 'msg' in message) {

    finalMessage = message.msg || (message.code === 1 ? 'Operation successful' : 'Operation failed')
    finalType = message.code === 1 ? 'success' : 'error'
  }

  const toast = {
    id,
    message: finalMessage,
    type: finalType,
    duration,
    confirm: false,
    entering: true,
    leaving: false
  }

  toasts.value.push(toast)

  setTimeout(() => {
    toast.entering = false
  }, 100)

  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  return id
}

const addConfirm = (message, options = {}) => {
  return new Promise((resolve) => {
    const id = ++toastId
    const toast = {
      id,
      message,
      type: options.type || 'warning',
      confirm: true,
      confirmText: options.confirmText || 'Confirm',
      cancelText: options.cancelText || 'Cancel',
      entering: true,
      leaving: false,
      resolve
    }

    toasts.value.push(toast)

    setTimeout(() => {
      toast.entering = false
    }, 100)
  })
}


const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index === -1) return

  const toast = toasts.value[index]
  toast.leaving = true


  setTimeout(() => {
    toasts.value.splice(index, 1)
    emit('close', id)
  }, 300)
}

const handleConfirm = (toast) => {
  toast.resolve?.(true)
  removeToast(toast.id)
  emit('confirm', toast.id)
}


const handleCancel = (toast) => {
  toast.resolve?.(false)
  removeToast(toast.id)
  emit('cancel', toast.id)
}


defineExpose({
  addToast,
  addConfirm,
  removeToast,
  clearAllToasts
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  pointer-events: none;
}

.toast-item {
  position: absolute;
  right: 0;
  min-width: 300px;
  max-width: 500px;
  padding: 0;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  pointer-events: auto;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(100%);
}

.toast-item.toast-enter {
  opacity: 1;
  transform: translateX(0);
}

.toast-item.toast-leave {
  opacity: 0;
  transform: translateX(100%);
}

/* Toast types - unified style */
.toast-info,
.toast-success,
.toast-warning,
.toast-error,
.toast-confirm {
  background-color: #1a1a1a;
  border-left: 4px solid #3552b0;
}

.toast-content {
  padding: 1rem 1.5rem;
}

.toast-message {
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.toast-confirm .toast-message {
  margin-bottom: 1rem;
}

.toast-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.toast-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.toast-cancel {
  background-color: #333333;
  color: #cccccc;
}

.toast-cancel:hover {
  background-color: #444444;
  color: #ffffff;
  transform: translateY(-1px);
}

.toast-confirm-btn {
  background-color: #3552b0;
  color: #ffffff;
}

.toast-confirm-btn:hover {
  background-color: #2a4193;
  transform: translateY(-1px);
}

.toast-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

/* Responsive */
@media (max-width: 768px) {
  .toast-container {
    left: 20px;
    right: 20px;
  }

  .toast-item {
    min-width: auto;
    max-width: none;
  }

  .toast-actions {
    flex-direction: column;
  }

  .toast-btn {
    width: 100%;
  }
}
</style>
