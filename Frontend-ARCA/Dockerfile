# Stage 1: Build
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npx ng build --output-path=dist/browser --base-href /

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist/browser/browser /usr/share/nginx/html
# Copiar configuración de nginx si es necesario para SPA
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
