/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f5f9',
          100: '#d9e6f0',
          200: '#b3cde0',
          300: '#8ab4d0',
          400: '#5f9bc0',
          500: '#3a82b0',
          600: '#2a6a9a',
          700: '#1d5280',
          800: '#14384d',
          900: '#0d2536',
          950: '#071420',
        },
        gold: {
          50: '#fdf8ed',
          100: '#f9edcc',
          200: '#f3d999',
          300: '#edc566',
          400: '#e7b133',
          500: '#b89a5a',
          600: '#9a7d45',
          700: '#7c6134',
          800: '#5e4523',
          900: '#3f2a12',
        },
        electric: {
          50: '#eef4ff',
          100: '#d9e6ff',
          200: '#bcccff',
          300: '#8faaff',
          400: '#4f8cff',
          500: '#3b73e6',
          600: '#2a5cc4',
          700: '#1e469e',
          800: '#1a3578',
          900: '#182c5c',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['SF Pro Display', 'Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'gradient': 'gradient 8s ease infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'aurora': 'aurora 15s ease infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'count-up': 'countUp 2s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(79, 140, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(79, 140, 255, 0.6)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        aurora: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '25%': { transform: 'translate(10%, -10%) scale(1.1)' },
          '50%': { transform: 'translate(-5%, 15%) scale(0.9)' },
          '75%': { transform: 'translate(15%, 5%) scale(1.05)' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
          '50%': { transform: 'scale(1.05)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
