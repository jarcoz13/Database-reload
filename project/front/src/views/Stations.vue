<template>
  <div class="stations">
    <div class="header">
      <h1>Monitoring Stations</h1>
      <button @click="loadData" class="refresh-btn" :disabled="loading">
        {{ loading ? 'Loading...' : '🔄 Refresh Data' }}
      </button>
    </div>
    
    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <div v-if="loading" class="loading">Loading stations...</div>

    <div v-else-if="stations.length === 0" class="no-data">
      <p>No monitoring stations found.</p>
      <p>The system is initializing. Please wait or click refresh.</p>
    </div>

    <div v-else class="stations-container">
      <div class="station-card" v-for="station in stations" :key="station.id">
        <div class="station-header">
          <div class="station-title">
            <h3>{{ station.name }}</h3>
            <span class="location">{{ station.city }}, {{ station.country }}</span>
          </div>
          <span class="status-badge" :class="{ active: station.is_active }">
            {{ station.is_active ? '● Active' : '○ Inactive' }}
          </span>
        </div>
        
        <div class="station-summary">
          <div class="summary-item">
            <span class="label">📍 Coordinates:</span>
            <span class="value">{{ station.latitude.toFixed(4) }}, {{ station.longitude.toFixed(4) }}</span>
          </div>
          
          <div class="summary-item" v-if="station.current_readings && station.current_readings.length > 0">
            <span class="label">📊 Latest AQI:</span>
            <span class="value aqi-badge" :class="getAQIClass(getLatestAQI(station))">
              {{ getLatestAQI(station) }}
            </span>
          </div>
          
          <div class="summary-item" v-else>
            <span class="label">📊 Status:</span>
            <span class="value">No recent data</span>
          </div>
        </div>

        <div class="station-footer">
          <button @click="viewStationDetails(station.id)" class="details-btn">
            🔍 View Details & Map
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default {
  name: 'Stations',
  setup() {
    const router = useRouter()
    const stations = ref([])
    const loading = ref(false)
    const error = ref(null)

    const loadStations = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stations`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        return data
      } catch (err) {
        console.error('Error loading stations:', err)
        throw err
      }
    }

    const loadCurrentReadings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/readings/current`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        return data
      } catch (err) {
        console.error('Error loading readings:', err)
        return []
      }
    }

    const loadData = async () => {
      loading.value = true
      error.value = null
      
      console.log('Attempting initialization', new Date())
      console.log('API Base URL:', API_BASE_URL)
      
      try {
        const [stationsData, readingsData] = await Promise.all([
          loadStations(),
          loadCurrentReadings()
        ])

        // Group readings by station
        const readingsByStation = {}
        readingsData.forEach(reading => {
          if (!readingsByStation[reading.station_id]) {
            readingsByStation[reading.station_id] = []
          }
          readingsByStation[reading.station_id].push(reading)
        })

        // Attach readings to stations
        stations.value = stationsData.map(station => ({
          ...station,
          current_readings: readingsByStation[station.id] || []
        }))

      } catch (err) {
        error.value = `Failed to load data: ${err.message}. Check browser console for details.`
        console.error('Error:', err)
        console.error('If you see CORS errors, try disabling browser extensions or using incognito mode.')
      } finally {
        loading.value = false
      }
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
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

    const getLatestAQI = (station) => {
      if (!station.current_readings || station.current_readings.length === 0) {
        return 'N/A'
      }
      // Get the highest AQI from current readings
      const maxAQI = Math.max(...station.current_readings.map(r => r.aqi || 0))
      return maxAQI || 'N/A'
    }

    const viewStationDetails = (stationId) => {
      router.push(`/stations/${stationId}`)
    }

    onMounted(() => {
      loadData()
      // Auto-refresh every 2 minutes
      const interval = setInterval(loadData, 120000)
      return () => clearInterval(interval)
    })

    return {
      stations,
      loading,
      error,
      loadData,
      formatTime,
      getAQIClass,
      getLatestAQI,
      viewStationDetails
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.refresh-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color, #4CAF50);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--primary-dark, #45a049);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
}

.error-message {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.no-data {
  text-align: center;
  padding: 3rem;
  background: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.stations-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.station-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #eee;
}

.station-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.station-title h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.4rem;
}

.station-title .location {
  display: block;
  color: #666;
  font-size: 0.9rem;
  font-weight: normal;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  background: #ddd;
  color: #666;
}

.status-badge.active {
  background: #d4edda;
  color: #28a745;
}

.station-summary {
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item .label {
  color: #666;
  font-size: 0.95rem;
  font-weight: 500;
}

.summary-item .value {
  color: #333;
  font-size: 1rem;
  font-weight: 600;
}

.aqi-badge {
  padding: 0.35rem 0.85rem;
  border-radius: 16px;
  font-size: 0.95rem;
  font-weight: bold;
  color: white;
}

.aqi-badge.aqi-good {
  background: #00e400;
}

.aqi-badge.aqi-moderate {
  background: #ffdd00;
  color: #333;
}

.aqi-badge.aqi-unhealthy-sensitive {
  background: #ff7e00;
}

.aqi-badge.aqi-unhealthy {
  background: #ff0000;
}

.aqi-badge.aqi-very-unhealthy {
  background: #8f3f97;
}

.aqi-badge.aqi-hazardous {
  background: #7e0023;
}

.station-footer {
  margin-top: 1rem;
  text-align: center;
}

.details-btn {
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s;
}

.details-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.time {
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.25rem;
}

.no-readings {
  text-align: center;
  padding: 1.5rem;
  color: #999;
  background: #f9f9f9;
  border-radius: 6px;
  margin-top: 1rem;
  font-style: italic;
}
</style>
