<template>
  <div class="station-details">
    <div class="header">
      <button @click="goBack" class="back-btn">← Back to Stations</button>
      <button @click="loadStationData" class="refresh-btn" :disabled="loading">
        {{ loading ? 'Loading...' : '🔄 Refresh' }}
      </button>
    </div>

    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <div v-if="loading && !station" class="loading">Loading station details...</div>

    <div v-else-if="station" class="content">
      <!-- Station Header -->
      <div class="station-header-card">
        <div class="title-section">
          <h1>{{ station.name }}</h1>
          <span class="status-badge" :class="{ active: station.is_active }">
            {{ station.is_active ? '● Active' : '○ Inactive' }}
          </span>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="icon">📍</span>
            <div>
              <div class="label">Location</div>
              <div class="value">{{ station.city }}, {{ station.country }}</div>
            </div>
          </div>
          <div class="info-item">
            <span class="icon">🗺️</span>
            <div>
              <div class="label">Coordinates</div>
              <div class="value">{{ station.latitude.toFixed(4) }}, {{ station.longitude.toFixed(4) }}</div>
            </div>
          </div>
          <div class="info-item">
            <span class="icon">🏢</span>
            <div>
              <div class="label">Provider</div>
              <div class="value">{{ station.provider_name || 'Unknown' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Section -->
      <div class="map-card">
        <h2>📍 Station Location</h2>
        <div class="map-container" ref="mapContainer">
          <iframe
            :src="`https://www.openstreetmap.org/export/embed.html?bbox=${station.longitude-0.01},${station.latitude-0.01},${station.longitude+0.01},${station.latitude+0.01}&layer=mapnik&marker=${station.latitude},${station.longitude}`"
            frameborder="0"
            scrolling="no"
            marginheight="0"
            marginwidth="0"
            class="map-iframe">
          </iframe>
          <div class="map-links">
            <a :href="`https://www.openstreetmap.org/?mlat=${station.latitude}&mlon=${station.longitude}#map=15/${station.latitude}/${station.longitude}`" 
               target="_blank" 
               class="map-link">
              View Larger Map →
            </a>
            <a :href="`https://www.google.com/maps?q=${station.latitude},${station.longitude}`" 
               target="_blank" 
               class="map-link">
              Open in Google Maps →
            </a>
          </div>
        </div>
      </div>

      <!-- Current Readings -->
      <div class="readings-card">
        <h2>📊 Current Air Quality Readings</h2>
        
        <div v-if="readings.length === 0" class="no-readings">
          <p>No recent readings available for this station.</p>
          <p>Data may be processing or the station may be temporarily offline.</p>
        </div>

        <div v-else class="readings-grid">
          <div v-for="reading in readings" :key="reading.id" 
               class="reading-card"
               :class="getAQIClass(reading.aqi)">
            <div class="reading-header">
              <span class="pollutant-name">{{ reading.pollutant_name }}</span>
              <span class="reading-time">{{ formatTime(reading.timestamp) }}</span>
            </div>
            <div class="reading-value">
              {{ reading.value.toFixed(2) }} <span class="unit">{{ reading.unit }}</span>
            </div>
            <div class="reading-aqi" v-if="reading.aqi">
              <span class="aqi-label">AQI:</span>
              <span class="aqi-value">{{ reading.aqi }}</span>
              <span class="aqi-category">{{ getAQICategory(reading.aqi) }}</span>
            </div>
            <div class="provider-badge">
              📡 {{ reading.provider_name || 'Unknown' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Historical Data Preview -->
      <div class="history-card">
        <h2>📈 Recent Trend</h2>
        <p class="history-note">
          View comprehensive historical data and charts in the 
          <router-link to="/reports" class="inline-link">Reports</router-link> section.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default {
  name: 'StationDetails',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const station = ref(null)
    const readings = ref([])
    const loading = ref(false)
    const error = ref(null)
    const mapContainer = ref(null)

    const stationId = route.params.id

    const loadStation = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stations`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include'
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        
        const stations = await response.json()
        const foundStation = stations.find(s => s.id === parseInt(stationId))
        
        if (!foundStation) {
          throw new Error('Station not found')
        }
        
        return foundStation
      } catch (err) {
        console.error('Error loading station:', err)
        throw err
      }
    }

    const loadReadings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/readings/current`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include'
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        
        const allReadings = await response.json()
        return allReadings.filter(r => r.station_id === parseInt(stationId))
      } catch (err) {
        console.error('Error loading readings:', err)
        return []
      }
    }

    const loadStationData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const [stationData, readingsData] = await Promise.all([
          loadStation(),
          loadReadings()
        ])

        station.value = stationData
        readings.value = readingsData.sort((a, b) => {
          // Sort by AQI descending
          return (b.aqi || 0) - (a.aqi || 0)
        })
      } catch (err) {
        error.value = `Failed to load station details: ${err.message}`
        console.error('Error:', err)
      } finally {
        loading.value = false
      }
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return 'N/A'
      const date = new Date(timestamp)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getAQIClass = (aqi) => {
      if (!aqi) return ''
      if (aqi <= 50) return 'aqi-good'
      if (aqi <= 100) return 'aqi-moderate'
      if (aqi <= 150) return 'aqi-unhealthy-sensitive'
      if (aqi <= 200) return 'aqi-unhealthy'
      if (aqi <= 300) return 'aqi-very-unhealthy'
      return 'aqi-hazardous'
    }

    const getAQICategory = (aqi) => {
      if (!aqi) return 'Unknown'
      if (aqi <= 50) return 'Good'
      if (aqi <= 100) return 'Moderate'
      if (aqi <= 150) return 'Unhealthy for Sensitive'
      if (aqi <= 200) return 'Unhealthy'
      if (aqi <= 300) return 'Very Unhealthy'
      return 'Hazardous'
    }

    const goBack = () => {
      router.push('/stations')
    }

    onMounted(() => {
      loadStationData()
    })

    return {
      station,
      readings,
      loading,
      error,
      mapContainer,
      loadStationData,
      formatTime,
      getAQIClass,
      getAQICategory,
      goBack
    }
  }
}
</script>

<style scoped>
.station-details {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: var(--accent-purple);
  padding: 1.5rem;
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
}

.back-btn {
  background: white;
  color: var(--text-color);
  border: var(--border-width) solid var(--border-color);
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.back-btn:hover {
  background: var(--accent-yellow);
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
}

.refresh-btn {
  background: var(--accent-blue);
  color: white;
  border: var(--border-width) solid var(--border-color);
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.refresh-btn:hover:not(:disabled) {
  background: var(--accent-blue);
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
}

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.5rem;
  font-weight: bold;
  background: white;
  border: var(--border-width) solid var(--border-color);
  margin: 2rem 0;
}

.error-message {
  background: var(--accent-red);
  border: var(--border-width) solid var(--border-color);
  color: white;
  padding: 1rem;
  font-weight: bold;
  margin-bottom: 1rem;
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Station Header Card */
.station-header-card {
  background: white;
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  padding: 2rem;
}

.title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: var(--border-width) solid var(--border-color);
}

.title-section h1 {
  margin: 0;
  font-size: 2.5rem;
  background: var(--accent-yellow);
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.status-badge {
  padding: 0.5rem 1rem;
  font-weight: bold;
  border: var(--border-width) solid var(--border-color);
  background: #ddd;
  color: var(--text-color);
  text-transform: uppercase;
}

.status-badge.active {
  background: var(--accent-green);
  color: var(--text-color);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--border-color);
  background: #f9f9f9;
}

.info-item .icon {
  font-size: 2rem;
}

.info-item .label {
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.info-item .value {
  font-size: 1.1rem;
  font-weight: bold;
  font-family: var(--font-main);
}

/* Map Card */
.map-card {
  background: white;
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  padding: 2rem;
}

.map-card h2 {
  margin: 0 0 1.5rem 0;
  background: var(--accent-blue);
  color: white;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.map-container {
  position: relative;
  border: var(--border-width) solid var(--border-color);
  overflow: hidden;
}

.map-iframe {
  width: 100%;
  height: 450px;
  border: none;
}

.map-links {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-top: var(--border-width) solid var(--border-color);
}

.map-link {
  color: var(--text-color);
  text-decoration: none;
  font-weight: bold;
  border-bottom: 2px solid var(--text-color);
}

.map-link:hover {
  background: var(--accent-yellow);
}

/* Readings Card */
.readings-card {
  background: white;
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  padding: 2rem;
}

.readings-card h2 {
  margin: 0 0 1.5rem 0;
  background: var(--accent-green);
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.no-readings {
  text-align: center;
  padding: 3rem 2rem;
  background: #f9f9f9;
  border: 2px dashed var(--border-color);
  font-weight: bold;
}

.readings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.reading-card {
  background: white;
  border: var(--border-width) solid var(--border-color);
  padding: 1.5rem;
  box-shadow: 4px 4px 0 0 var(--border-color);
  transition: all 0.2s;
}

.reading-card:hover {
  transform: translate(-4px, -4px);
  box-shadow: 8px 8px 0 0 var(--border-color);
}

.reading-card.aqi-good {
  background: #e8ffe8;
  border-left: 8px solid #00e400;
}

.reading-card.aqi-moderate {
  background: #fffce0;
  border-left: 8px solid #ffdd00;
}

.reading-card.aqi-unhealthy-sensitive {
  background: #fff0e0;
  border-left: 8px solid #ff7e00;
}

.reading-card.aqi-unhealthy {
  background: #ffe8e8;
  border-left: 8px solid #ff0000;
}

.reading-card.aqi-very-unhealthy {
  background: #f0e8f0;
  border-left: 8px solid #8f3f97;
}

.reading-card.aqi-hazardous {
  background: #f0e0e0;
  border-left: 8px solid #7e0023;
}

.reading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.pollutant-name {
  font-weight: 900;
  font-size: 1.2rem;
  text-transform: uppercase;
}

.reading-time {
  font-size: 0.8rem;
  font-weight: bold;
  font-family: var(--font-main);
}

.reading-value {
  font-size: 2.5rem;
  font-weight: 900;
  font-family: var(--font-display);
  margin-bottom: 0.75rem;
}

.unit {
  font-size: 1rem;
  font-weight: bold;
}

.reading-aqi {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  background: white;
  padding: 0.5rem;
  border: 2px solid var(--border-color);
}

.aqi-label {
  font-weight: bold;
}

.aqi-value {
  font-size: 1.2rem;
  font-weight: 900;
}

.aqi-category {
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
}

.provider-badge {
  font-size: 0.8rem;
  font-weight: bold;
  padding: 0.5rem;
  background: white;
  border: 2px solid var(--border-color);
  display: inline-block;
}

/* History Card */
.history-card {
  background: var(--accent-yellow);
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  padding: 2rem;
  text-align: center;
}

.history-card h2 {
  margin: 0 0 1rem 0;
  background: white;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.history-note {
  font-weight: bold;
  font-size: 1.1rem;
}

.inline-link {
  color: var(--text-color);
  text-decoration: none;
  font-weight: 900;
  border-bottom: 3px solid var(--text-color);
}

.inline-link:hover {
  background: white;
}
</style>
