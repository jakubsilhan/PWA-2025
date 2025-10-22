<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <div class="flex flex-row justify-between p-4 shadow">
      <p class="text-green-600 text-2xl font-bold align-middle">Chatster</p>
      <div class="flex items-center space-x-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="px-3 py-1 rounded-lg border border-gray-300 focus:outline-none focus:ring focus:ring-green-200 transition"
        />
        <button class="px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-white transition">
          Add
        </button>
        <button
          @click="handleLogout"
          class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 transition"
        >
          LogOut
        </button>
      </div>
    </div>
    <ul>
      <ConversationItem
        v-for="c in filteredConversations"
        :key="c.id"
        :conversation="c"
        @select="openConversation"
        class="py-2 shadow"
      />
      <li v-if="filteredConversations.length === 0" class="p-4 text-gray-500">
        No conversations found
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { wsService } from '@/utils/websocket'
import { apiService } from '@/utils/api'
import ConversationItem from '@/components/ConversationItem.vue'
import { clearUsername } from '@/stores/userStore'

const router = useRouter()
const conversations = ref([])
const searchQuery = ref('')

onMounted(async () => {
  // Mount callbacks to websocket
  wsService.on('new_conversation', handleNewConversation)
  wsService.on('new_message', handleNewMessage)
  // Query conversations
  try {
    const data = await apiService.get('/conversations/conversations')
    conversations.value = data.conversations.sort(
      (a, b) => new Date(b.last_message_time) - new Date(a.last_message_time),
    )
  } catch (err) {
    console.error('Failed to load conversations: ', err)
  }
})

onUnmounted(() => {
  wsService.off('new_conversation', handleNewConversation)
  wsService.off('new_message', handleNewMessage)
})

const filteredConversations = computed(() => {
  // Filtering through conversation names
  if (!searchQuery.value) return conversations.value // keep all
  const q = searchQuery.value.toLowerCase()
  return conversations.value.filter((c) => c.chat_name.toLowerCase().includes(q))
})

const handleNewConversation = (data) => {
  // Add new conversation to top
  console.log('New conversation received: ', data)
  conversations.value.unshift(data)
}

const handleNewMessage = (data) => {
  console.log('New message received: ', data)
  const convIndex = conversations.value.findIndex((x) => x.id == data.conversation_id)
  if (convIndex !== -1) {
    // Update conversation with new data
    const conv = conversations.value[convIndex]
    Object.assign(conv, {
      last_message: data.content,
      last_message_username: data.sender,
      last_message_time: data.timestamp,
    })
    // Remove conversation and add to top
    conversations.value.splice(convIndex, 1)
    conversations.value.unshift(conv)
  }
}

const openConversation = (conversation) => {
  router.push({ path: '/chat', query: { data: JSON.stringify(conversation) } })
}

const handleLogout = async () => {
  await wsService.disconnect()
  clearUsername()
  router.push('/')
}
</script>
