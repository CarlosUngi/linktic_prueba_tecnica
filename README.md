🚀 Desafío Técnico Full Stack: Plataforma de Productos e Inventario

Este documento consolida la arquitectura, el diseño y la estrategia de calidad para la solución de Microservicios Políglotas y Frontend Angular, cumpliendo con los estándares de la prueba de Líder Técnico.

Candidato: Carlos Andrés Garzón Arévalo
Identificación: 1030662725

Objetivo y Visión General del Proyecto

El objetivo principal es desarrollar una solución completa que incluya una API basada en microservicios y una interfaz frontend que consuma sus datos, cumpliendo con los estándares de robustez, calidad y documentación.

Estándar de Comunicación: Todas las APIs se adhieren estrictamente al estándar JSON API (v1.0), garantizando la uniformidad en la estructura de datos y errores.

Stack Tecnológico y Justificación Estratégica

La selección de tecnologías se basa en las tecnologías requeridas por la convocatoria y una decisión estratégica basada en la complejidad futura del dominio de negocio:

Microservicio Productos (Node.js/Express): Elegido para operaciones CRUD de baja complejidad e intensivas en I/O. Se anticipa que este módulo tendrá un crecimiento de lógica mínimo.

Microservicio Inventario (Python/Flask): Elegido por su robusto ecosistema en manejo de datos y lógica compleja. El Inventario tiene potencial para escalar a temas avanzados (Kardex, modelos de predicción, logística), donde Python ofrece una mejor base para el futuro.

Base de Datos (MySQL - SQL): Seleccionada por ser gratuita y por sus propiedades Relacionales (ACID). La consistencia transaccional es crítica para el dominio de Producto e Inventario, facilitando la escalabilidad a futuros sistemas ERP.

Frontend (Angular): Framework robusto, tipado (TypeScript), ideal para aplicaciones empresariales con requisitos de mantenimiento a largo plazo.

2.1. Descripción de la Aplicación Web (Frontend)

La aplicación web, desarrollada en Angular, actúa como una plataforma simple de ventas y gestión de stock. Su funcionalidad principal es:

Listado de Productos: Muestra los productos disponibles junto con su stock actual (obtenido del Microservicio de Inventario).

Simulación de Compra: Permite al usuario seleccionar la cantidad de unidades que desea comprar.

Gestión de Inventario: Al confirmar la compra, la aplicación realiza una solicitud al servicio de Inventario para restar la cantidad correspondiente del stock.

Consolidación de Eventos: El servicio de Inventario, al modificar el stock, emite un evento que puede ser visualizado en tiempo real usando el comando docker compose logs inventory-service.

Estructura y Convenciones de Nomenclatura

Convenciones de Nomenclatura
Todos los nombramientos de variables, métodos y bases de datos se harán en Inglés. Se omite el uso de tildes.

Código (Backend/Frontend): Se utiliza Camel Case (ej. variableExample, productName).

Base de Datos (Tablas/Campos): Se utiliza Snake Case (ej. variable_example, product_name) para evitar la sensibilidad a mayúsculas en SQL.

Estructura de Directorios
La arquitectura sigue una convención de Clean Architecture:

Raíz: docker-compose.yml, .env, README_ES.md.

/backend/: Contiene /products-service y /inventory-service.

/config/: Almacena valores constantes y error_codes.json.

/db/: Gestiona el Pool de Conexiones a MySQL.

/middleware/: Funciones de pre/post-procesamiento (Autenticación, Logging, Reintentos).

/models/: Patrón Repositorio (Abstracción de la base de datos).

/logic/: Patrón de Servicio (Lógica de negocio y coordinación).

/database/: Contiene /data (volúmenes de MySQL), /backups y /init (scripts SQL).

/logs/: Destino de los logs estructurados.

3.1. Diseño de la Base de Datos (DDL)

El esquema de la base de datos se basa en dos tablas relacionales, definidas en los archivos DDL (01-creacion-inicial.sql y 02-poblar-data.sql) que se ejecutan automáticamente al levantar el contenedor de MySQL con docker compose up.

Tabla

Microservicio que la Gestiona

Descripción

products

Products Microservice

Almacena los datos maestros del producto (nombre, precio, descripción).

inventory

Inventory Microservice

Almacena el stock disponible. Existe una relación 1:1 con la tabla products.

Estructura y Relaciones Clave:

products: PK id, restricción UNIQUE en name, restricción CHECK para price > 0.

inventory: PK id, campo product_id como clave foránea (FK) a products.id.

Relación 1:1: El campo product_id tiene una restricción UNIQUE KEY para asegurar que solo exista un registro de inventario por producto.

Resiliencia (Eventos): El campo last_inventory_update se actualiza automáticamente (ON UPDATE CURRENT_TIMESTAMP), sirviendo como un indicador de evento para que otros sistemas (o el log de Docker) detecten el momento exacto del cambio de stock.

Restricción: El campo available_stock tiene una restricción CHECK para asegurar que el stock nunca sea negativo.

Patrones de Diseño Centrales

Patrón Repositorio (models/): Aísla la lógica de consulta SQL de la lógica de negocio, facilitando la migración a otras bases de datos sin modificar las capas superiores.

Patrón de Servicio (logic/): Contiene todas las reglas de negocio, validaciones y la coordinación entre dependencias. El servicio de Inventario es la única entidad que puede llamar al servicio de Productos.

Comunicación y Resiliencia (Estrategia de Fallos)

Autenticación Inter-Servicios (API Key)

Mecanismo: Autenticación Básica por API Key precompartida y estática, enviada en el Header X-API-Key.

Flujo: El Inventory Service (Cliente) envía la clave secreta (PRODUCTS_API_KEY leída desde el .env) al Products Service.

Validación (Middleware): El middleware en el Products Service (Receptor) valida la clave.

Fallo JSON API: Un fallo de autenticación retorna 401 Unauthorized con la siguiente estructura estandarizada:

{
  "errors": [
    {
      "status": "401",
      "code": "UNAUTHORIZED_ACCESS",
      "title": "Acceso No Autorizado",
      "detail": "La API Key proporcionada es incorrecta o falta el header X-API-Key."
    }
  ]
}


Manejo de Fallos (Resiliencia)

Estrategia: Se implementa Reintentos (Retry) con Backoff Exponencial y un Timeout estricto en el servicio cliente (inventory-service al llamar a products-service).

Fallo Final: El fallo final, tras agotar los reintentos, retorna 503 SERVICE_UNAVAILABLE.

Estrategia de Pruebas y Cobertura

La estrategia se enfoca en la validación de la arquitectura, el desacoplamiento y la resiliencia.

Cobertura Mínima: 80% de cobertura de Rama y Línea en el Backend, con énfasis en el código de resiliencia y el manejo de errores.

Pruebas Unitarias: Aislamiento de capas (logic/, models/, middleware/) mediante Mocking para garantizar el 100% de la lógica de negocio.

Pruebas de Integración (Resiliencia): Se simulan fallos temporales del servicio dependiente para probar que la lógica de Reintentos se ejecuta correctamente y que el fallo final retorna 503 SERVICE_UNAVAILABLE.

Frontend (Angular): Cobertura del 30%-40%, enfocada en la lógica de los Servicios y los Interceptors HTTP.

Reporte: El reporte HTML de cobertura se genera en el directorio test_results/.

Estrategia de Logging de Errores

Enfoque: Logs de errores (Nivel ERROR y CRITICAL) con formato estructurado para facilitar el análisis.

Flujo de Implementación:

Un Middleware (Node.js) o Decorator (Python/Flask) captura la excepción 4xx/5xx.

Se construye un objeto JSON estructurado interno (facilitando futura integración con Kibana/DataDog).

Este objeto JSON se serializa al formato de texto plano final.

Destino: Los logs de ambos microservicios se consolidan en archivos por día (YYYY-MM-DD.log) en la carpeta /logs (montada por Docker).

Estructura del Log (Texto Plano):
fecha| hora| bakendconerror| codigo_error| api_url| mensaje_error

Nota al Revisor (Metodología de Trabajo)

Declaro que la responsabilidad por la calidad del entregable es mía. La Inteligencia Artificial (Gemini) fue utilizada como herramienta estratégica para la organización de ideas, la estructuración de la arquitectura y la aceleración de la documentación, y generación de código, lo cual es fundamental para cumplir con el plazo de 2 días. La estructura de prompts y contextos fue diseñada por mí, reflejando mi experiencia en el diseño de estrategias de trabajo con IA.

Instrucciones de Instalación y Ejecución

Para ejecutar la plataforma completa, solo se requiere Docker y Docker Compose.

Lanzamiento: Ejecute docker compose up --build -d en la raíz del proyecto.

Acceso Frontend: Acceda a la aplicación web en http://localhost:4200 (Puerto HOST).

Acceso a la Documentación Adicional: Acceda a los documentos de diseño y ayuda en http://localhost:8080/.

Documentación Swagger (APIs):

Inventario: http://localhost:8000/swagger-inventory/

Productos: http://localhost:8001/swagger-products/

La documentación de diseño y adicional se encuentra en la carpeta documents/.

Configuración de Variables de Entorno (Claves)

Las variables se cargan desde el archivo .env y son críticas para la conectividad y seguridad del sistema:

Variable

Consumidor Principal

Propósito Clave

MYSQL_HOST

Docker / Microservicios

Nombre del servicio Docker de la DB (mysql_db).

PRODUCTS_API_KEY

Inventory Service (Cliente) & Products Service (Servidor)

Clave secreta para autenticar llamadas inter-servicio (Header X-API-Key). CRÍTICA.

PRODUCTS_SERVICE_URL_INTERNAL

Inventory Service (logic/)

URL interna que el Inventory Service usa para llamadas síncronas a Products Service (ej. http://products-service:3000). CRÍTICA.

INVENTORY_SERVICE_PORT_HOST

Host

Puerto externo para el Microservicio de Inventario (8000).

PRODUCTS_SERVICE_PORT_HOST

Host

Puerto externo para el Microservicio de Productos (8001).

Temas para Profundizar (Referencias Teóricas)

JSON API (v1.0): Estándar para la estructura de datos y errores en APIs.

ACID: Propiedades de las transacciones de bases de datos relacionales.

Patrón Repositorio y Servicio: Patrones clave para el desacoplamiento de la lógica de negocio.

Backoff Exponencial: Algoritmo para la gestión de reintentos en arquitecturas distribuidas.

Trace ID: Identificador único para el rastreo de una solicitud a través de múltiples microservicios.