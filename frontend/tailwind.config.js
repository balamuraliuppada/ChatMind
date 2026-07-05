/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#6366f1", // indigo-500
        secondary: "#4f46e5", // indigo-600
        dark: "#0f172a", // slate-900
        darker: "#020617", // slate-950
        panel: "#1e293b", // slate-800
      }
    },
  },
  plugins: [],
}
