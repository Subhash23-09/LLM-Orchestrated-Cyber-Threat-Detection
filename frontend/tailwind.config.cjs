/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        syne:  ['Syne', 'sans-serif'],
        outfit: ['Inter', 'sans-serif'], // alias — keep old refs working
      },
      colors: {
        // Legacy token shims
        background: "hsl(var(--background))",
        foreground:  "hsl(var(--foreground))",
        primary: {
          DEFAULT:    "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        card: {
          DEFAULT:    "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        border: "hsl(var(--border))",
        // Enterprise palette
        navy: {
          base:     '#0E1420',
          surface:  '#141C2E',
          elevated: '#1C2740',
          sidebar:  '#0B1120',
        },
        accent: {
          blue:   '#2563EB',
          'blue-lt': '#3B82F6',
          cyan:   '#06B6D4',
          purple: '#8B5CF6',
        },
        risk: {
          critical: '#EF4444',
          high:     '#F97316',
          medium:   '#F59E0B',
          low:      '#10B981',
        },
      },
      boxShadow: {
        'card-glow':    '0 4px 24px rgba(37,99,235,0.08)',
        'sidebar-glow': '2px 0 20px rgba(0,0,0,0.3)',
        'badge-glow':   '0 0 12px rgba(239,68,68,0.3)',
      },
      keyframes: {
        fadeInUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          from: { opacity: '0', transform: 'translateX(-16px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        'fade-in-up':   'fadeInUp 0.4s ease both',
        'slide-in-left':'slideInLeft 0.3s ease both',
      },
    },
  },
  plugins: [],
}
