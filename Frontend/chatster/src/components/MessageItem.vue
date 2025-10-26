<template>
  <li v-if="message" class="mb-2 flex" :class="isOwnMessage ? 'justify-end' : 'justify-start'">
    <div
      class="p-3 rounded-lg max-w-3xl break-words"
      :class="isOwnMessage ? 'bg-green-100 rounded-tr-none' : 'bg-white rounded-tl-none shadow'"
    >
      <span class="font-semibold text-sm">{{ message.sender_name }}</span>
      <p class="text-gray-700 text-sm whitespace-pre-wrap">{{ message.content }}</p>
      <span class="text-xs text-gray-500">{{ formatTime(message.timestamp) }}</span>
    </div>
  </li>
</template>

<script setup>
import { user } from '@/stores/userStore'
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
    default: null,
  },
})

// Own message special display
const isOwnMessage = computed(() => user.value.username === props.message.sender_name)

// Time conversions
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
