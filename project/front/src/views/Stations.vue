<template>
  <div class="stations">
    <h1>Monitoring Stations</h1>
    <div class="stations-container">
      <div class="card" v-for="station in stations" :key="station.id">
        <h3>{{ station.name }}</h3>
        <p><strong>Location:</strong> {{ station.city }}, {{ station.country }}</p>
        <p><strong>Coordinates:</strong> {{ station.latitude }}, {{ station.longitude }}</p>
        <button @click="viewStation(station.id)">View Details</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Stations',
  setup() {
    const stations = ref([])

    const loadStations = async () => {
      // TODO: Replace with actual API call
      stations.value = [
        { id: 1, name: 'Station A', city: 'Bogotá', country: 'Colombia', latitude: 4.6097, longitude: -74.0817 },
        { id: 2, name: 'Station B', city: 'Medellín', country: 'Colombia', latitude: 6.2442, longitude: -75.5812 }
      ]
    }

    const viewStation = (id) => {
      console.log('View station:', id)
      // TODO: Navigate to station details
    }

    onMounted(() => {
      loadStations()
    })

    return {
      stations,
      viewStation
    }
  }
}
</script>

<style scoped>
.stations-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}
</style>
