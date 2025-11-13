#!/bin/bash

# ===============================================
# SCRIPT DE CONFIGURACIÓN INICIAL DEL PROYECTO
# Crea la estructura de directorios basada en el
# Canvas de Arquitectura (Clean Architecture adaptada).
# ===============================================

echo "Iniciando la configuración de directorios del proyecto..."

# 1. Directorios principales de la raíz
echo "-> Creando directorios raíz (backend, frontend, logs, etc.)."
mkdir -p backend frontend database storage logs test_results

# 2. Archivos de configuración y orquestación
echo "-> Creando archivos de configuración genéricos (env, docker-compose)."
touch .env
touch docker-compose.yml
touch README.md

# 3. Estructura interna del Backend (Común a ambos Microservicios)
# Estas carpetas se replicarán dentro de cada microservicio.
BACKEND_COMMON_DIRS="config db middleware"

# 4. Estructura del Products Microservice (Node.js/Express)
PRODUCTS_SERVICE_NAME="products-service"
PRODUCTS_SERVICE_DIRS="${PRODUCTS_SERVICE_NAME}/routes ${PRODUCTS_SERVICE_NAME}/logic ${PRODUCTS_SERVICE_NAME}/models"

echo "-> Creando estructura para el microservicio de Productos (${PRODUCTS_SERVICE_NAME})."
mkdir -p backend/$PRODUCTS_SERVICE_NAME

# Crear directorios comunes dentro de products-service
for dir in $BACKEND_COMMON_DIRS; do
    mkdir -p backend/$PRODUCTS_SERVICE_NAME/$dir
done

# Crear directorios específicos de capa
mkdir -p backend/$PRODUCTS_SERVICE_DIRS
touch backend/$PRODUCTS_SERVICE_NAME/index.js # Archivo principal
touch backend/$PRODUCTS_SERVICE_NAME/package.json # Para dependencias

# 5. Estructura del Inventory Microservice (Python/Flask)
INVENTORY_SERVICE_NAME="inventory-service"
INVENTORY_SERVICE_DIRS="${INVENTORY_SERVICE_NAME}/routes ${INVENTORY_SERVICE_NAME}/logic ${INVENTORY_SERVICE_NAME}/models"

echo "-> Creando estructura para el microservicio de Inventario (${INVENTORY_SERVICE_NAME})."
mkdir -p backend/$INVENTORY_SERVICE_NAME

# Crear directorios comunes dentro de inventory-service
for dir in $BACKEND_COMMON_DIRS; do
    mkdir -p backend/$INVENTORY_SERVICE_NAME/$dir
done

# Crear directorios específicos de capa
mkdir -p backend/$INVENTORY_SERVICE_DIRS
touch backend/$INVENTORY_SERVICE_NAME/app.py # Archivo principal
touch backend/$INVENTORY_SERVICE_NAME/requirements.txt # Para dependencias

# 6. Estructura del Frontend (Angular)
echo "-> Creando esqueleto de Frontend (Angular)."
mkdir -p frontend/src/app/services frontend/src/app/components frontend/src/app/middleware

echo ""
echo "¡Estructura de directorios creada con éxito!"
echo "Para ejecutar, haz: bash setup_project.sh"
echo "Para verificar, haz: tree" # Asume que 'tree' está instalado