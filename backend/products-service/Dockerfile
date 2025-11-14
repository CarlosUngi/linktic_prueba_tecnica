# Dockerfile para el microservicio de Productos (Node.js/Express)

# =================================
# ETAPA 1: Build
# =================================
# Usar una imagen oficial de Node.js como base.
# Se recomienda usar una versión LTS (Long Term Support) específica.
FROM node:18-alpine AS builder

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiar los archivos de definición de dependencias
COPY package*.json ./

# Instalar las dependencias del proyecto
RUN npm install

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto en el que la aplicación se ejecutará dentro del contenedor
EXPOSE 8001

# Comando para iniciar la aplicación
CMD [ "npm", "start" ]