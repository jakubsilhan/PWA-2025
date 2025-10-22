<template>
  <div class="flex flex-col h-screen bg-gray-100">
    <div class="flex flex-row justify-between p-4 shadow-md bg-white z-10">
      <button
        @click="handleReturn"
        class="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700 transition"
      >
        Return
      </button>
      <div class="flex items-center space-x-4">
        <p class="text-green-600 text-2xl font-bold align-middle">{{ conversation.chat_name }}</p>
      </div>
    </div>

    <div ref="messagesContainer" class="flex-1 overflow-y-auto flex flex-col">
      <div ref="topSentinel"></div>
      <ul>
        <MessageItem v-for="m in messages" :key="m.id" :message="m" class="py-2 px-4" />
      </ul>
      <div class="text-center p-10 italic" v-if="loading">Loading older messages...</div>
    </div>

    <div class="p-5 shadow-inner bg-white z-10">
      <div class="flex flex-row space-x-2">
        <textarea
          @keyup.enter.prevent.exact="sendMessage"
          v-model="message"
          rows="1"
          placeholder="Message..."
          class="flex-1 px-3 py-1 rounded-lg border border-gray-300 focus:outline-none focus:ring focus:ring-green-200 transition resize-y min-h-10 max-h-32 overflow-auto"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!message || !message.trim()"
          class="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { wsService } from '@/utils/websocket'
import { apiService } from '@/utils/api'
import MessageItem from '@/components/MessageItem.vue'

const router = useRouter()
const route = useRoute()
const conversation = ref({})
const message = ref('')
const messages = ref([])

// Infinite scroll
const loading = ref(false)
const page = ref(0)
const limit = ref(10)
const messagesContainer = ref(null)
const topSentinel = ref(null)
let observer = null

onMounted(async () => {
  wsService.on('new_message', handleNewMessage)
  // Retrieve conversation details and query for messages
  if (route.query.data) {
    conversation.value = JSON.parse(route.query.data)

    try {
      await loadOlderMessages()
      await nextTick()
      scrollToBottom()
      console.log(messages.value)
    } catch (err) {
      console.error('Failed to load conversations: ', err)
    }
  }
  // Create a oberver for infinite scroll and add message loading callback
  observer = new IntersectionObserver(
    (entries) => {
      const [entry] = entries
      if (entry.isIntersecting && !loading.value) {
        loadOlderMessages()
      }
    },
    {
      root: messagesContainer.value,
      threshold: 0.1,
    },
  )
  // Connect observer to sentinel component
  if (topSentinel.value) {
    observer.observe(topSentinel.value)
  }
})

onUnmounted(() => {
  wsService.off('new_message', handleNewMessage)
  observer.disconnect()
})

// Listeners
const sendMessage = async () => {
  if (!message.value || !message.value.trim()) return
  wsService.emit('send_message', { conversation_id: conversation.value.id, message: message.value })
  message.value = ''
}

const handleNewMessage = async (data) => {
  console.log('New message received: ', data)
  const container = messagesContainer.value
  const atBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 20 // check whether user is within autoscroll margin
  messages.value.push(data)
  await nextTick()
  if (atBottom) scrollToBottom()
}

// Utils
const handleReturn = () => {
  router.push('/conversations')
}

const scrollToBottom = () => {
  // Utility to scroll to botom of chats
  const container = messagesContainer.value
  if (container) container.scrollTop = container.scrollHeight
}

const loadOlderMessages = async () => {
  if (loading.value) return
  loading.value = true
  try {
    // Query for messages
    const data = await apiService.get(
      `/conversations/conversations/${conversation.value.id}/messages`,
      { limit: limit.value, offset: 0 + page.value * limit.value },
    )
    if (data.messages.length) {
      const container = messagesContainer.value
      const prevHeight = container.scrollHeight
      // Prepend older messages
      messages.value = [
        ...data.messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)),
        ...messages.value,
      ]

      await nextTick()
      // Retain scroll position
      container.scrollTop = container.scrollHeight - prevHeight
      page.value++
    }
    console.log('Loaded more messages')
  } catch (err) {
    console.error('Failed to load older messages', err)
  } finally {
    loading.value = false
  }
}
</script>
