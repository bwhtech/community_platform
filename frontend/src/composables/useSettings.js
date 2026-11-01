import { ref } from 'vue'

// One settings dialog for the whole app, opened from anywhere.
export const settingsOpen = ref(false)
export const settingsTab = ref('profile')

export function openSettings(tab = 'profile') {
  settingsTab.value = tab
  settingsOpen.value = true
}
