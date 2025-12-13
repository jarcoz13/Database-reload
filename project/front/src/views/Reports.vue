<template>
  <div class="reports">
    <h1>📊 Reports</h1>
    
    <div class="report-form card">
      <h2>Generate New Report</h2>
      <p class="subtitle">Create a comprehensive air quality report with visualizations</p>
      
      <form @submit.prevent="generateReport">
        <div class="form-row">
          <div class="form-group">
            <label>Report Title: *</label>
            <input 
              v-model="reportForm.title" 
              type="text" 
              placeholder="e.g., Monthly Air Quality Report"
              required 
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Start Date: *</label>
            <input 
              v-model="reportForm.start_date" 
              type="date" 
              :max="reportForm.end_date || today"
              required 
            />
          </div>
          
          <div class="form-group">
            <label>End Date: *</label>
            <input 
              v-model="reportForm.end_date" 
              type="date" 
              :min="reportForm.start_date"
              :max="today"
              required 
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Station: (optional)</label>
            <select v-model="reportForm.station_id">
              <option :value="null">All Stations</option>
              <option 
                v-for="station in stations" 
                :key="station.id" 
                :value="station.id"
              >
                {{ station.name }} - {{ station.city }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Pollutant: (optional)</label>
            <select v-model="reportForm.pollutant_id">
              <option :value="null">All Pollutants</option>
              <option 
                v-for="pollutant in pollutants" 
                :key="pollutant.id" 
                :value="pollutant.id"
              >
                {{ pollutant.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Format: *</label>
            <select v-model="reportForm.file_format">
              <option value="PDF">PDF (with charts)</option>
              <option value="CSV" disabled>CSV (coming soon)</option>
            </select>
          </div>
        </div>
        
        <button 
          type="submit" 
          class="btn-primary" 
          :disabled="isGenerating"
        >
          {{ isGenerating ? '⏳ Generating...' : '📄 Generate Report' }}
        </button>
      </form>
    </div>

    <div class="reports-list">
      <h2>📚 Previous Reports</h2>
      
      <div v-if="loading" class="loading">
        <p>Loading reports...</p>
      </div>

      <div v-else-if="reports.length === 0" class="empty-state">
        <p>No reports generated yet. Create your first report above!</p>
      </div>

      <div v-else class="report-cards">
        <div class="report-card" v-for="report in reports" :key="report.id">
          <div class="report-header">
            <h3>{{ report.title }}</h3>
            <span class="format-badge" :class="report.file_format.toLowerCase()">
              {{ report.file_format }}
            </span>
          </div>
          
          <div class="report-details">
            <div class="detail-item">
              <span class="icon">📅</span>
              <div>
                <div class="detail-label">Period</div>
                <div class="detail-value">{{ formatDate(report.start_date) }} to {{ formatDate(report.end_date) }}</div>
              </div>
            </div>

            <div class="detail-item" v-if="report.station_id">
              <span class="icon">📍</span>
              <div>
                <div class="detail-label">Station</div>
                <div class="detail-value">{{ getStationName(report.station_id) }}</div>
              </div>
            </div>

            <div class="detail-item" v-if="report.pollutant_id">
              <span class="icon">🧪</span>
              <div>
                <div class="detail-label">Pollutant</div>
                <div class="detail-value">{{ getPollutantName(report.pollutant_id) }}</div>
              </div>
            </div>

            <div class="detail-item">
              <span class="icon">⏰</span>
              <div>
                <div class="detail-label">Generated</div>
                <div class="detail-value">{{ formatDateTime(report.generated_at) }}</div>
              </div>
            </div>
          </div>

          <div class="report-actions">
            <button @click="downloadReport(report.id)" class="btn-download">
              ⬇️ Download
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'

export default {
  name: 'Reports',
  setup() {
    const reports = ref([])
    const stations = ref([])
    const pollutants = ref([])
    const loading = ref(false)
    const isGenerating = ref(false)
    
    // TODO: Replace with actual user ID from auth
    const MOCK_USER_ID = 2
    
    const reportForm = reactive({
      title: '',
      start_date: '',
      end_date: '',
      station_id: null,
      pollutant_id: null,
      file_format: 'PDF'
    })

    const today = computed(() => {
      return new Date().toISOString().split('T')[0]
    })

    const loadReports = async () => {
      loading.value = true
      try {
        const response = await fetch(
          `http://localhost:8000/api/reports?user_id=${MOCK_USER_ID}`,
          {
            method: 'GET',
            mode: 'cors',
            credentials: 'include',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          }
        )
        
        if (response.ok) {
          reports.value = await response.json()
        } else {
          console.error('Failed to load reports:', response.status)
        }
      } catch (error) {
        console.error('Error loading reports:', error)
      } finally {
        loading.value = false
      }
    }

    const loadStations = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/stations', {
          method: 'GET',
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          stations.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading stations:', error)
      }
    }

    const loadPollutants = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/pollutants', {
          method: 'GET',
          mode: 'cors',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          pollutants.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading pollutants:', error)
      }
    }

    const generateReport = async () => {
      if (!reportForm.title || !reportForm.start_date || !reportForm.end_date) {
        alert('Please fill in all required fields')
        return
      }

      if (new Date(reportForm.end_date) < new Date(reportForm.start_date)) {
        alert('End date must be after start date')
        return
      }

      isGenerating.value = true
      
      try {
        const payload = {
          title: reportForm.title,
          start_date: reportForm.start_date,
          end_date: reportForm.end_date,
          station_id: reportForm.station_id,
          pollutant_id: reportForm.pollutant_id,
          file_format: reportForm.file_format
        }

        const response = await fetch(
          `http://localhost:8000/api/reports?user_id=${MOCK_USER_ID}`,
          {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
          }
        )
        
        if (response.ok) {
          const newReport = await response.json()
          reports.value.unshift(newReport)
          
          // Reset form
          reportForm.title = ''
          reportForm.start_date = ''
          reportForm.end_date = ''
          reportForm.station_id = null
          reportForm.pollutant_id = null
          reportForm.file_format = 'PDF'
          
          alert('✅ Report generated successfully!')
          
          // Auto-download
          setTimeout(() => {
            downloadReport(newReport.id)
          }, 500)
        } else {
          const error = await response.json()
          alert(`Failed to generate report: ${error.detail || 'Unknown error'}`)
        }
      } catch (error) {
        console.error('Error generating report:', error)
        alert('Error generating report. Please try again.')
      } finally {
        isGenerating.value = false
      }
    }

    const downloadReport = async (reportId) => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/reports/${reportId}/download?user_id=${MOCK_USER_ID}`,
          {
            method: 'GET',
            mode: 'cors',
            credentials: 'include'
          }
        )
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          
          // Get filename from Content-Disposition header or use default
          const contentDisposition = response.headers.get('content-disposition')
          let filename = `report_${reportId}.pdf`
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i)
            if (filenameMatch) {
              filename = filenameMatch[1]
            }
          }
          
          a.download = filename
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        } else {
          alert('Failed to download report')
        }
      } catch (error) {
        console.error('Error downloading report:', error)
        alert('Error downloading report. Please try again.')
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getStationName = (stationId) => {
      const station = stations.value.find(s => s.id === stationId)
      return station ? `${station.name} - ${station.city}` : 'Unknown Station'
    }

    const getPollutantName = (pollutantId) => {
      const pollutant = pollutants.value.find(p => p.id === pollutantId)
      return pollutant ? pollutant.name : 'Unknown Pollutant'
    }

    onMounted(() => {
      loadReports()
      loadStations()
      loadPollutants()
    })

    return {
      reports,
      stations,
      pollutants,
      reportForm,
      loading,
      isGenerating,
      today,
      generateReport,
      downloadReport,
      formatDate,
      formatDateTime,
      getStationName,
      getPollutantName
    }
  }
}
</script>

<style scoped>
.reports {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 2rem;
}

h2 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.subtitle {
  color: #666;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

/* Report Form */
.report-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 3rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-row:first-of-type,
.form-row:last-of-type {
  grid-template-columns: 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #444;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4CAF50;
}

.btn-primary {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  padding: 1rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Reports List */
.reports-list {
  margin-top: 3rem;
}

.loading,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.report-cards {
  display: grid;
  gap: 1.5rem;
}

.report-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.report-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.format-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.format-badge.pdf {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.format-badge.csv {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.report-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.detail-item .icon {
  font-size: 1.5rem;
  margin-top: 0.2rem;
}

.detail-label {
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.detail-value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}

.report-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 2px solid #f0f0f0;
}

.btn-download {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

/* Responsive Design */
@media (max-width: 768px) {
  .reports {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .report-details {
    grid-template-columns: 1fr;
  }

  .report-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
