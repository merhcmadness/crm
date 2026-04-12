<template>
  <div :id="activity.name">
    <div class="mb-1 flex items-center justify-stretch gap-2 py-1 text-base">
      <div class="inline-flex items-center flex-wrap gap-1 text-ink-gray-5">
        <UserAvatar class="mr-1" :user="activity.owner" size="md" />
        <span class="font-medium text-ink-gray-8">
          {{ activity.owner_name }}
        </span>
        <span>{{ __('added a') }}</span>
        <span class="max-w-xs truncate font-medium text-ink-gray-8">
          {{ __('comment') }}
        </span>
      </div>
      <div class="ml-auto flex items-center gap-2 whitespace-nowrap">
        <Tooltip :text="formatDate(activity.creation)">
          <div class="text-sm text-ink-gray-5">
            {{ __(timeAgo(activity.creation)) }}
          </div>
        </Tooltip>
        <Dropdown
          :options="[
            {
              label: __('Delete'),
              icon: 'trash-2',
              onClick: () => deleteComment(activity.name),
            },
          ]"
          class="h-6 w-6"
        >
          <Button
            icon="more-horizontal"
            variant="ghosted"
            class="!h-6 !w-6"
          />
        </Dropdown>
      </div>
    </div>
    <div
      class="cursor-pointer rounded bg-surface-gray-1 px-3 py-[7.5px] text-base leading-6 transition-all duration-300 ease-in-out"
    >
      <div class="prose-f" v-html="activity.content" />
      <div v-if="activity.attachments.length" class="mt-2 flex flex-wrap gap-2">
        <AttachmentItem
          v-for="a in activity.attachments"
          :key="a.file_url"
          :label="a.file_name"
          :url="a.file_url"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import UserAvatar from '@/components/UserAvatar.vue'
import AttachmentItem from '@/components/AttachmentItem.vue'
import { Tooltip, Dropdown, Button, call, toast } from 'frappe-ui'
import { timeAgo, formatDate } from '@/utils'

defineProps({
  activity: { type: Object, default: () => ({}) },
})

const activities = defineModel({ type: Object })

async function deleteComment(name) {
  await toast.promise(
    call('frappe.client.delete', {
      doctype: 'Comment',
      name,
    }),
    {
      loading: __('Deleting comment...'),
      success: __('Comment deleted'),
      error: __('Failed to delete comment'),
    },
  )
  activities.value?.reload()
}
</script>
