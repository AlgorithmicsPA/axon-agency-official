# Node.js 20.x base
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files first (cache layer)
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --omit=dev

# Copy application code
COPY . .

# Build Next.js app
RUN npm run build

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Start Next.js production server
CMD ["npm", "run", "start", "--", "-p", "5000"]
