<template>
  <AppHeader :title="!request && requestResource.isFinished ? 'Not found' : `Request #${id}`" back="/requests">
    <template #title>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #actions>
      <Dropdown v-if="request && menuOptions.length" :options="menuOptions">
        <Button variant="ghost" icon="lucide-ellipsis" aria-label="Request options" />
      </Dropdown>
    </template>
  </AppHeader>

  <div v-if="!request && !requestResource.isFinished" class="mx-auto max-w-[770px] px-3 pt-6 sm:px-5" aria-busy="true">
    <div class="flex items-start gap-4">
      <Skeleton class="h-16 w-14 shrink-0 rounded-5" />
      <div class="flex-1 space-y-3">
        <Skeleton class="h-7 w-3/4 rounded-2" />
        <Skeleton class="h-4 w-64 max-w-full rounded-2" />
      </div>
    </div>
    <div class="mt-6 space-y-2">
      <Skeleton class="h-4 w-full rounded-2" />
      <Skeleton class="h-4 w-full rounded-2" />
      <Skeleton class="h-4 w-5/6 rounded-2" />
      <Skeleton class="h-4 w-2/3 rounded-2" />
    </div>
    <Skeleton class="mt-10 h-5 w-40 rounded-2" />
    <div class="mt-3 flex gap-1.5">
      <Skeleton v-for="i in 5" :key="i" class="size-8 rounded-full" />
    </div>
  </div>

  <div v-else-if="!request" class="flex flex-col items-center gap-3 py-24 text-center">
    <div class="rounded-full bg-surface-gray-2 p-3 text-ink-gray-5">
      <span class="lucide-search-x size-6" aria-hidden="true" />
    </div>
    <p class="text-base text-ink-gray-7">This request doesn't exist or was removed</p>
    <Button label="All feature requests" route="/requests" />
  </div>

  <div v-else class="mx-auto max-w-[770px] px-3 pb-20 pt-6 sm:px-5">
    <Alert
      v-if="request.hidden"
      class="mb-6"
      theme="red"
      title="Hidden by a moderator"
      description="Only moderators can see this request. Upvote points for the author were revoked."
    />

    <div class="flex items-start gap-4">
      <UpvoteButton :request="request" large />
      <div class="min-w-0 flex-1">
        <h1 class="text-2xl font-semibold leading-snug text-ink-gray-9">{{ request.title }}</h1>
        <div class="mt-2 flex flex-wrap items-center gap-x-1.5 text-sm text-ink-gray-5">
          <RouterLink
            :to="{ path: '/requests', query: { product: request.product } }"
            class="inline-flex items-center gap-1 hover:text-ink-gray-7"
          >
            <ProductLogo :product="request.productInfo" size="xs" />{{ request.productInfo?.name }}
          </RouterLink>
          <span aria-hidden="true">·</span>
          <RouterLink :to="`/u/${request.author.login}`" class="inline-flex items-center gap-1 hover:text-ink-gray-7">
            <Avatar :label="request.author.fullName" :image="request.author.avatar" size="xs" />
            {{ request.author.fullName }}
          </RouterLink>
          <span aria-hidden="true">·</span>
          <span>{{ timeAgo(request.createdAt) }}</span>
        </div>
      </div>
    </div>

    <DescriptionView class="mt-6" :source="request.description" />

    <ReactionBar class="mt-6" :request="request" />

    <section class="mt-10">
      <h2 class="text-lg-semibold text-ink-gray-8">
        Upvoted by {{ request.voters.length }} {{ request.voters.length === 1 ? 'person' : 'people' }}
      </h2>
      <div class="mt-3 flex flex-wrap gap-1.5">
        <Tooltip v-for="voter in request.voters" :key="voter.login" :text="voter.fullName">
          <RouterLink :to="`/u/${voter.login}`">
            <Avatar :label="voter.fullName" :image="voter.avatar" size="md" />
          </RouterLink>
        </Tooltip>
      </div>
    </section>

    <p class="mt-10 text-p-sm text-ink-gray-5">
      Want to talk it through? Start a thread on
      <a href="https://discuss.frappe.io" target="_blank" rel="noopener" class="text-ink-blue-link hover:underline">discuss.frappe.io</a>
      and link this request.
    </p>
  </div>

  <RequestDialog v-if="request" v-model:open="showEdit" :request="request" />
</template>

<script setup>
import { computed, defineAsyncComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Alert, Avatar, Breadcrumbs, Button, Dropdown, Skeleton, Tooltip, dialog, toast } from 'frappe-ui'
import AppHeader from '@/components/AppHeader.vue'
import ProductLogo from '@/components/ProductLogo.vue'
import ReactionBar from '@/components/ReactionBar.vue'
import RequestDialog from '@/components/RequestDialog.vue'
import UpvoteButton from '@/components/UpvoteButton.vue'
import { deleteFeatureRequest, setRequestHidden, useFeatureRequest } from '@/api'
import { timeAgo } from '@/utils/dates'

// The editor is heavy; keep it out of the shared requests chunk.
const DescriptionView = defineAsyncComponent(() => import('@/components/requests/DescriptionView.vue'))
const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()
const showEdit = ref(false)

const requestResource = useFeatureRequest(computed(() => props.id))
const request = computed(() => requestResource.data)

const breadcrumbs = computed(() => [
  { label: 'Feature requests', route: '/requests' },
  { label: !request.value && requestResource.isFinished ? 'Not found' : `#${props.id}` },
])

const menuOptions = computed(() => {
  const can = request.value.can
  return [
    can.edit && { label: 'Edit', icon: 'lucide-pencil', onClick: () => (showEdit.value = true) },
    can.moderate && {
      label: request.value.hidden ? 'Unhide' : 'Hide',
      icon: request.value.hidden ? 'lucide-eye' : 'lucide-eye-off',
      onClick: toggleHidden,
    },
    can.delete && { label: 'Delete', icon: 'lucide-trash-2', theme: 'red', onClick: confirmDelete },
  ].filter(Boolean)
})

function toggleHidden() {
  const hide = !request.value.hidden
  dialog.confirm({
    title: hide ? 'Hide this request?' : 'Unhide this request?',
    message: hide
      ? 'It disappears from the list for everyone except moderators, and the points the author earned from its upvotes are revoked.'
      : 'It shows in the list again, and the author earns points for its upvotes again.',
    confirmLabel: hide ? 'Hide' : 'Unhide',
    theme: hide ? 'red' : 'gray',
    onConfirm: async () => {
      await setRequestHidden(request.value.id, hide)
      toast.success(hide ? 'Request hidden' : 'Request visible again')
    },
  })
}

function confirmDelete() {
  dialog.confirm({
    title: 'Delete this request?',
    message: 'This cannot be undone.',
    confirmLabel: 'Delete',
    theme: 'red',
    onConfirm: async () => {
      await deleteFeatureRequest(request.value.id)
      toast.success('Request deleted')
      router.push('/requests')
    },
  })
}
</script>
