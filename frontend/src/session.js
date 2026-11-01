import { computed, reactive } from 'vue'
import { call } from 'frappe-ui'

// Who is looking, filled from boot data. `me` is the Contributor card of the
// logged-in user; a logged-in user without one (e.g. a desk admin) has none.
export const session = reactive({
  user: 'Guest',
  me: null,
  isModerator: false,
  isAdmin: false,
  githubLoginUrl: null,
  products: [],
})

export function applyBoot(boot) {
  Object.assign(session, {
    user: boot.user ?? 'Guest',
    me: boot.me ?? null,
    isModerator: Boolean(boot.isModerator),
    isAdmin: Boolean(boot.isAdmin),
    githubLoginUrl: boot.githubLoginUrl ?? null,
    products: boot.products ?? [],
  })
}

export async function refreshBoot() {
  applyBoot(await call('community_platform.api.session.get_boot'))
}

export const currentUser = computed(() => session.me?.login ?? null)
export const isLoggedIn = computed(() => session.user !== 'Guest')
export const isModerator = computed(() => session.isModerator)
export const isAdmin = computed(() => session.isAdmin)

// GitHub OAuth when it is configured, Frappe's own login page otherwise.
export function login(redirect = '/me') {
  window.location.href = session.githubLoginUrl ?? `/login?redirect-to=${encodeURIComponent(redirect)}`
}

export async function logout() {
  await call('logout')
  window.location.href = '/leaderboard'
}
