/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        sozo: {
          primary: '#1a365d',
          secondary: '#2b6cb0',
          accent: '#38a169',
          warning: '#d69e2e',
          danger: '#e53e3e',
          surface: '#f7fafc',
          text: '#1a202c',
        },
      },
    },
  },
  plugins: [],
};
