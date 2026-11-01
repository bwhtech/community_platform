import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Two-way binding between a ref and a URL query param, so filters survive
// reloads and links can be shared.
export function useQueryParam(name, fallback) {
  const route = useRoute()
  const router = useRouter()
  return computed({
    get: () => route.query[name] ?? fallback,
    set: (value) => {
      const query = { ...route.query, [name]: value === fallback ? undefined : value }
      router.replace({ query })
    },
  })
}
