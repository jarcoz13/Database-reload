import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Stations from '../views/Stations.vue'
import Alerts from '../views/Alerts.vue'
import Reports from '../views/Reports.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/stations',
    name: 'Stations',
    component: Stations
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: Alerts
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
