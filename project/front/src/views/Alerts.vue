<template>
  <div class="alerts">
    <div class="header">
      <h1>Air Quality Alerts</h1>
      <button @click="showCreateModal = true" class="create-btn">+ Create New Alert</button>
    </div>

    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <div v-if="loading" class="loading">Loading alerts...</div>

    <div v-else-if="alerts.length === 0" class="no-data">
      <p>You don't have any alerts configured yet.</p>
      <p>Create an alert to get notified when air quality exceeds your threshold.</p>
      <button @click="showCreateModal = true" class="create-btn">Create Your First Alert</button>
    </div>

    <div v-else class="alerts-container">
      <div class="card" v-for="alert in alerts" :key="alert.id">
        <div class="alert-header">
          <div class="alert-title">
            <span class="pollutant-badge">{{ alert.pollutant_name || 'Unknown' }}</span>
            <span class="status-badge" :class="{ active: alert.is_active }">
              {{ alert.is_active ? '● Active' : '○ Inactive' }}
            </span>
          </div>
          <div class="alert-actions">
            <button @click="editAlert(alert)" class="icon-btn" title="Edit">✏️</button>
            <button @click="deleteAlert(alert.id)" class="icon-btn delete" title="Delete">🗑️</button>
          </div>
        </div>
        
        <div class="alert-info">
          <p><strong>📍 Station:</strong> {{ alert.station_name || 'Unknown' }}</p>
          <p><strong>🎯 Threshold:</strong> {{ alert.threshold }} {{ alert.unit || 'μg/m³' }}</p>
          <p><strong>🔔 Condition:</strong> {{ formatCondition(alert.trigger_condition) }}</p>
          <p><strong>📬 Notification:</strong> {{ formatNotificationMethod(alert.notification_method) }}</p>
          <p v-if="alert.triggered_at" class="triggered">
            <strong>⚡ Last Triggered:</strong> {{ formatTime(alert.triggered_at) }}
          </p>
        </div>

        <div class="alert-footer">
          <button @click="toggleAlert(alert)" class="toggle-btn" :class="{ active: alert.is_active }">
            {{ alert.is_active ? 'Deactivate' : 'Activate' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit Alert' : 'Create New Alert' }}</h2>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Station</label>
            <select v-model="formData.station_id" required>
              <option value="">Select a station</option>
              <option v-for="station in stations" :key="station.id" :value="station.id">
                {{ station.name }} - {{ station.city }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Pollutant</label>
            <select v-model="formData.pollutant_id" required>
              <option value="">Select a pollutant</option>
              <option v-for="pollutant in pollutants" :key="pollutant.id" :value="pollutant.id">
                {{ pollutant.name }} ({{ pollutant.unit }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Threshold Value</label>
            <input 
              type="number" 
              v-model.number="formData.threshold" 
              step="0.1" 
              min="0"
              placeholder="e.g., 50"
              required
            />
          </div>

          <div class="form-group">
            <label>Trigger Condition</label>
            <select v-model="formData.trigger_condition">
              <option value="exceeds">Exceeds (greater than)</option>
              <option value="below">Below (less than)</option>
              <option value="equals">Equals</option>
            </select>
          </div>

          <div class="form-group">
            <label>Notification Method</label>
            <select v-model="formData.notification_method">
              <option value="telegram">Telegram 📱</option>
            </select>
            <small class="help-text">ℹ️ Only Telegram notifications are enabled at this time. Email and SMS coming soon!</small>
          </div>

          <div v-if="formError" class="error-message">
            {{ formError }}
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeModal" class="cancel-btn">Cancel</button>
          <button @click="saveAlert" class="save-btn" :disabled="formLoading">
            {{ formLoading ? 'Saving...' : (showEditModal ? 'Update Alert' : 'Create Alert') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const MOCK_USER_ID = 2 // TODO: Replace with actual user ID from auth

export default {
  name: 'Alerts',
  setup() {
    const alerts = ref([])
    const stations = ref([])
    const pollutants = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const formLoading = ref(false)
    const formError = ref(null)
    const editingAlert = ref(null)

    const formData = ref({
      station_id: '',
      pollutant_id: '',
      threshold: '',
      trigger_condition: 'exceeds',
      notification_method: 'telegram'
    })

    const loadAlerts = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/alerts?user_id=${MOCK_USER_ID}`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json'
          }
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        
        const data = await response.json()
        
        // Enrich alerts with station and pollutant names
        alerts.value = data.map(alert => {
          const station = stations.value.find(s => s.id === alert.station_id)
          const pollutant = pollutants.value.find(p => p.id === alert.pollutant_id)
          return {
            ...alert,
            station_name: station?.name,
            pollutant_name: pollutant?.name,
            unit: pollutant?.unit
          }
        })
      } catch (err) {
        console.error('Error loading alerts:', err)
        error.value = `Failed to load alerts: ${err.message}`
      }
    }

    const loadStations = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/stations`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include'
        })
        if (response.ok) {
          stations.value = await response.json()
        }
      } catch (err) {
        console.error('Error loading stations:', err)
      }
    }

    const loadPollutants = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/pollutants`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'include'
        })
        if (response.ok) {
          pollutants.value = await response.json()
        }
      } catch (err) {
        console.error('Error loading pollutants:', err)
      }
    }

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        await Promise.all([loadStations(), loadPollutants()])
        await loadAlerts()
      } finally {
        loading.value = false
      }
    }

    const toggleAlert = async (alert) => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/alerts/${alert.id}?user_id=${MOCK_USER_ID}`,
          {
            method: 'PATCH',
            mode: 'cors',
            credentials: 'include',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ is_active: !alert.is_active })
          }
        )
        
        if (response.ok) {
          await loadAlerts()
        } else {
          throw new Error('Failed to update alert')
        }
      } catch (err) {
        console.error('Error toggling alert:', err)
        alert('Failed to update alert status')
      }
    }

    const editAlert = (alert) => {
      editingAlert.value = alert
      formData.value = {
        station_id: alert.station_id,
        pollutant_id: alert.pollutant_id,
        threshold: alert.threshold,
        trigger_condition: alert.trigger_condition,
        notification_method: alert.notification_method
      }
      showEditModal.value = true
    }

    const deleteAlert = async (alertId) => {
      if (!confirm('Are you sure you want to delete this alert?')) return
      
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/alerts/${alertId}?user_id=${MOCK_USER_ID}`,
          {
            method: 'DELETE',
            mode: 'cors',
            credentials: 'include'
          }
        )
        
        if (response.ok) {
          await loadAlerts()
        } else {
          throw new Error('Failed to delete alert')
        }
      } catch (err) {
        console.error('Error deleting alert:', err)
        alert('Failed to delete alert')
      }
    }

    const saveAlert = async () => {
      formError.value = null
      
      if (!formData.value.station_id || !formData.value.pollutant_id || !formData.value.threshold) {
        formError.value = 'Please fill in all required fields'
        return
      }

      formLoading.value = true
      
      try {
        const url = showEditModal.value
          ? `${API_BASE_URL}/api/alerts/${editingAlert.value.id}?user_id=${MOCK_USER_ID}`
          : `${API_BASE_URL}/api/alerts?user_id=${MOCK_USER_ID}`
        
        const method = showEditModal.value ? 'PATCH' : 'POST'
        
        const response = await fetch(url, {
          method,
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData.value)
        })
        
        if (response.ok) {
          await loadAlerts()
          closeModal()
        } else {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Failed to save alert')
        }
      } catch (err) {
        console.error('Error saving alert:', err)
        formError.value = err.message
      } finally {
        formLoading.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingAlert.value = null
      formError.value = null
      formData.value = {
        station_id: '',
        pollutant_id: '',
        threshold: '',
        trigger_condition: 'exceeds',
        notification_method: 'in-app'
      }
    }

    const formatCondition = (condition) => {
      const conditions = {
        'exceeds': 'When value exceeds threshold',
        'below': 'When value is below threshold',
        'equals': 'When value equals threshold'
      }
      return conditions[condition] || condition
    }

    const formatNotificationMethod = (method) => {
      const methods = {
        'telegram': 'Telegram 📱',
        'in-app': 'In-App',
        'email': 'Email',
        'sms': 'SMS',
        'all': 'All Methods'
      }
      return methods[method] || method
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return 'Never'
      const date = new Date(timestamp)
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadData()
    })

    return {
      alerts,
      stations,
      pollutants,
      loading,
      error,
      showCreateModal,
      showEditModal,
      formLoading,
      formError,
      formData,
      toggleAlert,
      editAlert,
      deleteAlert,
      saveAlert,
      closeModal,
      formatCondition,
      formatNotificationMethod,
      formatTime
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
  background: var(--accent-purple);
  padding: 1.5rem;
  border: var(--border-width) solid var(--border-color);
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
}

.header h1 {
  margin: 0;
  font-size: 2rem;
}

.create-btn {
  padding: 0.75rem 1.5rem;
  background: var(--accent-green);
  color: var(--text-color);
  border: var(--border-width) solid var(--border-color);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 900;
  text-transform: uppercase;
  box-shadow: 4px 4px 0 0 var(--border-color);
  transition: all 0.2s;
}

.create-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
  background: var(--accent-green);
}

.loading {
  text-align: center;
  padding: 2rem;
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

.no-data {
  text-align: center;
  padding: 3rem;
  background: white;
  border: var(--border-width) solid var(--border-color);
  font-weight: bold;
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.no-data button {
  margin-top: 1rem;
}

.alerts-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.card {
  background: white;
  border: var(--border-width) solid var(--border-color);
  padding: 1.5rem;
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  transition: transform 0.2s;
}

.card:hover {
  transform: translate(-4px, -4px);
  box-shadow: calc(var(--shadow-offset) + 4px) calc(var(--shadow-offset) + 4px) 0 0 var(--border-color);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: var(--border-width) solid var(--border-color);
}

.alert-title {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pollutant-badge {
  font-size: 1.25rem;
  font-weight: 900;
  color: var(--text-color);
  background: var(--accent-yellow);
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border: 2px solid var(--border-color);
}

.status-badge {
  padding: 0.25rem 0.75rem;
  font-weight: bold;
  border: 2px solid var(--border-color);
  background: #ddd;
  color: var(--text-color);
  text-transform: uppercase;
  font-size: 0.85rem;
  width: fit-content;
}

.status-badge.active {
  background: var(--accent-green);
  color: var(--text-color);
}

.alert-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: white;
  border: 2px solid var(--border-color);
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
  box-shadow: 2px 2px 0 0 var(--border-color);
}

.icon-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 0 var(--border-color);
  background: var(--accent-yellow);
}

.icon-btn.delete:hover {
  background: var(--accent-red);
  color: white;
}

.alert-info {
  margin: 1rem 0;
  padding: 1rem;
  background: #f9f9f9;
  border: 2px solid var(--border-color);
}

.alert-info p {
  margin: 0.5rem 0;
  color: var(--text-color);
  font-size: 0.95rem;
  font-weight: bold;
}

.alert-info .triggered {
  color: white;
  background: var(--accent-red);
  padding: 0.2rem 0.5rem;
  font-style: normal;
  border: 2px solid var(--border-color);
  display: inline-block;
}

.alert-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: var(--border-width) solid var(--border-color);
}

.toggle-btn {
  width: 100%;
  padding: 0.75rem;
  border: var(--border-width) solid var(--border-color);
  background: white;
  color: var(--text-color);
  cursor: pointer;
  font-weight: 900;
  text-transform: uppercase;
  transition: all 0.2s;
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.toggle-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
  background: var(--accent-yellow);
}

.toggle-btn.active {
  background: var(--accent-green);
  color: var(--text-color);
}

.toggle-btn.active:hover {
  background: var(--accent-red);
  color: white;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal {
  background: white;
  border: var(--border-width) solid var(--border-color);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 10px 10px 0 0 var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: var(--border-width) solid var(--border-color);
  background: var(--accent-blue);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
  text-shadow: 2px 2px 0 var(--border-color);
}

.close-btn {
  background: white;
  border: 2px solid var(--border-color);
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-color);
  padding: 0;
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 4px 4px 0 0 var(--border-color);
}

.close-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
  background: var(--accent-red);
  color: white;
}

.modal-body {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 900;
  color: var(--text-color);
  text-transform: uppercase;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: var(--border-width) solid var(--border-color);
  font-size: 1rem;
  box-sizing: border-box;
  background: white;
  box-shadow: 4px 4px 0 0 var(--border-color);
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  background: var(--accent-yellow);
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
}

.form-group .help-text {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-color);
  font-weight: bold;
  background: var(--accent-yellow);
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--border-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: var(--border-width) solid var(--border-color);
  background: #f9f9f9;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: white;
  color: var(--text-color);
  border: var(--border-width) solid var(--border-color);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 900;
  text-transform: uppercase;
  box-shadow: 4px 4px 0 0 var(--border-color);
  transition: all 0.2s;
}

.cancel-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
  background: var(--accent-red);
  color: white;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background: var(--accent-green);
  color: var(--text-color);
  border: var(--border-width) solid var(--border-color);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 900;
  text-transform: uppercase;
  box-shadow: 4px 4px 0 0 var(--border-color);
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 0 var(--border-color);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}
</style>
