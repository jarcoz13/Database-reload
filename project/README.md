# Air Quality Monitoring System

Sistema completo de monitoreo de calidad del aire con frontend en Vue.js, backend en FastAPI y bases de datos PostgreSQL y MongoDB.

## 🏗️ Arquitectura

Este proyecto implementa la arquitectura completa descrita en `../src/Report_Latex/chapters/03_architecture.tex`.

### Capas de la Arquitectura:

1. **Clients & Web Frontend**: Vue.js 3 (Citizens, Researchers, Administrators)
2. **API Layer**: 
   - Public REST API (`/api/*`) - Para ciudadanos y investigadores
   - Admin REST API (`/admin/*`) - Para administración del sistema
3. **Data Persistence Layer**:
   - PostgreSQL con PostGIS (datos operacionales y analíticos)
   - MongoDB (logs, preferencias, audit trails)
4. **Batch Processing Layer**:
   - Ingestion Job (cada 30 minutos)
   - Normalizer & Validator (transformación de datos)
   - Daily Aggregation Job (02:00 UTC)
5. **Observability**: Logs estructurados en MongoDB

### Componentes de Datos (4 componentes):

1. **Geospatial & Monitoring**: Station, AirQualityReading, Pollutant, Provider, MapRegion
2. **Users & Access Control**: AppUser, Role, Permission, RolePermission
3. **Alerts & Recommendations**: Alert, Recommendation, ProductRecommendation
4. **Reporting & Analytics**: Report, AirQualityDailyStats

## 📁 Estructura del Proyecto

```
project/
├── docker-compose.yml          # Orquestación de servicios
├── front/                      # Aplicación Vue.js
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/
│       └── views/
├── back/                       # API FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── database/
│       ├── postgres_db.py
│       └── mongo_db.py
└── db/
    └── mongo-init.js           # Inicialización de MongoDB
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)

### Instalación y Ejecución

1. **Clonar el repositorio**:
```bash
cd /home/juferoga/repos/ud/Database-reload/project
```

2. **Configurar variables de entorno** (opcional):
```bash
# Backend
cp back/.env.example back/.env
# Frontend
cp front/.env.example front/.env
```

3. **Iniciar todos los servicios**:
```bash
docker-compose up -d
```

4. **Verificar que los servicios estén corriendo**:
```bash
docker-compose ps
```

### Acceso a los Servicios

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
  - Usuario: `airquality_user`
  - Contraseña: `airquality_pass`
  - Base de datos: `airquality_db`
- **MongoDB**: localhost:27017
  - Usuario: `admin`
  - Contraseña: `admin_pass`
  - Base de datos: `airquality_logs`
- **PgAdmin**: http://localhost:5050
  - Email: admin@airquality.com
  - Contraseña: admin
- **Mongo Express**: http://localhost:8081
  - Usuario: admin
  - Contraseña: admin

## 📊 Base de Datos

### PostgreSQL (Datos Operacionales)

La base de datos PostgreSQL almacena:
- Estaciones de monitoreo
- Lecturas de calidad del aire
- Usuarios y permisos
- Alertas y recomendaciones
- Reportes y estadísticas

**Esquema inicializado automáticamente** desde [init_database.sql](../docs/Diagram_ER/init_database.sql)

#### Usuarios de Prueba

El sistema inicializa automáticamente 3 usuarios de prueba:

| Username   | Email            | Password | Role    | Location |
|-----------|------------------|----------|---------|----------|
| testuser1 | user1@test.com   | hash123  | Citizen | Bogotá   |
| testuser2 | user2@test.com   | hash456  | Citizen | Medellín |
| testuser3 | user3@test.com   | hash789  | Citizen | Cali     |

**Nota**: En producción, cambiar estos usuarios y usar contraseñas con hash seguro (bcrypt/argon2).

### MongoDB (Logs y Datos No Estructurados)

MongoDB almacena:
- Logs de API
- Logs de errores
- Historial de ingestión de datos
- Historial de alertas

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f [servicio]

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v

# Reconstruir imágenes
docker-compose build

# Reiniciar un servicio específico
docker-compose restart [servicio]
```

### Frontend (Vue.js)

```bash
# Entrar al contenedor
docker-compose exec frontend sh

# Instalar nuevas dependencias
docker-compose exec frontend npm install [paquete]

# Ver logs del frontend
docker-compose logs -f frontend
```

### Backend (FastAPI)

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Ver logs del backend
docker-compose logs -f backend

# Ejecutar migraciones (cuando se implementen)
docker-compose exec backend alembic upgrade head
```

### Bases de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec postgres psql -U airquality_user -d airquality_db

# Acceder a MongoDB
docker-compose exec mongodb mongosh -u admin -p admin_pass

# Backup de PostgreSQL
docker-compose exec postgres pg_dump -U airquality_user airquality_db > backup.sql

# Restaurar PostgreSQL
docker-compose exec -T postgres psql -U airquality_user airquality_db < backup.sql
```

## 📝 Desarrollo

### Agregar Nuevas Dependencias

**Frontend**:
```bash
cd front
npm install [paquete]
# Reconstruir imagen
docker-compose build frontend
```

**Backend**:
```bash
cd back
# Agregar a requirements.txt
echo "nuevo-paquete==version" >> requirements.txt
# Reconstruir imagen
docker-compose build backend
```

### Hot Reload

Ambos servicios (frontend y backend) tienen hot reload habilitado:
- Los cambios en el código se reflejan automáticamente
- No es necesario reiniciar los contenedores para ver los cambios

## 🌐 API y CORS

### Configuración de CORS

El backend está configurado para aceptar peticiones desde:
- `http://localhost:5173` (Frontend local)
- `http://127.0.0.1:5173` (Frontend local via 127.0.0.1)
- `http://localhost:3000` (Desarrollo alternativo)

En modo **DEBUG=true**, CORS acepta todos los orígenes (`["*"]`).

### Endpoints Principales

- **GET /api/stations** - Listar estaciones de monitoreo
- **GET /api/readings** - Obtener lecturas de calidad del aire
- **GET /api/alerts?user_id={id}** - Listar alertas del usuario
- **POST /api/alerts?user_id={id}** - Crear nueva alerta
- **PATCH /api/alerts/{alert_id}?user_id={id}** - Actualizar alerta
- **DELETE /api/alerts/{alert_id}?user_id={id}** - Eliminar alerta

Ver documentación completa en: http://localhost:8000/docs

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Las credenciales en este proyecto son para desarrollo. En producción:

1. Cambiar todas las contraseñas
2. Usar variables de entorno seguras
3. Configurar certificados SSL/TLS
4. Implementar autenticación JWT robusta
5. Habilitar HTTPS
6. Configurar firewall y reglas de red
7. Deshabilitar modo DEBUG
8. Configurar CORS con orígenes específicos

## 📚 Documentación Adicional

- **Diagrama ER**: [Diagram_ER.puml](../docs/Diagram_ER/Diagram_ER.puml)
- **Esquema DBML**: [Diagram_ER.dbml](../docs/Diagram_ER/Diagram_ER.dbml)
- **SQL Schema**: [init_database.sql](../docs/Diagram_ER/init_database.sql)

## 🐛 Solución de Problemas

### Puerto ya en uso
```bash
# Ver qué proceso usa el puerto
lsof -i :5173  # o el puerto que esté ocupado
# Cambiar el puerto en docker-compose.yml
```

### Problemas de permisos
```bash
# Dar permisos a los directorios
sudo chown -R $USER:$USER .
```

### Reiniciar desde cero
```bash
# Eliminar todo y empezar de nuevo
docker-compose down -v
docker-compose up -d --build
```

## 📖 Endpoints API Principales

Una vez que el backend esté corriendo, visita http://localhost:8000/docs para ver la documentación completa interactiva de la API.

### Public API (`/api/*`) - Para Ciudadanos e Investigadores

**Estaciones:**
- `GET /api/stations` - Lista de estaciones de monitoreo
- `GET /api/stations/{station_id}` - Detalles de una estación

**Lecturas de Calidad del Aire:**
- `GET /api/readings/current` - Lecturas actuales (últimas 24h)
- `GET /api/readings/historical` - Lecturas históricas (rango de fechas)
- `GET /api/readings/latest/{station_id}` - Última lectura por contaminante

**Estadísticas Diarias:**
- `GET /api/stats/daily` - Estadísticas agregadas por día

**Alertas:**
- `GET /api/alerts` - Alertas del usuario
- `POST /api/alerts` - Crear nueva alerta
- `PATCH /api/alerts/{alert_id}` - Actualizar alerta
- `DELETE /api/alerts/{alert_id}` - Eliminar alerta

**Recomendaciones:**
- `GET /api/recommendations` - Recomendaciones de salud personalizadas

**Contaminantes:**
- `GET /api/pollutants` - Lista de contaminantes monitoreados

### Admin API (`/admin/*`) - Para Administradores

**Monitoreo del Sistema:**
- `GET /admin/health` - Estado de salud completo del sistema
- `GET /admin/stats` - Estadísticas del sistema

**Gestión de Jobs:**
- `GET /admin/jobs/status` - Estado de los jobs programados
- `POST /admin/jobs/run/{job_name}` - Ejecutar job manualmente

**Gestión de Proveedores:**
- `GET /admin/providers` - Lista de proveedores de datos
- `POST /admin/providers` - Crear proveedor
- `DELETE /admin/providers/{provider_id}` - Eliminar proveedor

**Gestión de Estaciones:**
- `GET /admin/stations` - Lista de estaciones (vista admin)
- `POST /admin/stations` - Crear estación
- `PUT /admin/stations/{station_id}` - Actualizar estación
- `DELETE /admin/stations/{station_id}` - Eliminar estación

**Gestión de Usuarios:**
- `GET /admin/users` - Lista de usuarios
- `GET /admin/users/{user_id}` - Detalles de usuario
- `PATCH /admin/users/{user_id}` - Actualizar usuario
- `DELETE /admin/users/{user_id}` - Desactivar usuario

**Roles y Permisos:**
- `GET /admin/roles` - Lista de roles
- `GET /admin/permissions` - Lista de permisos

**Logs de Auditoría:**
- `GET /admin/logs/api` - Logs de acceso API
- `GET /admin/logs/errors` - Logs de errores
- `GET /admin/logs/ingestion` - Logs de ingesta de datos

## 👥 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Ver archivo [LICENSE](../LICENSE) para más detalles.

## 🎯 Estado de Implementación

### ✅ Completado

- [x] Modelos SQLAlchemy para las 14 entidades
- [x] Schemas Pydantic para validación
- [x] Public REST API (10+ endpoints)
- [x] Admin REST API (15+ endpoints)
- [x] Servicios mock para APIs externas (AQICN, Google, IQAir)
- [x] Batch Jobs:
  - [x] Ingestion Job (programado cada 30 min)
  - [x] Normalizer & Validator
  - [x] Daily Aggregation Job (02:00 UTC)
- [x] Job Scheduler con APScheduler
- [x] Inicialización automática de BD con datos seed
- [x] Estructura completa de 4 componentes de datos
- [x] Logging en MongoDB (api_logs, error_logs, data_ingestion_logs)
- [x] Docker Compose con todos los servicios

### 🚧 Por Implementar

1. **Autenticación JWT**: Sistema completo de auth con tokens
2. **Frontend Vue Avanzado**: 
   - Integración real con API
   - Mapas con Leaflet
   - Gráficos con Chart.js
   - Dashboard personalizable
3. **WebSockets**: Datos en tiempo real
4. **Tests**: Unitarios e integración (pytest)
5. **CI/CD**: GitHub Actions pipeline
6. **Caching**: Redis para queries frecuentes
7. **Rate Limiting**: Protección contra abuso
8. **API Documentation**: OpenAPI specs mejorados

## 📚 Documentación Técnica

- **Arquitectura Completa**: [back/ARCHITECTURE.md](back/ARCHITECTURE.md)
- **Diagrama ER**: [../docs/Diagram_ER/Diagram_ER.puml](../docs/Diagram_ER/Diagram_ER.puml)
- **Schema SQL**: [../docs/Diagram_ER/init_database.sql](../docs/Diagram_ER/init_database.sql)
- **Documento de Arquitectura**: [../src/Report_Latex/chapters/03_architecture.tex](../src/Report_Latex/chapters/03_architecture.tex)

## ✅ Validación del Sistema

Para verificar que todos los componentes están configurados correctamente:

```bash
./validate.sh
```

Este script verifica:
- ✓ Contenedores Docker en ejecución
- ✓ Inicialización de base de datos
- ✓ Usuarios de prueba creados
- ✓ Endpoints de API funcionando
- ✓ Configuración de CORS
- ✓ Ingesta de datos operativa
- ✓ Frontend accesible

Ver [CHANGELOG.md](CHANGELOG.md) para registro completo de cambios.
