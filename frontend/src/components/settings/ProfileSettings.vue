<template>
  <SettingsHeader title="My profile" description="Shown on your public profile. Defaults come from GitHub.">
    <template #actions>
      <Button label="View profile" :route="`/u/${currentUser}`" @click="settingsOpen = false" />
      <Button variant="solid" label="Save" :loading="saving" :disabled="!dirty" @click="save" />
      <Button v-if="isMobile" variant="ghost" icon="lucide-x" aria-label="Close settings" @click="settingsOpen = false" />
    </template>
  </SettingsHeader>

  <FadingSettingsBody v-if="!profile">
    <div class="space-y-4 pt-4" aria-busy="true">
      <div v-for="i in 5" :key="i" class="space-y-1.5">
        <Skeleton class="h-3 w-20 rounded-2" />
        <Skeleton class="h-7 w-full rounded-2" />
      </div>
    </div>
  </FadingSettingsBody>
  <FadingSettingsBody v-else>
    <FileUploader
      class="pt-4"
      :private="false"
      file-types="image/png,image/jpeg,image/gif,image/webp"
      :validate-file="validateImage"
      @success="(file) => runPhoto(file.file_url)"
    >
      <template #default="{ openFileSelector, error, uploading }">
        <div class="flex items-center gap-3">
          <div class="group relative size-14 shrink-0">
            <Avatar class="!size-14" :image="profile.avatar" :label="profile.fullName" />
            <Tooltip :hover-delay="0" side="bottom" :text="profile.avatar ? 'Change photo' : 'Upload photo'">
              <button
                type="button"
                class="absolute inset-0 rounded-full"
                :aria-label="profile.avatar ? 'Change photo' : 'Upload photo'"
                @click="openFileSelector"
              />
            </Tooltip>
            <Tooltip v-if="profile.avatar" :hover-delay="0" side="bottom" text="Remove photo">
              <button
                type="button"
                class="absolute -right-1 -top-1 flex size-4 items-center justify-center rounded-full bg-surface-base opacity-0 outline outline-black-overlay-50 duration-300 ease-in-out hover:bg-surface-gray-2 focus-visible:opacity-100 group-hover:opacity-100"
                aria-label="Remove photo"
                @click="runPhoto(null)"
              >
                <span class="lucide-x size-3.5 text-ink-gray-4" aria-hidden="true" />
              </button>
            </Tooltip>
            <div
              v-if="uploading || savingPhoto"
              class="absolute inset-0 flex items-center justify-center rounded-full bg-black-overlay-200"
            >
              <LoadingIndicator class="size-4 text-ink-base" />
            </div>
          </div>
          <div class="min-w-0">
            <div v-if="!editingName" class="flex items-center gap-1">
              <span class="truncate text-2xl font-semibold text-ink-gray-8">{{ profile.fullName }}</span>
              <Button variant="ghost" size="sm" icon="lucide-pencil" aria-label="Edit name" @click="editName" />
            </div>
            <div v-else class="flex items-center gap-1">
              <TextInput
                ref="nameInput"
                v-model="nameDraft"
                aria-label="Name"
                @keydown.enter="saveName"
                @keydown.esc.stop="editingName = false"
              />
              <Button variant="outline" icon="lucide-check" aria-label="Save name" :loading="savingName" @click="saveName" />
            </div>
            <p class="text-p-sm text-ink-gray-6">{{ profile.email }}</p>
            <ErrorMessage :message="error" />
          </div>
        </div>
      </template>
    </FileUploader>

    <div class="space-y-4 pb-8 pt-6">
      <FormControl v-model="form.bio" type="textarea" label="Bio" :rows="3" />
      <div class="grid gap-4 sm:grid-cols-2">
        <FormControl v-model="form.company" label="Company" />
        <FormControl v-model="form.location" label="Location" />
      </div>
      <FormControl v-model="form.website" label="Website" placeholder="https://" />
      <div class="grid gap-4 sm:grid-cols-3">
        <FormControl v-model="form.x" label="X handle" />
        <FormControl v-model="form.linkedin" label="LinkedIn" />
        <FormControl v-model="form.youtube" label="YouTube" />
      </div>
      <MultiSelect v-model="form.products" label="Products I work with" :options="productOptions" placeholder="Pick products" />
    </div>

    <h3 class="text-lg-semibold text-ink-gray-8">Connected accounts</h3>
    <p class="mt-1 text-p-sm text-ink-gray-5">Where your points come from.</p>
    <div class="mt-2 divide-y divide-outline-gray-1">
      <SettingsRow
        :title="`GitHub · @${profile.login}`"
        :description="`Issues, merged PRs and reviews in the frappe org. ${profile.lastGithubSync ? `Last synced ${timeAgo(profile.lastGithubSync)}.` : 'Not synced yet.'}`"
      >
        <Button label="Sync now" icon-left="lucide-refresh-cw" :loading="syncing" @click="runSync()" />
      </SettingsRow>
      <SettingsRow
        :title="profile.discussUsername ? `Discuss · @${profile.discussUsername}` : 'Discuss'"
        :description="profile.discussUsername ? 'Accepted solutions on discuss.frappe.io.' : 'Connect to earn points for accepted solutions.'"
      >
        <Button v-if="profile.discussUsername" label="Disconnect" @click="disconnect" />
        <Button v-else variant="solid" label="Connect" :loading="connecting" @click="connect" />
      </SettingsRow>
      <SettingsRow
        title="Events and Frappe School"
        :description="`Matched by your verified GitHub emails: ${profile.emails.join(', ')}.`"
      >
        <Badge theme="green" label="Automatic" />
      </SettingsRow>
    </div>

    <template v-if="profile.hasPassword">
      <h3 class="mt-8 text-lg-semibold text-ink-gray-8">Security</h3>
      <div class="mt-2 divide-y divide-outline-gray-1">
        <SettingsRow title="Password" description="Change the password you use to log in.">
          <Button label="Change password" @click="showPassword = true" />
        </SettingsRow>
      </div>
    </template>
  </FadingSettingsBody>

  <ChangePasswordDialog v-model:open="showPassword" />
</template>

<script setup>
import { computed, nextTick, reactive, ref, useTemplateRef, watch } from 'vue'
import {
  Avatar,
  Badge,
  Button,
  ErrorMessage,
  FileUploader,
  FormControl,
  LoadingIndicator,
  MultiSelect,
  SettingsHeader,
  SettingsRow,
  Skeleton,
  TextInput,
  Tooltip,
  dialog,
} from 'frappe-ui'
import ChangePasswordDialog from '@/components/settings/ChangePasswordDialog.vue'
import FadingSettingsBody from '@/components/settings/FadingSettingsBody.vue'
import {
  connectDiscuss,
  disconnectDiscuss,
  listProducts,
  syncGithub,
  updateName,
  updatePhoto,
  updateProfile,
  useMyProfile,
} from '@/api'
import { useAction } from '@/composables/useAction'
import { useIsMobile } from '@/composables/useIsMobile'
import { settingsOpen } from '@/composables/useSettings'
import { currentUser } from '@/session'
import { timeAgo } from '@/utils/dates'

const FIELDS = ['bio', 'company', 'location', 'website', 'x', 'linkedin', 'youtube', 'products']

// The bare dialog has no close button, and phones have no Escape key.
const isMobile = useIsMobile()
const profileResource = useMyProfile()
const profile = computed(() => profileResource.data)
const form = reactive(snapshot(null))

const productOptions = computed(() => listProducts().map((p) => ({ label: p.name, value: p.id })))
const dirty = computed(() => profile.value && JSON.stringify(form) !== JSON.stringify(snapshot(profile.value)))

// Fill the form when the profile loads, and again after each save.
watch(profile, (p) => Object.assign(form, snapshot(p)))

const { run: runSave, loading: saving } = useAction(updateProfile, { success: 'Profile saved' })
const { run: runSync, loading: syncing } = useAction(syncGithub, {
  success: 'GitHub sync started. New activity shows up in a few minutes.',
})
const { run: runConnect, loading: connecting } = useAction(connectDiscuss, { success: 'Discuss connected' })

function snapshot(p) {
  return Object.fromEntries(FIELDS.map((f) => [f, f === 'products' ? [...(p?.[f] ?? [])] : (p?.[f] ?? '')]))
}

function save() {
  runSave({ ...form, products: [...form.products] })
}

// Name and photo save on their own, like the rest of the Frappe apps.
const editingName = ref(false)
const nameDraft = ref('')
const nameInput = useTemplateRef('nameInput')
const showPassword = ref(false)
const { run: runName, loading: savingName } = useAction(updateName, { success: 'Name updated' })
const { run: runPhoto, loading: savingPhoto } = useAction(updatePhoto)

function editName() {
  nameDraft.value = profile.value.fullName
  editingName.value = true
  nextTick(() => nameInput.value?.focus())
}

async function saveName() {
  const name = nameDraft.value.trim()
  if (name && name !== profile.value.fullName) await runName(name)
  editingName.value = false
}

function validateImage(file) {
  if (!file.type.match(/^image\/(png|jpeg|gif|webp)$/)) return 'Only PNG, JPEG, GIF or WebP images'
}

// TODO: switch to the Discourse User API Key flow so the username is
// verified on discuss.frappe.io instead of typed in.
function connect() {
  dialog.prompt({
    title: 'Connect Discuss',
    message: 'Your accepted solutions on discuss.frappe.io will start earning points.',
    fields: [{ name: 'username', label: 'Discuss username', required: true, defaultValue: profile.value.login.replace('-', '_') }],
    confirmLabel: 'Connect',
    onConfirm: ({ values }) => runConnect(values.username),
  })
}

function disconnect() {
  dialog.confirm({
    title: 'Disconnect Discuss?',
    message: 'Points you already earned stay. New solutions stop counting until you connect again.',
    confirmLabel: 'Disconnect',
    theme: 'red',
    onConfirm: () => disconnectDiscuss(),
  })
}
</script>
