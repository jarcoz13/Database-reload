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
      <div class="card" v-for="station in stations" :key="station.id">
        <div class="station-header">
          <h3>{{ station.name }}</h3>
          <span class="status-badge" :class="{ active: station.is_active }">
            {{ station.is_active ? '● Active' : '○ Inactive' }}
          </span>
        </div>
        
        <div class="station-info">
          <p><strong>📍 Location:</strong> {{ station.city }}, {{ station.country }}</p>
          <p><strong>🗺️ Coordinates:</strong> {{ station.latitude.toFixed(4) }}, {{ station.longitude.toFixed(4) }}</p>
          <p><strong>🏢 Provider:</strong> {{ station.provider_name || 'Unknown' }}</p>
        </div>

        <div v-if="station.current_readings && station.current_readings.length > 0" class="readings">
          <h4>Latest Readings:</h4>
          <div class="readings-grid">
            <div v-for="reading in station.current_readings" :key="reading.pollutant_name" 
                 class="reading-item"
                 :class="getAQIClass(reading.aqi)">
              <div class="pollutant">{{ reading.pollutant_name }}</div>
              <div class="value">{{ reading.value.toFixed(2) }} {{ reading.unit }}</div>
              <div class="aqi" v-if="reading.aqi">AQI: {{ reading.aqi }}</div>
              <div class="time">{{ formatTime(reading.timestamp) }}</div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-readings">
          No recent readings available
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default {
  name: 'Stations',
  setup() {
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
      getAQIClass
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
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #eee;
}

.station-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
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

.station-info {
  margin-bottom: 1rem;
}

.station-info p {
  margin: 0.5rem 0;
  color: #555;
  font-size: 0.95rem;
}

.readings h4 {
  margin: 1rem 0 0.75rem 0;
  color: #333;
  font-size: 1.1rem;
}

.readings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
}

.reading-item {
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 4px solid #ddd;
  transition: transform 0.2s;
}

.reading-item:hover {
  transform: scale(1.05);
}

.reading-item.aqi-good {
  border-left-color: #00e400;
  background: #f0fff0;
}

.reading-item.aqi-moderate {
  border-left-color: #ffff00;
  background: #fffef0;
}

.reading-item.aqi-unhealthy-sensitive {
  border-left-color: #ff7e00;
  background: #fff8f0;
}

.reading-item.aqi-unhealthy {
  border-left-color: #ff0000;
  background: #fff0f0;
}

.reading-item.aqi-very-unhealthy {
  border-left-color: #8f3f97;
  background: #f8f0f8;
}

.reading-item.aqi-hazardous {
  border-left-color: #7e0023;
  background: #f5f0f0;
}

.pollutant {
  font-weight: bold;
  color: #333;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.value {
  font-size: 1.2rem;
  color: #555;
  margin: 0.25rem 0;
}

.aqi {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
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
