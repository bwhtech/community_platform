import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'

export default defineConfig({
  plugins: [
    frappeui({
      // Dev server (:8081, or the next free port) proxies /api, /assets and /login
      // to bench on :8001. Open it as http://community.localhost:<port> so the proxy picks the site.
      frappeProxy: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../community_platform/www/community.html',
      },
      // its esbuild helper breaks Vite 8's dependency scan
      codeLanguages: false,
    }),
    vue(),
    routeMeta(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, 'src'),
    },
    dedupe: ['vue', 'vue-router', 'frappe-ui', 'reka-ui', '@vueuse/core'],
  },
  optimizeDeps: {
    // frappe-ui ships source: pre-bundling it leaves its .vue files outside
    exclude: ['frappe-ui'],
  },
})

// In the built page, swap the static <title> for Jinja meta tags that
// www/community.py fills per route, so shared links preview well.
function routeMeta() {
  return {
    name: 'community-route-meta',
    apply: 'build',
    transformIndexHtml(html) {
      return html.replace(
        '<title>Frappe Community</title>',
        `<title>{{ meta.title }}</title>
    <meta name="description" content="{{ meta.description }}" />
    <meta property="og:title" content="{{ meta.title }}" />
    <meta property="og:description" content="{{ meta.description }}" />
    <meta property="og:url" content="{{ meta.url }}" />
    <meta property="og:type" content="website" />
    {% if meta.image %}<meta property="og:image" content="{{ meta.image }}" />{% endif %}
    <meta name="twitter:card" content="summary" />`,
      )
    },
  }
}
