// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  routeRules: {
    '/api/**': { proxy: 'http://api:8000/**' },
    '/docs': { proxy: 'http://api:8000/docs' },
    '/redoc': { proxy: 'http://api:8000/redoc' },
    '/openapi.json': { proxy: 'http://api:8000/openapi.json' },
  },
})
