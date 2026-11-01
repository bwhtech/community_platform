// Backend calls. Reads are `useCall` resources that refetch when their params
// change; writes go through `write()`, which bumps `dataVersion` so every
// mounted resource refetches and the page reflects the change.
import { ref, toValue } from 'vue'
import { call, useCall } from 'frappe-ui'
import { refreshBoot, session } from '@/session'
import { todayIST } from '@/utils/dates'

const METHOD = 'community_platform.api.'
export const REACTIONS = ['❤️', '🎉', '🚀', '👀', '😕']

const dataVersion = ref(0)

function useRead(method, params = () => ({})) {
  return useCall({
    url: `/api/v2/method/${METHOD}${method}`,
    params: () => ({ ...params(), _v: dataVersion.value }),
    refetch: true,
  })
}

async function write(method, args = {}) {
  const result = await call(METHOD + method, args)
  dataVersion.value++
  return result
}

// -- Products (from boot data) --------------------------------------------

export function listProducts() {
  return session.products
}

export function getProduct(id) {
  return session.products.find((p) => p.id === id) ?? null
}

// -- Leaderboard --------------------------------------------------------------

export function useLeaderboard(month) {
  return useRead('leaderboard.get_leaderboard', () => ({ month: toValue(month) }))
}

export function useMonthSummary(month) {
  return useRead('leaderboard.get_month_summary', () => ({ month: toValue(month) }))
}

export function leaderboardMonths(count = 12) {
  const [y, m] = todayIST().split('-').map(Number)
  return Array.from({ length: count }, (_, i) => new Date(Date.UTC(y, m - 1 - i, 1)).toISOString().slice(0, 7))
}

// -- Profile ------------------------------------------------------------------

export function useProfile(login) {
  return useRead('profile.get_profile', () => ({ login: toValue(login) }))
}

export function useHeatmap(login, period, source) {
  return useRead('profile.get_heatmap', () => ({
    login: toValue(login),
    period: toValue(period),
    source: toValue(source),
  }))
}

export function useActivity(login, { source, date, limit }) {
  return useRead('profile.get_activity', () => {
    const day = toValue(date)
    return {
      login: toValue(login),
      source: toValue(source),
      limit: toValue(limit),
      ...(day ? { date: day } : {}),
    }
  })
}

// -- Feature requests -------------------------------------------------------

export function useFeatureRequests({ product, sort, query }) {
  return useRead('requests.list_requests', () => ({
    product: toValue(product),
    sort: toValue(sort),
    query: toValue(query),
  }))
}

export function useFeatureRequest(id) {
  return useRead('requests.get_request', () => ({ id: toValue(id) }))
}

export const createFeatureRequest = (values) => write('requests.create_request', values)
export const updateFeatureRequest = (id, values) => write('requests.update_request', { id, ...values })
export const deleteFeatureRequest = (id) => write('requests.delete_request', { id })
export const setRequestHidden = (id, hidden) => write('requests.set_hidden', { id, hidden })
export const toggleUpvote = (id) => write('requests.toggle_upvote', { id })
export const toggleReaction = (id, emoji) => write('requests.toggle_reaction', { id, emoji })

// -- Badges -------------------------------------------------------------------

export function useBadges() {
  return useRead('badges.list_badges')
}

// -- My account ---------------------------------------------------------------

export function useMyProfile() {
  return useRead('me.get_my_profile')
}

export async function updateProfile(profile) {
  await write('me.update_profile', { profile })
  await refreshBoot()
}

export async function updateName(fullName) {
  await write('me.update_name', { full_name: fullName })
  await refreshBoot()
}

export async function updatePhoto(fileUrl) {
  await write('me.update_photo', { file_url: fileUrl || null })
  await refreshBoot()
}

export const changePassword = (oldPassword, newPassword) =>
  call(METHOD + 'me.change_password', { old_password: oldPassword, new_password: newPassword })
export const connectDiscuss = (username) => write('me.connect_discuss', { username })
export const disconnectDiscuss = () => write('me.disconnect_discuss')
export const syncGithub = () => write('me.sync_github')

// -- Admin --------------------------------------------------------------------

export function usePointRules() {
  return useRead('admin.list_point_rules')
}

export function useAdminBadges() {
  return useRead('admin.list_badges')
}

export function useLedger({ login, source, limit }) {
  return useRead('admin.list_ledger', () => {
    const who = toValue(login)
    return { source: toValue(source), limit: toValue(limit), ...(who ? { login: who } : {}) }
  })
}

export function useContributors() {
  return useRead('admin.list_contributors')
}

export const updatePointRule = (action, patch) => write('admin.update_point_rule', { action, patch })
export const saveBadge = (badge) => write('admin.save_badge', { badge })
export const deleteBadge = (id) => write('admin.delete_badge', { id })
export const awardBadge = (id, login) => write('admin.award_badge', { id, login })
export const revokeEntry = (id, reason) => write('admin.revoke_entry', { id, reason })

export async function updateProduct(id, patch) {
  await write('admin.update_product', { id, patch })
  await refreshBoot()
}
