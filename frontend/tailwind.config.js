/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        command: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#102a43',
          950: '#0a1929',
        },
        alert: {
          critical: '#b91c1c',
          high: '#c2410c',
          medium: '#a16207',
          low: '#15803d',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'Segoe UI', 'sans-serif'],
        display: ['"IBM Plex Sans Condensed"', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
