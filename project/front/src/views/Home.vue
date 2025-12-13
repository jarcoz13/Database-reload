<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <h1>🌍 Air Quality Monitor</h1>
        <h2>Jose Alejandro Cortazar Lopéz - 20181020022</h2>
        <p class="subtitle">Real-time air quality monitoring and analysis system</p>
      </div>
    </section>

    <section class="stats">
      <div class="stat-box">
        <h3>Stations</h3>
        <p class="number">{{ stats.stations }}</p>
        <p>Active monitoring stations</p>
      </div>
      <div class="stat-box">
        <h3>Readings</h3>
        <p class="number">{{ stats.readings }}</p>
        <p>Total measurements</p>
      </div>
      <div class="stat-box">
        <h3>Users</h3>
        <p class="number">{{ stats.users }}</p>
        <p>Registered users</p>
      </div>
      <div class="stat-box alert-box">
        <h3>Alerts</h3>
        <p class="number">{{ stats.alerts }}</p>
        <p>Active alerts</p>
      </div>
    </section>

    <section class="about">
      <h2>About the System</h2>
      <p>This air quality monitoring system provides real-time data from multiple monitoring stations, helping citizens, researchers, and administrators make informed decisions about air quality.</p>
    </section>

    <section class="features">
      <h2>Features</h2>
      <ul>
        <li>Real-time air quality data from multiple stations</li>
        <li>Personalized alerts for air quality thresholds</li>
        <li>Historical data analysis and reporting</li>
        <li>Health recommendations based on AQI</li>
        <li>Geographic visualization of pollution levels</li>
      </ul>
    </section>
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
.home {
  display: flex;
  flex-direction: column;
  gap: 4rem;
}

.hero {
  background: var(--accent-yellow);
  border: var(--border-width) solid var(--border-color);
  padding: 3rem;
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  text-align: center;
}

.hero h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  line-height: 1;
}

.hero h2 {
  font-size: 1.5rem;
  background: white;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
  transform: rotate(-2deg);
  margin-bottom: 1.5rem;
}

.subtitle {
  font-size: 1.2rem;
  font-weight: bold;
  font-family: var(--font-main);
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.stat-box {
  background: white;
  border: var(--border-width) solid var(--border-color);
  padding: 2rem;
  box-shadow: var(--shadow-offset) var(--shadow-offset) 0 0 var(--border-color);
  text-align: center;
  transition: transform 0.2s;
}

.stat-box:hover {
  transform: translate(-4px, -4px);
  box-shadow: calc(var(--shadow-offset) + 4px) calc(var(--shadow-offset) + 4px) 0 0 var(--border-color);
}

.stat-box h3 {
  background: var(--accent-blue);
  color: white;
  display: inline-block;
  padding: 0.2rem 0.8rem;
  border: var(--border-width) solid var(--border-color);
  margin-bottom: 1rem;
}

.stat-box.alert-box h3 {
  background: var(--accent-red);
}

.number {
  font-size: 4rem;
  font-weight: 900;
  font-family: var(--font-display);
  margin: 1rem 0;
  line-height: 1;
}

.about {
  background: var(--accent-green);
  border: var(--border-width) solid var(--border-color);
  padding: 3rem;
  box-shadow: -8px 8px 0 0 var(--border-color);
}

.about h2 {
  background: white;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.about p {
  font-size: 1.2rem;
  font-weight: bold;
  max-width: 800px;
}

.features {
  border: var(--border-width) solid var(--border-color);
  padding: 3rem;
  background: white;
  box-shadow: 8px 8px 0 0 var(--border-color);
}

.features h2 {
  background: var(--accent-purple);
  display: inline-block;
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
}

.features ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.features li {
  padding: 1rem;
  border: 2px solid var(--border-color);
  font-weight: bold;
  display: flex;
  align-items: center;
}

.features li::before {
  content: "►";
  margin-right: 1rem;
  font-size: 1.2rem;
}
</style>
