<template>
  <div class="reports">
    <h1>Reports</h1>
    <div class="report-form card">
      <h2>Generate New Report</h2>
      <form @submit.prevent="generateReport">
        <div class="form-group">
          <label>Report Title:</label>
          <input v-model="reportForm.title" type="text" required />
        </div>
        <div class="form-group">
          <label>Start Date:</label>
          <input v-model="reportForm.start_date" type="date" required />
        </div>
        <div class="form-group">
          <label>End Date:</label>
          <input v-model="reportForm.end_date" type="date" required />
        </div>
        <div class="form-group">
          <label>Format:</label>
          <select v-model="reportForm.format">
            <option value="CSV">CSV</option>
            <option value="PDF">PDF</option>
          </select>
        </div>
        <button type="submit">Generate Report</button>
      </form>
    </div>

    <div class="reports-list">
      <h2>Previous Reports</h2>
      <div class="card" v-for="report in reports" :key="report.id">
        <h3>{{ report.title }}</h3>
        <p><strong>Period:</strong> {{ report.start_date }} to {{ report.end_date }}</p>
        <p><strong>Format:</strong> {{ report.file_format }}</p>
        <p><strong>Generated:</strong> {{ report.generated_at }}</p>
        <button @click="downloadReport(report.id)">Download</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'

export default {
  name: 'Reports',
  setup() {
    const reports = ref([])
    const reportForm = reactive({
      title: '',
      start_date: '',
      end_date: '',
      format: 'CSV'
    })

    const loadReports = async () => {
      // TODO: Replace with actual API call
      reports.value = [
        {
          id: 1,
          title: 'Monthly Air Quality Report',
          start_date: '2024-01-01',
          end_date: '2024-01-31',
          file_format: 'PDF',
          generated_at: '2024-02-01'
        }
      ]
    }

    const generateReport = async () => {
      console.log('Generating report:', reportForm)
      // TODO: Call API to generate report
    }

    const downloadReport = (id) => {
      console.log('Downloading report:', id)
      // TODO: Download report
    }

    onMounted(() => {
      loadReports()
    })

    return {
      reports,
      reportForm,
      generateReport,
      downloadReport
    }
  }
}
</script>

<style scoped>
.report-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.reports-list {
  margin-top: 2rem;
}

.reports-list .card {
  margin-bottom: 1rem;
}
</style>
