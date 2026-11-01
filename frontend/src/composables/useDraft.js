import { toValue } from 'vue'

// Unsent form values kept in localStorage, so a refresh or a closed dialog
// loses nothing. `key` can be a getter when it depends on props.
export function useDraft(key) {
  return {
    load() {
      try {
        return JSON.parse(localStorage.getItem(toValue(key)))
      } catch {
        return null
      }
    },
    save(value) {
      localStorage.setItem(toValue(key), JSON.stringify(value))
    },
    clear() {
      localStorage.removeItem(toValue(key))
    },
  }
}
