import Chat from '@/views/Chat.vue'
import Conversations from '@/views/Conversations.vue'
import Login from '@/views/Login.vue'
import Registration from '@/views/Registration.vue'
import { createRouter, createWebHistory } from 'vue-router'

// TODO add authentication checks: https://medium.com/@tahnyybelguith/authentication-and-authorization-implementation-with-vue-js-6afcbb821c85
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // history: createWebHashHistory('/jakub.silhan/sp/'),
  routes: [
    { path: '/', component: Login },
    { path: '/register', component: Registration },
    { path: '/conversations', component: Conversations },
    { path: '/chat', component: Chat },
  ],
})

export default router
