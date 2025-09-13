# Build stage with optimized caching
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install dependencies with optimizations
RUN npm ci --only=production --silent --no-audit --no-fund

# Copy source code
COPY . .

# Build the app with optimizations and disable source maps for smaller build
RUN GENERATE_SOURCEMAP=false npm run build

# Production stage - lightweight nginx
FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && chmod -R 755 /usr/share/nginx/html

# Expose port 3000 (matching docker-compose)
EXPOSE 3000

# Start nginx with optimized settings
CMD ["nginx", "-g", "daemon off;"]