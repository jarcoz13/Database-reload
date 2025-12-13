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
}

.back-btn {
  padding: 0.75rem 1.5rem;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #e0e0e0;
  transform: translateX(-4px);
}

.refresh-btn {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: #45a049;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #666;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Station Header Card */
.station-header-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 2rem;
}

.title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.title-section h1 {
  margin: 0;
  color: #333;
  font-size: 2rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.95rem;
  font-weight: 600;
  background: #ddd;
  color: #666;
}

.status-badge.active {
  background: #d4edda;
  color: #28a745;
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
}

.info-item .icon {
  font-size: 2rem;
}

.info-item .label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.info-item .value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

/* Map Card */
.map-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 2rem;
}

.map-card h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.map-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
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
  background: #f9f9f9;
  border-top: 1px solid #e0e0e0;
}

.map-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.3s;
}

.map-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Readings Card */
.readings-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 2rem;
}

.readings-card h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.no-readings {
  text-align: center;
  padding: 3rem 2rem;
  background: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.no-readings p {
  margin: 0.5rem 0;
}

.readings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.reading-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border-left: 5px solid #ddd;
  transition: all 0.3s;
}

.reading-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

.reading-card.aqi-good {
  border-left-color: #00e400;
  background: linear-gradient(135deg, #f0fff0 0%, #e8ffe8 100%);
}

.reading-card.aqi-moderate {
  border-left-color: #ffdd00;
  background: linear-gradient(135deg, #fffef0 0%, #fffce0 100%);
}

.reading-card.aqi-unhealthy-sensitive {
  border-left-color: #ff7e00;
  background: linear-gradient(135deg, #fff8f0 0%, #fff0e0 100%);
}

.reading-card.aqi-unhealthy {
  border-left-color: #ff0000;
  background: linear-gradient(135deg, #fff0f0 0%, #ffe8e8 100%);
}

.reading-card.aqi-very-unhealthy {
  border-left-color: #8f3f97;
  background: linear-gradient(135deg, #f8f0f8 0%, #f0e8f0 100%);
}

.reading-card.aqi-hazardous {
  border-left-color: #7e0023;
  background: linear-gradient(135deg, #f5f0f0 0%, #f0e0e0 100%);
}

.reading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.pollutant-name {
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
}

.reading-time {
  font-size: 0.8rem;
  color: #666;
}

.reading-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 0.75rem;
}

.unit {
  font-size: 1rem;
  color: #666;
  font-weight: normal;
}

.reading-aqi {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.aqi-label {
  font-size: 0.9rem;
  color: #666;
}

.aqi-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.aqi-category {
  font-size: 0.85rem;
  color: #666;
  padding: 0.25rem 0.5rem;
  background: rgba(255,255,255,0.5);
  border-radius: 4px;
}

.provider-badge {
  font-size: 0.8rem;
  color: #666;
  padding: 0.5rem;
  background: rgba(255,255,255,0.6);
  border-radius: 6px;
}

/* History Card */
.history-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 2rem;
  text-align: center;
}

.history-card h2 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.5rem;
}

.history-note {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.inline-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.inline-link:hover {
  text-decoration: underline;
}
</style>
