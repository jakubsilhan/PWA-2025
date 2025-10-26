import { ref } from 'vue'

export const user = ref(null)

export function setUser(newUser) {
  user.value = newUser
}

export function clearUser() {
  user.value = null
}
