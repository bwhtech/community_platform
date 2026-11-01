<template>
  <AppHeader title="Products" />

  <div class="mx-auto max-w-[940px] px-3 pb-20 pt-5 sm:px-5">
    <p class="max-w-xl text-p-base text-ink-gray-6">
      Activity is tagged with a product by repo, Discuss category or School course. Product tags drive
      product-scoped badges and the product filter on feature requests. Activity from repos no product lists
      still earns points, just without a product tag.
    </p>

    <div class="-mx-3 mt-6 overflow-x-auto">
      <List class="min-w-[36rem] list-row-px-3" :columns="['minmax(0,14rem)', 'minmax(0,1fr)', '3rem']">
        <ListHeader>
          <ListHeaderCell>Product</ListHeaderCell>
          <ListHeaderCell>Mapped from</ListHeaderCell>
          <ListHeaderCell />
        </ListHeader>
        <ListRows :items="products" v-slot="{ item }">
          <ListRow class="py-3">
            <ListCell class="gap-2.5">
              <ProductLogo :product="item" size="md" />
              <span class="truncate text-base text-ink-gray-8">{{ item.name }}</span>
            </ListCell>
            <ListCell class="flex-wrap gap-1">
              <Badge v-for="repo in item.repos" :key="repo" :label="repo" variant="outline" />
              <Badge v-for="c in item.discussCategories" :key="c" :label="`Discuss: ${c}`" variant="subtle" />
              <Badge v-for="c in item.schoolCourses" :key="c" :label="`School: ${c}`" variant="subtle" theme="green" />
            </ListCell>
            <ListCell class="justify-end">
              <Button variant="ghost" icon="lucide-pencil" :aria-label="`Edit ${item.name}`" @click="edit(item)" />
            </ListCell>
          </ListRow>
        </ListRows>
      </List>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge, Button, dialog, toast } from 'frappe-ui'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import AppHeader from '@/components/AppHeader.vue'
import ProductLogo from '@/components/ProductLogo.vue'
import { listProducts, updateProduct } from '@/api'

const products = computed(() => listProducts())

function edit(product) {
  dialog.prompt({
    title: `Edit ${product.name}`,
    message: 'One per line. New mappings apply to new activity only.',
    fields: [
      { name: 'repos', label: 'GitHub repos', type: 'textarea', defaultValue: product.repos.join('\n') },
      { name: 'discussCategories', label: 'Discuss categories', type: 'textarea', defaultValue: product.discussCategories.join('\n') },
      { name: 'schoolCourses', label: 'School courses', type: 'textarea', defaultValue: product.schoolCourses.join('\n') },
    ],
    confirmLabel: 'Save',
    onConfirm: async ({ values }) => {
      await updateProduct(product.id, {
        repos: lines(values.repos),
        discussCategories: lines(values.discussCategories),
        schoolCourses: lines(values.schoolCourses),
      })
      toast.success(`${product.name} saved`)
    },
  })
}

function lines(text) {
  return text.split('\n').map((l) => l.trim()).filter(Boolean)
}
</script>
