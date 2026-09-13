/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'sire-dark': '#0F1117',
        'sire-card': '#1A1D26',
        'sire-secondary': '#262C36',
        'sire-blue': '#1877F2',
        'sire-green': '#2FA572',
        'sire-red': '#E74C3C',
      },
    },
  },
  plugins: [],
}
