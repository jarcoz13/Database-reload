<template>
  <div class="alerts">
    <h1>Your Alerts</h1>
    <div class="alerts-container">
      <div class="card" v-for="alert in alerts" :key="alert.id">
        <h3>{{ alert.pollutant }}</h3>
        <p><strong>Station:</strong> {{ alert.station }}</p>
        <p><strong>Threshold:</strong> {{ alert.threshold }}</p>
        <p><strong>Status:</strong> <span :class="alert.is_active ? 'active' : 'inactive'">
          {{ alert.is_active ? 'Active' : 'Inactive' }}
        </span></p>
        <button @click="toggleAlert(alert.id)">
          {{ alert.is_active ? 'Deactivate' : 'Activate' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Alerts',
  setup() {
    const alerts = ref([])

    const loadAlerts = async () => {
      // TODO: Replace with actual API call
      alerts.value = [
        { id: 1, pollutant: 'PM2.5', station: 'Station A', threshold: 50, is_active: true },
        { id: 2, pollutant: 'O3', station: 'Station B', threshold: 100, is_active: false }
      ]
    }

    const toggleAlert = (id) => {
      const alert = alerts.value.find(a => a.id === id)
      if (alert) {
        alert.is_active = !alert.is_active
      }
    }

    onMounted(() => {
      loadAlerts()
    })

    return {
      alerts,
      toggleAlert
    }
  }
}
</script>

<style scoped>
.alerts-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.active {
  color: #22c55e;
  font-weight: bold;
}

.inactive {
  color: #ef4444;
  font-weight: bold;
}
</style>
