<template>
  <AppHeader title="Feature requests">
    <template #actions>
      <Button variant="solid" icon-left="lucide-plus" label="New request" @click="openNew" />
    </template>
    <template #mobile-actions>
      <Button variant="ghost" icon="lucide-plus" aria-label="New request" @click="openNew" />
    </template>
  </AppHeader>

  <div class="mx-auto max-w-[940px] px-3 pb-20 pt-5 sm:px-5">
    <div class="flex flex-wrap items-center gap-2">
      <TabButtons v-model="sort" :options="SORTS" />
      <div class="w-48">
        <Select v-model="product" :options="productOptions" />
      </div>
      <TextInput v-model="query" class="ml-auto w-full sm:w-60" placeholder="Search titles" :debounce="150">
        <template #prefix>
          <span class="lucide-search size-4 text-ink-gray-5" aria-hidden="true" />
        </template>
      </TextInput>
    </div>

    <div v-if="!requestsResource.data" class="mt-4 divide-y divide-outline-gray-1" aria-busy="true">
      <div v-for="i in 6" :key="i" class="flex items-start gap-4 py-4">
        <Skeleton class="h-12 w-11 shrink-0 rounded-5" />
        <div class="flex-1 space-y-2">
          <Skeleton class="h-4 w-2/3 rounded-2" />
          <Skeleton class="h-3 w-full rounded-2" />
          <Skeleton class="h-3 w-48 rounded-2" />
        </div>
      </div>
    </div>
    <RequestList v-else-if="requests.length" class="mt-4" :requests="requests" :show-trend="sort === 'trending'" />

    <div v-else class="flex flex-col items-center gap-3 py-16 text-center">
      <div class="rounded-full bg-surface-gray-2 p-3 text-ink-gray-5">
        <span class="lucide-lightbulb size-6" aria-hidden="true" />
      </div>
      <p class="text-base text-ink-gray-7">No requests match</p>
      <p class="text-sm text-ink-gray-5">Try another product or search, or post the first one.</p>
      <Button variant="solid" icon-left="lucide-plus" label="New request" class="mt-2" @click="openNew" />
    </div>
  </div>

  <RequestDialog
    v-model:open="showNew"
    :default-product="product === 'all' ? null : product"
    @saved="(id) => router.push(`/requests/${id}`)"
  />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Select, Skeleton, TabButtons, TextInput } from 'frappe-ui'
import AppHeader from '@/components/AppHeader.vue'
import RequestDialog from '@/components/RequestDialog.vue'
import RequestList from '@/components/requests/RequestList.vue'
import { listProducts, useFeatureRequests } from '@/api'
import { useQueryParam } from '@/composables/useQueryParam'
import { useRequireLogin } from '@/composables/useRequireLogin'

const SORTS = [
  { value: 'top', label: 'Top' },
  { value: 'trending', label: 'Trending' },
  { value: 'new', label: 'New' },
]

const router = useRouter()
const requireLogin = useRequireLogin()

const sort = useQueryParam('sort', 'top')
const product = useQueryParam('product', 'all')
const query = ref('')
const showNew = ref(false)

const productOptions = computed(() => [
  { label: 'All products', value: 'all' },
  ...listProducts().map((p) => ({ label: p.name, value: p.id })),
])

const requestsResource = useFeatureRequests({ product, sort, query })
const requests = computed(() => requestsResource.data ?? [])

function openNew() {
  if (requireLogin()) showNew.value = true
}
</script>
