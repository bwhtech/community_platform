import './index.css'

import { createApp } from 'vue'
import { FrappeUI, call } from 'frappe-ui'
import { router } from './router'
import { applyBoot } from './session'
import App from './App.vue'

// The built page gets boot data as window globals from Jinja; the Vite dev
// server can't render Jinja, so it asks the backend instead.
async function loadBoot() {
  if (import.meta.env.DEV) {
    const boot = await call('community_platform.www.community.get_context_for_dev')
    window.csrf_token = boot.csrf_token
    return boot
  }
  const { user, me, isModerator, isAdmin, products, githubLoginUrl } = window
  return { user, me, isModerator, isAdmin, products, githubLoginUrl }
}

loadBoot().then((boot) => {
  applyBoot(boot)
  const app = createApp(App)
  app.use(router)
  app.use(FrappeUI)
  app.mount('#app')
})
