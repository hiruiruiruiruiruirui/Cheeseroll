import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/result/:id',
    name: 'Result',
    component: () => import('../views/ResultView.vue'),
    props: true,
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
  },
  {
    path: '/plans',
    name: 'Plans',
    component: () => import('../views/PlansView.vue'),
  },
  {
    path: '/mine',
    name: 'Mine',
    component: () => import('../views/MineView.vue'),
  },
  {
    path: '/wrong-answers',
    name: 'WrongAnswers',
    component: () => import('../views/WrongAnswersView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/share/:code',
    name: 'Share',
    component: () => import('../views/ShareView.vue'),
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
