// Toast Manager - Global toast management to avoid component ref issues
class ToastManager {
  constructor() {
    this.toastComponent = null
    this.queue = []
  }

  // Register the toast component instance
  register(toastInstance) {
    this.toastComponent = toastInstance
    // Process any queued operations
    while (this.queue.length > 0) {
      const { method, args } = this.queue.shift()
      this[method](...args)
    }
  }

  // Unregister the toast component
  unregister() {
    this.toastComponent = null
  }

  // Safe method caller with queuing
  _call(method, ...args) {
    if (this.toastComponent && typeof this.toastComponent[method] === 'function') {
      return this.toastComponent[method](...args)
    } else {
      // Queue the operation for when component is available
      this.queue.push({ method, args })
      return null
    }
  }

  // Public API methods
  addToast(message, type = 'info', duration = 3000) {
    return this._call('addToast', message, type, duration)
  }

  addConfirm(message, options = {}) {
    return this._call('addConfirm', message, options)
  }

  removeToast(id) {
    return this._call('removeToast', id)
  }

  // Helper methods for common use cases
  showSuccess(message, duration = 3000) {
    return this.addToast(message, 'success', duration)
  }

  showError(message, duration = 3000) {
    return this.addToast(message, 'error', duration)
  }

  showWarning(message, duration = 3000) {
    return this.addToast(message, 'warning', duration)
  }

  showInfo(message, duration = 3000) {
    return this.addToast(message, 'info', duration)
  }

  confirm(message, options = {}) {
    return this.addConfirm(message, options)
  }
}

// Create singleton instance
const toastManager = new ToastManager()

export default toastManager
