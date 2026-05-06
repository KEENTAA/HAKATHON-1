#!/bin/sh

# Reemplazar API_URL en los archivos JavaScript compilados
if [ -n "$API_URL" ]; then
  echo "Configurando API_URL: $API_URL"
  # Buscar y reemplazar en archivos JS del dist
  find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|http://localhost:8000/api/v1|${API_URL}|g" {} \;
  find /usr/share/nginx/html -name "*.js" -type f -exec sed -i "s|http://api-gateway:8000/api/v1|${API_URL}|g" {} \;
fi

# Ejecutar nginx
exec "$@"
