# Arquitectura del Sistema — Alarma para Hogar IoT

## 1. Contexto y Objetivo

El sistema es una **alarma de seguridad para hogar** basada en IoT que permite:
- Monitorear eventos de sensores (puerta, movimiento, botones, teclado PIN)
- Gestionar estados de la alarma (desarmada, armando, armada, alarma disparada)
- Persistir histórico de eventos en base de datos
- Visualizar estado en tiempo real y análisis histórico desde un frontend web
- Detectar anomalías mediante algoritmos de análisis

**Actores principales:**
- **Usuario del hogar** — Arma/desarma la alarma, consulta estado desde frontend
- **ESP32 (firmware)** — Dispositivo IoT que captura eventos de sensores y los envía al backend
- **Auditor del sistema** — Consulta histórico y métricas de analytics

---

## 2. Arquitectura del Sistema: Distribuida REST

El sistema sigue una **arquitectura distribuida REST** donde los componentes se comunican exclusivamente vía HTTP REST. Cada componente tiene su propia arquitectura interna (ver sección 3 para el detalle del backend).

El sistema está compuesto por 4 containers principales:

```
┌─────────────────┐
│   ESP32         │
│   (Firmware)    │
│   C++/Arduino   │
└────────┬────────┘
         │ HTTP POST /api/v1/events
         ▼
┌─────────────────────────────────────────┐
│   Backend (Flask + Python)              │
│   - Controllers (HTTP)                  │
│   - Services (lógica de negocio)        │
│   - Repositories (acceso a datos)       │
│   - Patrones: State, Strategy, Observer │
└────────┬────────────────────────────────┘
         │ SQL (SQLAlchemy)
         ▼
┌─────────────────┐
│   PostgreSQL    │
│   (Database)    │
│   Tabla: events │
└─────────────────┘
         ▲
         │ HTTP GET (polling)
         │
┌────────┴────────┐
│   Frontend      │
│   React + TS    │
└─────────────────┘
```

**Flujo de datos:**
1. ESP32 captura eventos de sensores → envía a Backend vía POST
2. Backend valida, persiste en PostgreSQL, actualiza estado de alarma, notifica observers
3. Frontend hace polling a Backend vía GET para obtener estado actual, histórico y analytics
4. Frontend renderiza dashboards en tiempo real y tablas históricas

---

## 3. Arquitectura por Capas (Backend)

El backend sigue una **arquitectura en capas** clásica con separación de responsabilidades:

### Capa 1: Controllers (HTTP)
**Responsabilidad:** Recibir requests HTTP, validar parámetros, delegar a services, retornar responses.

**Clases:**
- `EventController` — Endpoints de ingesta y consulta de eventos
- `AlarmController` — Endpoint de estado actual de alarma
- `AnalyticsController` — Endpoint de métricas calculadas

**No contiene:** lógica de negocio, acceso directo a DB, validaciones complejas.

### Capa 2: Services (Lógica de negocio)
**Responsabilidad:** Orquestar operaciones, aplicar reglas de negocio, gestionar estado, notificar observers.

**Clases:**
- `EventService` — Valida eventos, persiste, notifica observers de ingesta
- `AlarmStateManager` — Mantiene estado actual, gestiona transiciones (patrón State), notifica observers de estado
- `AnalyticsService` — Ejecuta algoritmos de analytics (patrón Strategy)

**No contiene:** lógica HTTP, serialización/deserialización de requests.

### Capa 3: Repositories (Acceso a datos)
**Responsabilidad:** Abstraer el acceso a PostgreSQL, ejecutar queries, mapear resultados a modelos.

**Clases:**
- `EventRepository` — Insertar y consultar eventos con filtros

**No contiene:** lógica de negocio, validaciones de dominio.

### Capa 4: Models (Entidades de dominio)
**Responsabilidad:** Representar las entidades del sistema como objetos Python.

**Clases:**
- `Event` — Evento persistido (eventId, type, deviceId, payload, receivedAt)
- `AlarmStateResponse` — Estado actual de alarma
- `AnalyticsResponse` — Resultado de algoritmos

---

## 4. Patrones de Diseño

El sistema utiliza 4 patrones GoF para resolver problemas específicos de la arquitectura:

| Patrón | Problema que resuelve | Dónde se aplica |
|--------|----------------------|-----------------|
| **State** | La alarma tiene 4 estados con comportamientos diferentes ante los mismos eventos | `AlarmStateManager` + 4 estados concretos |
| **Strategy** | Necesitamos 3 algoritmos de analytics intercambiables | `AnalyticsService` + 3 estrategias concretas |
| **Observer #1** | Múltiples componentes necesitan reaccionar cuando cambia el estado de la alarma | `AlarmStateManager` notifica a `LiveStateCacheObserver`, `StateTransitionLoggerObserver` |
| **Observer #2** | Múltiples componentes necesitan reaccionar cuando llega un nuevo evento | `EventService` notifica a `AnalyticsCacheInvalidatorObserver`, `EventStreamLoggerObserver` |

**Ver detalle completo en:** [`design-patterns.md`](./design-patterns.md)

---

## 5. Decisiones Arquitectónicas

### 5.1 Framework Backend: Flask
**Decisión:** Usar Flask como framework backend único.

**Razones:**
- Ecosistema maduro con extensiones para validación (Pydantic), DB (SQLAlchemy), migraciones (Alembic)
- Equipo familiarizado con Python

**Alternativas consideradas:** NestJS (TypeScript), Spring Boot (Java).

### 5.2 Base de Datos: PostgreSQL
**Decisión:** Usar PostgreSQL como base de datos relacional.

**Razones:**
- Requisito explícito de la consigna
- Soporte en Flask vía SQLAlchemy

### 5.3 Comunicación: REST HTTP
**Decisión:** Usar HTTP REST para comunicación ESP32↔Backend y Frontend↔Backend.

**Razones:**
- Requisito explícito de la consigna

**Alternativas consideradas:** WebSockets — descartado por complejidad adicional y porque polling desde frontend es suficiente para el caso de uso.

### 5.4 Patrón State para gestión de alarma
**Decisión:** Usar patrón State para modelar la máquina de estados de la alarma.

**Razones:**
- La alarma tiene 4 estados mutuamente excluyentes con comportamientos diferentes
- Cada estado encapsula su propia lógica de transiciones

**Alternativas consideradas:** Command (para requests), Factory (para creación), Decorator (para responsabilidades dinámicas) — descartados porque no modelan estados mutuamente excluyentes.

### 5.5 Frontend: React con polling
**Decisión:** Usar React y polling periódico al backend para actualización en vivo.

**Razones:**
- Requisito explícito de la consigna
- Polling simple de implementar y suficiente para actualización en tiempo real (intervalo de 2-5 segundos)
- No requiere infraestructura adicional (WebSocket server)

**Alternativas consideradas:** WebSockets — descartados por complejidad adicional para el alcance del proyecto.

---

## 6. Restricciones y Consideraciones

### Restricciones técnicas
- **Backend único:** La consigna exige un solo framework backend activo en la entrega final
- **PostgreSQL obligatorio:** La consigna exige PostgreSQL para persistencia histórica
- **REST obligatorio:** La consigna exige REST para comunicación entre componentes
- **Frontend no puede hablar directo con ESP32:** Todo debe pasar por el backend
- **Código en inglés:** Todo el código fuente y comentarios técnicos deben estar en inglés
- **Documentación en español:** Informes, Jira y documentación pueden estar en español

### Consideraciones de diseño
- **Polling vs WebSockets:** Se eligió polling por simplicidad.
- **Sensor de movimiento:** Solo dispara alarma en estado `ARMED_COUNTDOWN`. En otros estados se ignora para evitar falsas alarmas cuando el usuario está en casa.
- **Botón de pánico:** Dispara alarma inmediatamente sin importar el estado actual (override de seguridad).

---

## 7. Referencias

- **Patrones de diseño:** [`design-patterns.md`](./design-patterns.md)
- **Contrato API (OpenAPI):** [`OpenAPI/openapi.yaml`](./OpenAPI/openapi.yaml)
- **Consigna del proyecto:** [`CONSIGNA.md`](./CONSIGNA.md)
