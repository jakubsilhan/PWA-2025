import { ref } from 'vue'

export const username = ref('')

export function setUsername(newUsername) {
  username.value = newUsername
}

export function clearUsername() {
  username.value = ''
}
