import { defineConfig } from 'astro/config'
import tailwindcss from '@tailwindcss/vite'

// Site estático. Sem fontes remotas, sem integrações que falem com terceiro.
export default defineConfig({
  site: 'https://edgebuildlabs.tech',
  trailingSlash: 'always',
  build: {
    format: 'directory',
    inlineStylesheets: 'auto',
  },
  vite: {
    plugins: [tailwindcss()],
  },
})
