# Documentación Técnico-Funcional: Contrato de API (Home Alarm)

Este documento presenta el resumen técnico de la API diseñada para el sistema de alarma hogareña inteligente. Sirve como guía de referencia para el equipo de desarrollo del Frontend, Backend y Firmware (ESP32).

El contrato oficial está completamente especificado bajo el estándar OpenAPI 3.0 en el archivo `docs/openapi.yaml`.

---

## 1. Arquitectura General del Sistema

El sistema opera bajo un flujo de tres capas bien definidas:
1. **Firmware (ESP32):** El nodo físico de hardware. Detecta los eventos del entorno (apertura de puertas, pulsación de botones, intentos de clave) y los ingesta en tiempo real hacia el servidor central.
2. **Backend (Servidor central):** Valida de forma estricta los datos entrantes, los persiste cronológicamente en la base de datos (PostgreSQL), computa las máquinas de estado de la alarma y ejecuta algoritmos analíticos sobre ventanas de tiempo.
3. **Frontend (Aplicación de usuario):** Consume los endpoints del backend para renderizar la interfaz web/móvil en vivo, mostrando el estado actual de la alarma, alertas analíticas y el historial paginado de eventos.

---

## 2. Detalle Funcional de los Endpoints

La API cuenta con 4 endpoints clave distribuidos por tags según su responsabilidad:

### 📥 Ingesta de Eventos
* **Ruta:** `POST /api/v1/events` (Consumido por el **ESP32**)
* **Descripción:** Permite al microcontrolador reportar novedades en la casa.
* **Tipos de Eventos Soportados (`type`):**
  * `DOOR_STATE_CHANGED`: Reporta si el sensor magnético detectó que la puerta pasó a `OPEN` o `CLOSED`.
  * `ARM_BUTTON_PRESSED`: Alguien presionó el botón físico para activar el sistema.
  * `PANIC_BUTTON_PRESSED`: Disparo inmediato por botón de pánico de hardware.
  * `PIN_ATTEMPT`: Envía el resultado (`SUCCESS` o `FAIL`) de una clave ingresada en el teclado físico. *Nota de seguridad: El PIN se valida localmente en la placa para no transmitir contraseñas por la red.*
* **Respuesta Exitosa (`201 Created`):** Devuelve un JSON con `{ eventId, receivedAt }`. El backend genera el ID único y estampa el tiempo exacto del servidor para garantizar la consistencia horaria, independientemente del reloj de la placa.

### 📜 Historial de Eventos
* **Ruta:** `GET /api/v1/events` (Consumido por el **Frontend**)
* **Descripción:** Trae la lista de todo lo que pasó en la casa para mostrar en formato de tabla o bitácora.
* **Características Técnicas:**
  * **Ordenamiento:** Fijo descendente (`receivedAt DESC`). Lo más nuevo siempre aparece primero.
  * **Filtros Dinámicos:** Se puede buscar por rango de fechas (`from`, `to`), por origen (`deviceId`) o por tipo de evento (`type`).
  * **Paginación:** Basada en parámetros de posición (`limit` y `offset`). Por defecto trae 50 registros y soporta un máximo de 200 por llamada. El payload final contiene el array de ítems limpios (`eventId`, `receivedAt`, `type`, `payload`) junto con el `total` de registros para el manejo de la interfaz.

### 🔴 Estado en Vivo de la Alarma
* **Ruta:** `GET /api/v1/alarm/state` (Consumido por el **Frontend**)
* **Descripción:** Devuelve la situación en tiempo real de la alarma para saber si el usuario debe poner la clave o si la sirena está sonando.
* **Códigos de Estado (`AlarmStateCode`):**
  * `DISARMED`: Alarma apagada.
  * `ARMING_WAIT`: Período de gracia inicial (Espera de salida).
  * `ARMED_COUNTDOWN`: Cuenta regresiva de entrada (Cuando abrís la puerta y tenés segundos para poner el PIN).
  * `ALARM`: El sistema fue vulnerado y la alarma está disparada.
* **Contexto Técnico:** No solo devuelve el código de estado para el código y una etiqueta traducida en español (`stateLabel: "Espera"`), sino que además incluye los campos `lastEventId` y `lastEventType`. Esto permite al Frontend mostrarle al usuario *por qué* cambió el estado (ej: *"Alarma Disparada - Causa: Sensor de Puerta"*).

### 📊 Motor de Analíticas y Algoritmos
* **Ruta:** `GET /api/v1/analytics` (Consumido por el **Frontend**)
* **Descripción:** Endpoint estratégico de solo lectura que expone métricas derivadas de los últimos **10 minutos** fijos de datos para detectar anomalías o intentos de sabotaje.

---

## 3. Lógica de los Algoritmos Implementados (Backend)

Para cumplir con las reglas avanzadas del sistema, el backend calcula en tiempo real tres algoritmos dentro de un objeto unificado en el endpoint de analíticas:

1. **Conteo por Ventana Temporal:** Realiza sumatorias agrupadas de los eventos ocurridos estrictamente en los últimos 10 minutos (`doorOpens`, `doorStateChanges`, `pinFails`, `panicPresses`).
2. **Sospecha de Sabotaje con Histéresis (`pinFailSuspicious`):** Es una regla analítica con memoria para evitar alertas falsas o intermitentes. 
   * Se **activa** (`active: true`) si se registran **$\ge 3$ intentos fallidos de PIN** en la ventana de tiempo.
   * Se **desactiva** (`active: false`) únicamente cuando la actividad maliciosa cesa y el conteo de fallos desciende a **$\le 1$**. 
3. **Detección de Anomalías por Frecuencia (`doorOpenAnomaly`):** Marca una alerta (`active: true`) si el sensor de la puerta cambia de estado de forma frenética o sospechosa, superando un umbral estricto de **$\ge 6$ aperturas** dentro de la ventana de 10 minutos.

---

## 4. Instrucciones para Visualizar e Interactuar con el Contrato

Cualquier integrante del equipo puede previsualizar de forma interactiva el archivo `docs/openapi.yaml` mediante cualquiera de estas opciones:

* **Opción Online (Rápida):** Copiar el contenido del YAML y pegarlo en [editor.swagger.io](https://editor.swagger.io/). Se generará la documentación visual y los esquemas interactivos a la derecha de la pantalla.
* **Opción Postman (Para Pruebas):** Abrir Postman, clickear en **Import**, seleccionar el archivo `openapi.yaml`. Esto generará automáticamente una colección con todas las solicitudes estructuradas, parámetros de consulta preconfigurados y ejemplos de respuestas JSON simuladas (Mock) listos para testear el Backend cuando esté programado.
