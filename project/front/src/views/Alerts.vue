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
              <option value="in-app">In-App Notification</option>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="all">All Methods</option>
            </select>
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
      notification_method: 'in-app'
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
}

.create-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color, #4CAF50);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.3s;
}

.create-btn:hover {
  background: var(--primary-dark, #45a049);
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

.no-data button {
  margin-top: 1rem;
}

.alerts-container {
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

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #eee;
}

.alert-title {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pollutant-badge {
  font-size: 1.25rem;
  font-weight: bold;
  color: #333;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  background: #ddd;
  color: #666;
  width: fit-content;
}

.status-badge.active {
  background: #d4edda;
  color: #28a745;
}

.alert-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.icon-btn:hover {
  background: #e0e0e0;
}

.icon-btn.delete:hover {
  background: #fee;
  color: #c33;
}

.alert-info {
  margin: 1rem 0;
}

.alert-info p {
  margin: 0.5rem 0;
  color: #555;
  font-size: 0.95rem;
}

.alert-info .triggered {
  color: #f59e0b;
  font-style: italic;
}

.alert-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.toggle-btn {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #666;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.toggle-btn:hover {
  border-color: #4CAF50;
  color: #4CAF50;
}

.toggle-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.toggle-btn.active:hover {
  background: #ef4444;
  border-color: #ef4444;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 2rem;
  height: 2rem;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4CAF50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: #45a049;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
