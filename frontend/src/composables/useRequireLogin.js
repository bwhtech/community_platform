import { useRoute, useRouter } from 'vue-router'
import { toast } from 'frappe-ui'
import { currentUser, isLoggedIn } from '@/session'

// Guests can browse everything; any write needs a GitHub-linked Contributor.
export function useRequireLogin() {
  const router = useRouter()
  const route = useRoute()
  return function requireLogin() {
    if (currentUser.value) return true
    if (isLoggedIn.value) {
      toast.info('Log in with GitHub to take part')
      return false
    }
    toast.info('Log in with GitHub to do that')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return false
  }
}
