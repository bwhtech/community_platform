import { ref } from 'vue'
import { toast } from 'frappe-ui'

// Wraps a mock write: tracks loading and turns thrown errors into toasts.
export function useAction(fn, { success } = {}) {
  const loading = ref(false)
  async function run(...args) {
    loading.value = true
    try {
      const result = await fn(...args)
      if (success) toast.success(success)
      return result
    } catch (error) {
      toast.error(error.message)
      throw error
    } finally {
      loading.value = false
    }
  }
  return { run, loading }
}
