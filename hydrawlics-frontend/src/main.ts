import { createApp } from 'vue'
import './tailwind.css'
import './style.scss'
import './css/fonts.css'
import App from './App.vue'
import router from "./router";

// Set theme based on user's browser preference
function setInitialTheme() {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = prefersDark ? 'dark' : 'light';
  
  // Add the theme class to html element
  document.documentElement.className = theme;
  
  // Listen for changes in user's preference
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    document.documentElement.className = e.matches ? 'dark' : 'light';
  });
}

setInitialTheme();

createApp(App).use(router).mount('#app')
