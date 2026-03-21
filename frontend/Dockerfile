# Build Angular app
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
ARG CONFIGURATION=production
RUN npm run build -- --configuration=${CONFIGURATION}
RUN mkdir -p /app/output && (cp -r dist/*/browser/. /app/output 2>/dev/null || cp -r dist/*/. /app/output 2>/dev/null || true)

# Serve with nginx
FROM nginx:alpine
COPY --from=builder /app/output /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
