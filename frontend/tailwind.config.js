/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          950: '#060913',
          900: '#0B1120',
          850: '#0F172A',
          800: '#1E293B',
          700: '#334155',
          600: '#475569',
        },
        isro: {
          orange: '#FF6B00',
          blue: '#0284C7',
          sky: '#38BDF8',
          gold: '#F59E0B'
        }
      }
    },
  },
  plugins: [],
}
