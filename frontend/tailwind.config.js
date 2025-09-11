/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        health: {
          excellent: '#10B981',
          good: '#34D399',
          warning: '#F59E0B',
          poor: '#EF4444',
          critical: '#DC2626',
        }
      }
    },
  },
  plugins: [],
}