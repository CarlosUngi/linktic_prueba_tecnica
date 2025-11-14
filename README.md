🚀 Desafío Técnico Full Stack: Plataforma de Productos e Inventario

Este documento consolida la arquitectura, el diseño y la estrategia de calidad para la solución de Microservicios Políglotas y Frontend Angular, cumpliendo con los estándares de la prueba de Líder Técnico.

Candidato: Carlos Andrés Garzón Arévalo
Identificación: 1030662725

1. Objetivo y Visión General del Proyecto

El objetivo principal es desarrollar una solución completa que incluya una API basada en microservicios y una interfaz frontend que consuma sus datos, cumpliendo con los estándares de robustez, calidad y documentación.

Estándar de Comunicación: Todas las APIs se adhieren estrictamente al estándar JSON API (v1.0), garantizando la uniformidad en la estructura de datos y errores.

2. Stack Tecnológico y Justificación Estratégica

La selección de tecnologías se basa en las técnologias que se requieren la convocatoria, la selección de que técnologia se utilizaria en que microservicio se escogió
 en una previsión de la complejidad futura del dominio de negocio:

Microservicio Productos (Node.js/Express): Elegido para operaciones CRUD de baja complejidad e intensivas en I/O. Se anticipa que este módulo tendrá un crecimiento de lógica mínimo.

Microservicio Inventario (Python/Flask): Elegido por su robusto ecosistema en manejo de datos y lógica compleja. El Inventario tiene potencial para escalar a temas avanzados (Kardex, modelos de predicción, logística), donde Python ofrece una mejor base para el futuro.

Base de Datos (MySQL - SQL): Seleccionada por ser gratuita y por sus propiedades Relacionales (ACID). La consistencia transaccional es crítica para el dominio de Producto e Inventario, facilitando la escalabilidad a futuros sistemas ERP.

Frontend (Angular): Framework robusto, tipado (TypeScript), ideal para aplicaciones empresariales con requisitos de mantenimiento a largo plazo.

3. Estructura y Convenciones de Nomenclatura

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

4. Patrones de Diseño Centrales

Patrón Repositorio (models/): Aísla la lógica de consulta SQL de la lógica de negocio, facilitando la migración a otras bases de datos sin modificar las capas superiores.

Patrón de Servicio (logic/): Contiene todas las reglas de negocio, validaciones y la coordinación entre dependencias. El servicio de Inventario es la única entidad que puede llamar al servicio de Productos.

5. Comunicación y Resiliencia (Estrategia de Fallos)

Autenticación Inter-Servicios (API Key)

Mecanismo: Autenticación Básica por API Key precompartida, enviada en el Header X-API-Key.

Validación: El Middleware en el servicio receptor valida la clave. El fallo retorna 401 Unauthorized con el código interno UNAUTHORIZED_ACCESS.

Manejo de Fallos (Resiliencia)

Requisito: Cada servicio será resiliente ante fallos temporales de sus dependencias.

Estrategia: Se implementa Reintentos (Retry) con Backoff Exponencial y un Timeout estricto en el servicio cliente (inventory-service al llamar a products-service). El fallo final retorna 503 SERVICE_UNAVAILABLE.

6. Estrategia de Pruebas y Cobertura (80%)

La estrategia se enfoca en la validación de la arquitectura y la resiliencia:

Cobertura: 80% de cobertura de Rama y Línea en el Backend, con énfasis en el código de resiliencia y el manejo de errores.

Pruebas Unitarias: Aislamiento de capas (logic/, models/, middleware/) mediante Mocking para garantizar el 100% de la lógica de negocio.

Pruebas de Integración (Resiliencia): Se simulan fallos temporales del servicio dependiente para probar que la lógica de Reintentos se ejecuta correctamente y que el fallo final retorna 503 SERVICE_UNAVAILABLE.

Contrato JSON API: Se prueba que todas las respuestas de éxito y error se adhieren estrictamente al formato JSON API.

7. Estrategia de Logging de Errores

Enfoque: Logs de errores (Nivel ERROR y CRITICAL) con formato estructurado.

Flujo: Un Middleware captura la excepción, construye un objeto JSON estructurado y lo serializa a texto plano.

Destino: Los logs de ambos microservicios se consolidan en archivos por día (YYYY-MM-DD.log) en la carpeta /logs.

Estructura del Log (Texto Plano): fecha| hora| bakendconerror| codigo_error| api_url| mensaje_error

8. Nota al Revisor (Metodología de Trabajo)

Declaro que la responsabilidad por la calidad del entregable es mía. La Inteligencia Artificial (Gemini) fue utilizada como herramienta estratégica para la organización de ideas, la estructuración de la arquitectura y la aceleración de la documentación, y generación de codigó, lo cual es fundamental para cumplir con el plazo de 2 días. La estructura de prompts y contextos fue diseñada por mí, reflejando mi experiencia en el diseño de estrategias de trabajo con IA.

9. Instrucciones de Instalación y Ejecución

Para ejecutar la plataforma completa, solo se requiere Docker y Docker Compose.


Lanzamiento: Ejecute docker compose up --build -d en la raíz del proyecto.

Acceso Frontend: Acceda a la aplicación web en http://localhost:4300.

acceso a la documentación swagger


http://localhost:8000/swagger-inventory/

http://localhost:8001/swagger-products/


10. La documentación de diseño y adicional se encuentra en la carpeta documents:



Temas para Profundizar (Referencias Teóricas)

JSON API (v1.0): Estándar para la estructura de datos y errores en APIs.

ACID: Propiedades de las transacciones de bases de datos relacionales.

Patrón Repositorio y Servicio: Patrones clave para el desacoplamiento de la lógica de negocio.

Backoff Exponencial: Algoritmo para la gestión de reintentos en arquitecturas distribuidas.

Trace ID: Identificador único para el rastreo de una solicitud a través de múltiples microservicios.