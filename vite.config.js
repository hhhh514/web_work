import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import path from 'path'; 

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), // Define @ as src directory
    },
  },
  server: {
    host: true,
    port: 5173,
    allowedHosts: [
      'salanakawaii.tplinkdns.com'
    ]
  }
});