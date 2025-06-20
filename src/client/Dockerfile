# Step 1: Install dependencies only when needed
FROM node:18-alpine AS deps
WORKDIR /app

COPY src/client/package.json src/client/package-lock.json ./
RUN npm ci

# Step 2: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# FIXED: copy only the content of client/
COPY --from=deps /app/node_modules ./node_modules
COPY src/client/ ./
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Step 3: Run the application with minimal image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000

CMD ["npm", "start"]