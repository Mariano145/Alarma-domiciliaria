# Patrones de Diseño — Sistema de Alarma para Hogar

Este documento describe los patrones de diseño GoF utilizados en la arquitectura del sistema, su propósito y dónde se aplican en el código.

---

## 1. Patrón State

**Tipo:** Comportamiento

**Propósito:** Permitir que el sistema de alarma cambie su comportamiento cuando cambia su estado interno. La alarma parece cambiar de clase.

### Dónde se aplica

**Componente:** `backend/services/alarm_state_manager.py`

**Contexto:** El sistema de alarma tiene 4 estados distintos con comportamientos diferentes:
- `DISARMED` — Sistema desactivado, los eventos se registran pero no disparan acciones
- `ARMING_WAIT` — Sistema armando, esperando que el usuario se retire
- `ARMED_COUNTDOWN` — Sistema armado, cuenta regresiva antes de activación completa
- `ALARM` — Alarma disparada

**Comportamiento por estado ante MOTION_DETECTED:**
- `DisarmedState` — Ignora el evento (podés moverte libremente en tu casa)
- `ArmingWaitState` — Ignora el evento (todavía estás saliendo)
- `ArmedCountdownState` — Transiciona a `ALARM` (detección de intruso)
- `AlarmTriggeredState` — Ignora el evento (ya está en alarma)

**Comportamiento por estado ante ARMING_TIMEOUT:**
- `DisarmedState` — Ignora el evento (no aplica en este estado)
- `ArmingWaitState` — Transiciona a `DISARMED` (el usuario no salió en el tiempo de gracia)
- `ArmedCountdownState` — Ignora el evento (no aplica en este estado)
- `AlarmTriggeredState` — Ignora el evento (no aplica en este estado)

**Comportamiento por estado ante ENTRY_TIMEOUT:**
- `DisarmedState` — Ignora el evento (no aplica en este estado)
- `ArmingWaitState` — Ignora el evento (no aplica en este estado)
- `ArmedCountdownState` — Transiciona a `ALARM` (el usuario no ingresó el PIN en el countdown)
- `AlarmTriggeredState` — Ignora el evento (ya está en alarma)

### Estructura de implementación

```
AlarmStateManager (Contexto)
  ├─ state: AlarmState
  ├─ transition_to(nuevo_estado)
  └─ handle_event(evento)

AlarmState (Interfaz de Estado)
  ├─ handle_door_state_changed(contexto, evento)
  ├─ handle_arm_button(contexto, evento)
  ├─ handle_panic_button(contexto, evento)
  ├─ handle_pin_attempt(contexto, evento)
  ├─ handle_motion_detected(contexto, evento)
  ├─ handle_arming_timeout(contexto, evento)
  └─ handle_entry_timeout(contexto, evento)

Estados Concretos:
  ├─ DisarmedState
  ├─ ArmingWaitState
  ├─ ArmedCountdownState
  └─ AlarmTriggeredState
```

### Por qué este patrón

- Cada estado encapsula su propia lógica de transiciones (ej: `ArmedCountdownState` transiciona a `AlarmTriggeredState` al abrir la puerta, pero `DisarmedState` lo ignora)
- Agregar nuevos estados (ej: `MAINTENANCE_MODE`) no requiere modificar las clases de estado existentes
- Elimina grandes bloques condicionales (`if estado == X and evento == Y`)
- Las transiciones de estado son explícitas y testeables

---

## 2. Patrón Strategy

**Tipo:** Comportamiento

**Propósito:** Definir una familia de algoritmos de analytics, encapsular cada uno y hacerlos intercambiables. El cliente puede elegir qué algoritmo usar independientemente del servicio que los orquesta.

### Dónde se aplica

**Componente:** `backend/services/analytics_service.py`

**Contexto:** El sistema necesita calcular métricas derivadas de eventos persistidos usando diferentes algoritmos:
- **Windowed Counts** (Conteos por ventana) — Cuenta eventos por tipo en una ventana de 10 minutos (incluye `motionDetections`)
- **PIN Fail Suspicious** (PIN fallido sospechoso) — Detección basada en histéresis (se activa con 3 fallos, se desactiva con 1 éxito)
- **Door Open Anomaly** (Anomalía de puerta abierta) — Detección basada en umbral (se activa si hay >6 aperturas en 10 min)

### Estructura de implementación

```
AnalyticsService (Contexto)
  ├─ algorithms: list[AnalyticsAlgorithm]
  └─ calculate_metrics(events) -> dict

AnalyticsAlgorithm (Interfaz de Estrategia)
  └─ process(events: list[Event]) -> dict

Estrategias Concretas:
  ├─ WindowedCountsAlgorithm
  ├─ PinFailHysteresisAlgorithm
  └─ DoorOpenAnomalyAlgorithm
```

### Por qué este patrón

- Cada algoritmo es testeable y modificable de forma independiente
- Agregar nuevos analytics (ej: `MovementPatternDetector`) solo requiere crear una nueva clase de estrategia
- El servicio no necesita conocer los detalles de cada algoritmo
- Los algoritmos pueden configurarse en tiempo de ejecución (ej: habilitar/deshabilitar analytics específicos)

---

## 3. Patrón Observer — Implementación #1: Cambios de Estado de Alarma

**Tipo:** Comportamiento

**Propósito:** Definir una dependencia uno-a-muchos entre el administrador de estado de la alarma y sus observadores, de modo que cuando el estado cambie, todos los componentes dependientes sean notificados y actualizados automáticamente.

### Dónde se aplica

**Componente:** `backend/services/alarm_state_manager.py` (Sujeto) + `backend/services/alarm_state_observer.py` (Observadores)

**Contexto:** Cuando la alarma transiciona entre estados (ej: `DISARMED` → `ARMING_WAIT`), múltiples componentes necesitan reaccionar:
- **Caché de estado en vivo** — Actualizar el estado cacheado para respuestas rápidas de `/api/v1/alarm/state`
- **Logger de eventos** — Registrar transiciones de estado para auditoría/debugging
- **Futuro: Broadcaster WebSocket** — Enviar cambios de estado a clientes frontend conectados

### Estructura de implementación

```
AlarmStateManager (Sujeto)
  ├─ observers: list[AlarmStateObserver]
  ├─ attach(observador)
  ├─ detach(observador)
  └─ notify_observers(estado_anterior, estado_nuevo)

AlarmStateObserver (Interfaz de Observador)
  └─ on_alarm_state_changed(estado_anterior, estado_nuevo, timestamp)

Observadores Concretos:
  ├─ LiveStateCacheObserver
  ├─ StateTransitionLoggerObserver
  └─ (futuro) WebSocketBroadcasterObserver
```

### Por qué este patrón

- El administrador de estado no necesita saber qué componentes están interesados en los cambios
- Se pueden agregar nuevos observadores sin modificar el sujeto (Principio Abierto/Cerrado)
- Desacopla la lógica de transición de estado de los efectos secundarios (caché, logging, broadcasting)
- Los observadores pueden habilitarse/deshabilitarse en tiempo de ejecución

---

## 4. Patrón Observer — Implementación #2: Ingesta de Nuevos Eventos

**Tipo:** Comportamiento

**Propósito:** Notificar a los componentes interesados cuando se ingieren nuevos eventos desde la ESP32, habilitando procesamiento en tiempo real y actualizaciones de analytics.

### Dónde se aplica

**Componente:** `backend/services/event_service.py` (Sujeto) + `backend/services/event_observer.py` (Observadores)

**Contexto:** Cuando llega un nuevo evento vía `POST /api/v1/events`, múltiples componentes necesitan reaccionar:
- **Invalidador de caché de analytics** — Marcar analytics cacheados como obsoletos para que el próximo request recalcule
- **Logger de stream de eventos** — Registrar el evento para debugging/monitoreo
- **Futuro: Sistema de alertas en tiempo real** — Disparar alertas inmediatas para eventos críticos (ej: botón de pánico)

### Estructura de implementación

```
EventService (Sujeto)
  ├─ observers: list[EventObserver]
  ├─ attach(observador)
  ├─ detach(observador)
  └─ notify_observers(evento)

EventObserver (Interfaz de Observador)
  └─ on_new_event(evento)

Observadores Concretos:
  ├─ AnalyticsCacheInvalidatorObserver
  ├─ EventStreamLoggerObserver
  └─ (futuro) RealTimeAlertObserver
```

### Por qué este patrón

- La lógica de ingesta de eventos está desacoplada del procesamiento posterior
- Se pueden agregar nuevos manejadores de eventos sin modificar `EventService`
- Los observadores pueden procesar eventos de forma asíncrona si es necesario
- Eventos críticos (botón de pánico) pueden disparar acciones inmediatas sin esperar polling

---

## Interacción entre Patrones

Los patrones trabajan juntos en el flujo de procesamiento de eventos:

```
ESP32 → POST /events → EventService.ingest()
                          ├─> Persistir en PostgreSQL
                          ├─> AlarmStateManager.handle_event()
                          │     ├─> Patrón State: transicionar si corresponde
                          │     └─> Observer #1: notificar observadores de cambio de estado
                          └─> Observer #2: notificar observadores de ingesta de eventos

Frontend → GET /alarm/state → LiveStateCacheObserver (alimentado por Observer #1)
Frontend → GET /analytics → AnalyticsService
                              └─> Patrón Strategy: ejecutar todos los algoritmos de analytics
```

---

## Tabla Resumen

| Patrón | Componente | Propósito | Clases Clave |
|--------|-----------|-----------|--------------|
| **State** | AlarmStateManager | Gestionar transiciones de estado de la alarma (7 eventos: puerta, armar, pánico, PIN, movimiento, arming_timeout, entry_timeout) | AlarmState, DisarmedState, ArmingWaitState, ArmedCountdownState, AlarmTriggeredState |
| **Strategy** | AnalyticsService | Encapsular algoritmos de analytics | AnalyticsAlgorithm, WindowedCountsAlgorithm, PinFailHysteresisAlgorithm, DoorOpenAnomalyAlgorithm |
| **Observer #1** | AlarmStateManager | Notificar cambios de estado | AlarmStateObserver, LiveStateCacheObserver, StateTransitionLoggerObserver |
| **Observer #2** | EventService | Notificar nuevos eventos | EventObserver, AnalyticsCacheInvalidatorObserver, EventStreamLoggerObserver |
