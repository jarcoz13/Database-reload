<template>
  <div class="home">
    <div class="hero">
      <h1>🌍 Air Quality Monitor</h1>
      <p>Real-time air quality monitoring and analysis system</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>Stations</h3>
        <p class="stat-number">{{ stats.stations }}</p>
        <p class="stat-label">Active monitoring stations</p>
      </div>
      <div class="stat-card">
        <h3>Readings</h3>
        <p class="stat-number">{{ stats.readings }}</p>
        <p class="stat-label">Total measurements</p>
      </div>
      <div class="stat-card">
        <h3>Users</h3>
        <p class="stat-number">{{ stats.users }}</p>
        <p class="stat-label">Registered users</p>
      </div>
      <div class="stat-card">
        <h3>Alerts</h3>
        <p class="stat-number">{{ stats.alerts }}</p>
        <p class="stat-label">Active alerts</p>
      </div>
    </div>

    <div class="info-section">
      <div class="card">
        <h2>About the System</h2>
        <p>
          This air quality monitoring system provides real-time data from multiple
          monitoring stations, helping citizens, researchers, and administrators
          make informed decisions about air quality.
        </p>
      </div>

      <div class="card">
        <h2>Features</h2>
        <ul>
          <li>Real-time air quality data from multiple stations</li>
          <li>Personalized alerts for air quality thresholds</li>
          <li>Historical data analysis and reporting</li>
          <li>Health recommendations based on AQI</li>
          <li>Geographic visualization of pollution levels</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Home',
  setup() {
    const stats = ref({
      stations: 0,
      readings: 0,
      users: 0,
      alerts: 0
    })

    const loadStats = async () => {
      try {
        // TODO: Replace with actual API endpoints
        stats.value = {
          stations: 45,
          readings: 12580,
          users: 234,
          alerts: 12
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats
    }
  }
}
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 3rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #667eea;
  margin: 0.5rem 0;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

ul {
  list-style-position: inside;
  line-height: 1.8;
}

li {
  margin-bottom: 0.5rem;
}
</style>
