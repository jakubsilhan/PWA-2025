<template>
  <div class="flex flex-col space-y-10 items-center justify-center min-h-screen bg-gray-100">
    <h1 class="text-center text-6xl text-green-600 font-bold">Chatster</h1>
    <div class="bg-white shadow-xl rounded-2xl p-8 w-96">
      <h1 class="text-2xl font-bold mb-6 text-center">Login</h1>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            required
            ref="emailInput"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200"
          />
          <p v-if="email && !$refs.emailInput.validity.valid" class="text-red-500 text-sm mt-1">
            Please enter a valid email address
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring focus:ring-blue-200"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-600 hover:bg-green-700 text-white rounded-lg py-2 transition disabled:opacity-50"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <p v-if="error" class="text-red-500 text-sm text-center mt-2">{{ error }}</p>
        <div class="flex items-center justify-center text-center">
          <p>
            Don't have an account yet? <br />
            <router-link to="/register" class="font-bold hover:text-gray-500"
              >Register now!</router-link
            >
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/utils/api'
import { wsService } from '@/utils/websocket'
import { setUsername } from '@/stores/userStore'

const router = useRouter()

const email = ref('')
const emailInput = ref(null)
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  //Try logging in user
  error.value = ''
  loading.value = true
  try {
    // Send credentials
    const data = await apiService.post('/users/login', {
      email: email.value,
      password: password.value,
    })
    setUsername(data.username)
    await wsService.connect()

    // Redirect on success
    router.push('/conversations')
  } catch (err) {
    const data = err.response?.data
    error.value = data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
