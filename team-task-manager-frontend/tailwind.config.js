/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f7ff',
          100: '#e0f0ff',
          200: '#bae0ff',
          300: '#7cc5ff',
          400: '#36a9ff',
          500: '#0084ff',
          600: '#0060d5',
          700: '#0042a6',
          800: '#023275',
          900: '#001d4d',
        },
        secondary: {
          50: '#f5f3ff',
          100: '#ede9ff',
          200: '#d9d0ff',
          300: '#c1b0ff',
          400: '#a087ff',
          500: '#7c5fff',
          600: '#6b42ff',
          700: '#5a2dff',
          800: '#4620e0',
          900: '#2e1199',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-gentle': 'pulseGentle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGentle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '.8' },
        }
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}
