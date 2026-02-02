import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Neutral political spectrum colors (avoiding red/blue)
        spectrum: {
          'far-left': '#7c3aed',    // Purple
          'left': '#8b5cf6',        // Light purple
          'center-left': '#a78bfa', // Lighter purple
          'center': '#6b7280',      // Gray
          'center-right': '#f59e0b',// Amber
          'right': '#f97316',       // Orange
          'far-right': '#ea580c',   // Darker orange
        },
      },
    },
  },
  plugins: [],
} satisfies Config
