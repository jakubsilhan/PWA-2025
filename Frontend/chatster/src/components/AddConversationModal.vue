<template>
  <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
    <div class="bg-white rounded-lg shadow-lg w-96 p-6">
      <h2 class="text-xl font-semibold mb-4">Create Conversation</h2>

      <!-- Conversation name -->
      <input
        v-model="conversationName"
        type="text"
        placeholder="Conversation name"
        class="w-full px-3 py-2 mb-4 border rounded focus:outline-none focus:ring focus:ring-green-200"
      />

      <!-- Search bar -->
      <label class="font-medium mb-2 block">Add Users</label>
      <input
        v-model="userQuery"
        @input="searchUsers"
        type="text"
        placeholder="Search by username"
        class="w-full px-3 py-2 mb-2 border rounded focus:outline-none focus:ring focus:ring-green-200"
      />

      <!-- Search results -->
      <ul v-if="searchResults.length > 0" class="border rounded max-h-40 overflow-y-auto mb-4">
        <li
          v-for="user in searchResults"
          :key="user.id"
          @click="addUser(user)"
          class="px-3 py-2 hover:bg-green-100 cursor-pointer"
        >
          {{ user.username }} ({{ user.email }})
        </li>
      </ul>

      <!-- Selected users -->
      <div class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="user in selectedUsers"
          :key="user.id"
          class="bg-green-200 px-2 py-1 rounded flex items-center gap-1"
        >
          {{ user.username }}
          <button @click="removeUser(user)" class="text-red-600 font-bold">×</button>
        </span>
      </div>

      <!-- Control buttons -->
      <div class="flex justify-end space-x-2">
        <button @click="cancel" class="px-3 py-1 rounded bg-gray-300 hover:bg-gray-400 transition">
          Cancel
        </button>
        <button
          @click="submit"
          class="px-3 py-1 rounded bg-green-600 hover:bg-green-700 text-white transition"
        >
          Create
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { apiService } from '@/utils/api'

const props = defineProps({
  show: { type: Boolean, required: true },
})

const emit = defineEmits(['close', 'created'])

const conversationName = ref('')
const userQuery = ref('')
const searchResults = ref([])
const selectedUsers = ref([])

// Dynamic user search
const searchUsers = async () => {
  if (!userQuery.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    const res = await apiService.get('users/search', { username: userQuery.value })
    searchResults.value = res.profiles.filter(
      (user) => !selectedUsers.value.find((u) => u.id === user.id),
    )
  } catch (err) {
    console.error('User search failed:', err)
  }
}

// Add and remove users
const addUser = (user) => {
  selectedUsers.value.push(user)
  searchResults.value = searchResults.value.filter((u) => u.id !== user.id)
  // searchResults.value = []
  userQuery.value = ''
}

const removeUser = (user) => {
  selectedUsers.value = selectedUsers.value.filter((u) => u.id !== user.id)
}

// Cancel modal
const cancel = () => {
  emit('close')
  conversationName.value = ''
  userQuery.value = ''
  searchResults.value = []
  selectedUsers.value = []
}

// Submit conversation
const submit = async () => {
  if (!conversationName.value || selectedUsers.value.length === 0) {
    alert('Please provide a conversation name and add at least one user.')
    return
  }
  try {
    const payload = {
      chat_name: conversationName.value,
      participant_ids: selectedUsers.value.map((u) => u.id),
    }

    const res = await apiService.post('conversations/conversations', payload)
    cancel()
  } catch (err) {
    console.error('Failed to create conversation:', err)
  }
}
</script>
