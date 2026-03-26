/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm peach / blush light theme
        surface: '#FCF7F2',
        'surface-alt': '#FAF3ED',
        sidebar: '#F7EFE8',
        card: '#FFF8F3',
        'card-hover': '#FFF1E8',
        border: '#EADFD6',
        'border-strong': '#DDD0C4',
        'text-primary': '#3A2E2A',
        'text-secondary': '#7A6258',
        'text-muted': '#A89385',
        'peach-light': '#F6C7B8',
        'peach': '#F0A890',
        'peach-dark': '#E09478',
        'blush': '#F3D8C7',
        'blush-light': '#FBE8DD',
        'accent-warm': '#E8976E',

        // Dark mode (warm dark, not blue)
        'dark-bg': '#1A1412',
        'dark-surface': '#241E1A',
        'dark-card': '#2E2622',
        'dark-border': '#3D3430',
        'dark-hover': '#453B36',
        'dark-text': '#E8DDD6',
        'dark-text-secondary': '#A89890',
        'dark-text-muted': '#7A6E66',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
