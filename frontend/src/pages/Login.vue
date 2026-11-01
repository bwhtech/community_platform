<template>
  <div class="grid min-h-screen place-content-center bg-surface-gray-1 px-4">
    <div class="w-full max-w-sm rounded-6 border border-outline-gray-1 bg-surface-base p-8 shadow-sm">
      <img :src="LOGO" alt="" class="size-10" />
      <h1 class="mt-6 text-2xl font-semibold text-ink-gray-9">Join the Frappe community</h1>
      <p class="mt-2 text-p-base text-ink-gray-6">
        Earn points for your issues, pull requests, talks and certifications. Vote on what gets built next.
      </p>
      <Button
        class="mt-6 w-full"
        size="md"
        variant="solid"
        icon-left="lucide-log-in"
        :label="session.githubLoginUrl ? 'Continue with GitHub' : 'Log in'"
        :loading="loading"
        @click="continueWithGithub"
      />
      <p v-if="!session.githubLoginUrl" class="mt-3 text-p-xs text-ink-amber-7">
        GitHub login isn't set up on this site yet. Add a GitHub Social Login Key in Desk to enable it.
      </p>
      <p class="mt-4 text-p-xs text-ink-gray-5">
        We read your public profile and verified emails. Emails are used only to match your
        events.frappe.io and school.frappe.io records.
      </p>
      <Button class="mt-6" variant="ghost" icon-left="lucide-arrow-left" label="Browse without logging in" route="/leaderboard" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { Button } from 'frappe-ui'
import { login, session } from '@/session'

// Served by Frappe from the app's public folder, not bundled by Vite.
const LOGO = '/assets/community_platform/logos/frappe.svg'

const route = useRoute()
const loading = ref(false)

function continueWithGithub() {
  loading.value = true
  login(route.query.redirect || '/me')
}
</script>
