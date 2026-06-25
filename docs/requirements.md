# Requisitos del Sistema — Proyecto IoT Alarma

Este documento especifica los requisitos funcionales (RF) y no funcionales (RNF) del sistema de alarma IoT.

---

## Requisitos Funcionales (RF)

**RF-01:** El sistema deberá permitir activar la alarma mediante el botón físico de armado.

**RF-02:** El sistema deberá permitir desactivar la alarma mediante la entrada correcta de PIN en el teclado matricial.

**RF-03:** El sistema deberá registrar eventos de apertura de puertas detectados por la ESP32.

**RF-04:** El sistema deberá registrar eventos de movimiento detectados por el sensor PIR.

**RF-05:** El sistema deberá registrar activaciones del botón de pánico.

**RF-06:** El sistema deberá mostrar el historial de eventos registrados en formato tabular.

**RF-07:** El sistema deberá mostrar el estado actual de la alarma en tiempo real.

**RF-08:** El sistema deberá ejecutar algoritmos de análisis sobre los eventos almacenados (Windowed Counts, PIN Fail Suspicious, Door Open Anomaly).

**RF-09:** El sistema deberá mostrar los resultados de los algoritmos de análisis en el dashboard de forma estructurada.

**RF-10:** La interfaz deberá actualizarse sin requerir refresco manual.

---

## Requisitos No Funcionales (RNF)

**RNF-01:** El sistema debe utilizar una base de datos relacional PostgreSQL para el almacenamiento histórico.

**RNF-02:** El frontend y la ESP32 deben comunicarse con el backend exclusivamente mediante HTTP REST.

**RNF-03:** El backend debe implementarse utilizando un único framework de desarrollo (Flask).

**RNF-04:** El backend debe validar los JSON de entrada. Si un payload es inválido, debe responder con código HTTP 4xx y abortar la persistencia en la base de datos.

**RNF-05:** Todo el código fuente, identificadores de APIs y comentarios deben estar estrictamente en inglés.

**RNF-06:** El firmware de la ESP32 debe incluir pruebas unitarias automatizadas ejecutables mediante el comando `pio test` en GitHub Actions.

**RNF-07:** La propagación de datos de dominio hacia el frontend en vivo no puede depender únicamente del estado local (useState), sino que debe canalizarse a través de las abstracciones del patrón Observer.

**RNF-08:** En caso de desconexión física de la ESP32 o caída del frontend, los datos previamente aceptados deben permanecer íntegros y accesibles en PostgreSQL para auditorías posteriores.

**RNF-09:** El backend debe implementar al menos tres algoritmos distintos sobre datos persistidos en PostgreSQL, con salidas semánticamente diferenciadas e identificables por separado.

**RNF-10:** El sistema debe evidenciar: al menos dos implementaciones concretas del patrón Observer, al menos una implementación del patrón Strategy, y al menos un tercer patrón GoF (State) con justificación por escrito.

**RNF-11:** El repositorio debe incluir GitHub Actions en `.github/workflows/` que ejecuten build + tests unitarios para backend, frontend y firmware (`pio test`) en cada Pull Request.

**RNF-12:** El repositorio debe permitir instalar hooks `pre-commit` (linter) y `pre-push` (tests), versionados o instalables desde el propio repositorio.

**RNF-13:** Antes de implementar funcionalidad sustantiva, el equipo debe versionar en `docs/` un diagrama de componentes, un diagrama de clases del backend, y uno o más diagramas de secuencia de flujos relevantes.

**RNF-14:** El equipo debe usar una única convención de mensajes de commit, documentada en `docs/`, incluyendo regla general, al menos tres ejemplos válidos, y clave Jira en cada ejemplo.
