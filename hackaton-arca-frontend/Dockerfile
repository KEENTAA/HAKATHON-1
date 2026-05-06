FROM oven/bun:alpine AS build
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install
COPY . .

# Crear archivo de configuración dinámica
RUN bun run build

FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*

# Copiar archivos build
COPY --from=build /app/dist/hackaton-arca-frontend/browser /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Script para inyectar API_URL en runtime
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
