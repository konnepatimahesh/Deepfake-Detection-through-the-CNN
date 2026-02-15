# Setup Frontend Files Script

Write-Host "Creating frontend structure..." -ForegroundColor Green

# Create tailwind.config.js
@"
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"@ | Out-File -FilePath "tailwind.config.js" -Encoding UTF8

Write-Host "✓ Created tailwind.config.js" -ForegroundColor Green

# Update src/index.css
@"
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}
"@ | Out-File -FilePath "src\index.css" -Encoding UTF8

Write-Host "✓ Updated src/index.css" -ForegroundColor Green

Write-Host "`nAll configuration files created!" -ForegroundColor Cyan
Write-Host "Now I'll provide the component files. Continue? (Y/N)" -ForegroundColor Yellow