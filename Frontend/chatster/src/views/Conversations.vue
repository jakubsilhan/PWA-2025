<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <div class="flex flex-row justify-between p-4 shadow">
      <!-- Logo -->
      <p class="text-green-600 text-2xl font-bold align-middle">Chatster</p>
      <!-- Toolbar -->
      <div class="flex items-center space-x-4">
        <!-- Conversation search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="px-3 py-1 rounded-lg border border-gray-300 focus:outline-none focus:ring focus:ring-green-200 transition"
        />
        <!-- Add button -->
        <button
          @click="showModal = true"
          class="px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-white transition"
        >
          Add
        </button>
        <!-- Logout button -->
        <button
          @click="handleLogout"
          class="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700 transition"
        >
          LogOut
        </button>
      </div>
    </div>
    <!-- Conversations -->
    <ul>
      <ConversationItem
        v-for="c in filteredConversations"
        :key="c.id"
        :conversation="c"
        @select="openConversation"
        @delete="deleteConversation"
        class="py-2 shadow"
      />
      <li v-if="filteredConversations.length === 0" class="p-4 text-gray-500">
        No conversations found
      </li>
    </ul>
    <!-- Add modal -->
    <AddConversationModal :show="showModal" @close="showModal = false" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { wsService } from '@/utils/websocket'
import { apiService } from '@/utils/api'
import ConversationItem from '@/components/ConversationItem.vue'
import AddConversationModal from '@/components/AddConversationModal.vue'
import { clearUser, user } from '@/stores/userStore'

const router = useRouter()
const conversations = ref([])
const searchQuery = ref('')

// Modal vars
const showModal = ref(false)

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
  wsService.emit('join_conversation', { conversation_id: data.id })
}

const handleRemovedConversation = (data) => {
  // Remove conversation
  console.log('Removed converesation: ', data)
  const convIndex = conversations.value.findIndex((x) => x.id == data.id)
  conversations.value.splice(convIndex, 1)
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

const deleteConversation = async (conversation) => {
  const confirmed = window.confirm(`Are you sure you want to delete "${conversation.chat_name}"?`)
  if (!confirmed) return

  try {
    await apiService.post(`/conversations/conversations/${conversation.id}/remove_user`, {
      user_id: user.value.id,
    })
    conversations.value = conversations.value.filter((c) => c.id !== conversation.id)
  } catch (err) {
    console.error('Failed to delete conversation:', err)
    alert('Failed to delete conversation.')
  }
}

const handleLogout = async () => {
  await wsService.disconnect()
  clearUser()
  router.push('/')
}
</script>
