<template>
  <li
    class="p-4 hover:bg-gray-200 cursor-pointer"
    @click="$emit('select', conversation)"
    v-if="conversation"
  >
    <div class="flex justify-between items-center">
      <span class="font-semibold">{{ conversation.chat_name }}</span>
      <span class="text-xs text-gray-500">
        {{ formatTime(conversation.last_message_time) }}
      </span>
    </div>
    <p class="text-gray-700 text-sm truncate">
      <span class="font-medium text-gray-800" v-if="conversation.last_message_username">
        {{ conversation.last_message_username }}:
      </span>
      {{ conversation.last_message || 'No messages yet' }}
    </p>
  </li>
</template>

<script setup>
const props = defineProps({
  conversation: {
    type: Object,
    required: true,
    defalt: null,
  },
})

// Time conversions
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
