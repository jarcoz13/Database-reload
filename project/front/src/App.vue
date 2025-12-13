<template>
  <div id="app">
    <header class="neo-header">
      <div class="logo">🌍 Air Quality Monitor</div>
      <nav>
        <router-link to="/">Home</router-link>
        <router-link to="/stations">Stations</router-link>
        <router-link to="/alerts">Alerts</router-link>
        <router-link to="/reports">Reports</router-link>
      </nav>
    </header>
    <main class="main-content">
      <router-view />
    </main>
    <footer class="neo-footer">
      <p>© 2025 Air Quality Monitor. Jarcoz All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.neo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: var(--border-width) solid var(--border-color);
  background: var(--bg-color);
}

.logo {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 900;
  text-transform: uppercase;
  background: var(--accent-yellow);
  padding: 0.5rem 1rem;
  border: var(--border-width) solid var(--border-color);
  box-shadow: 4px 4px 0 0 var(--border-color);
}

nav {
  display: flex;
  gap: 1.5rem;
}

nav a {
  font-family: var(--font-display);
  text-transform: uppercase;
  font-size: 1.1rem;
  padding: 0.5rem;
  border: 2px solid transparent;
}

nav a:hover, nav a.router-link-active {
  background: var(--accent-blue);
  color: white;
  border: 2px solid var(--border-color);
  box-shadow: 4px 4px 0 0 var(--border-color);
  text-decoration: none;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 3rem auto;
  padding: 0 2rem;
}

.neo-footer {
  border-top: var(--border-width) solid var(--border-color);
  padding: 2rem;
  text-align: center;
  background: var(--bg-color);
  font-weight: bold;
}
</style>
