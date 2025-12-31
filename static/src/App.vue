<script setup>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import Toast from '@/components/Toast.vue'
</script>

<template>
  <div id="app">
    <Navbar />
    <div class="main-content">
    <router-view />
    </div>
    <Footer />
    <!-- Global Toast Component -->
    <Toast />
  </div>
</template>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Verdana', 'Geneva', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ffffff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  background-color: #000000;
  padding-top: 60px;
  flex: 1;
}

/* Remove default link styles */
a {
  text-decoration: none;
  color: inherit;
}

/* Button reset */
button {
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
}
</style>
