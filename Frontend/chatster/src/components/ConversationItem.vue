<template>
  <li
    class="p-4 hover:bg-gray-200 cursor-pointer"
    @click="$emit('select', conversation)"
    v-if="conversation"
  >
    <div class="flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <span class="font-semibold">{{ conversation.chat_name }}</span>
      </div>
      <span class="text-xs text-gray-500">
        {{ formatTime(conversation.last_message_time) }}
        <button
          @click.stop="$emit('delete', conversation)"
          class="text-red-500 hover:text-red-700 font-bold px-2"
          title="Delete conversation"
        >
          ×
        </button>
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
    default: null,
  },
})

// Time conversions
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('es-ES', { hour12: false })
}
</script>
