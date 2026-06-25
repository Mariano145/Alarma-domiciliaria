# Git Workflow

Este documento define el flujo de trabajo con ramas que el equipo utiliza para desarrollar el proyecto IoT.

## 1. Estructura de Ramas

El proyecto sigue un modelo **Gitflow** con tres tipos de ramas:

### 1.1 `master` (Rama de Producción)
- **Propósito:** Contiene el código estable y funcional listo para entrega/evaluación.
- **Protección:** Solo se actualiza mediante Pull Requests (PR) aprobados desde `develop`.
- **Regla:** Nunca se commitea directamente en `master`.

### 1.2 `develop` (Rama de Integración)
- **Propósito:** Rama de integración continua donde se fusionan todas las features terminadas.
- **Uso:** El equipo mergea sus features aquí. Es el punto de prueba antes de pasar a `main`.
- **Regla:** Se actualiza solo mediante PRs desde ramas `feature/*`.

### 1.3 `feature/*` (Ramas de Desarrollo)
- **Propósito:** Cada historia de usuario se desarrolla en su propia rama.
- **Origen:** Se crean desde `develop`.
- **Destino:** Se mergean de vuelta a `develop` mediante PR.

---

## 2. Nomenclatura de Ramas

Toda rama de trabajo debe seguir este formato:

```
feature/IOT-XX-descripcion-corta
```

Donde:
- `IOT-XX` = clave de la historia de usuario en Jira
- `descripcion-corta` = breve descripción en minúsculas y guiones

### Ejemplos válidos:

```
feature/IOT-21-ingesta-eventos
feature/IOT-25-persistencia-postgresql
feature/IOT-29-maquina-estados
feature/IOT-33-frontend-dashboard
feature/IOT-41-firmware-sensores
feature/IOT-45-algoritmos-analytics
```

---

## 3. Flujo de Trabajo Paso a Paso

### Paso 1: Crear rama desde develop

```bash
# Asegurarse de estar en develop y actualizado
git checkout develop
git pull origin develop

# Crear nueva rama para la historia
git checkout -b feature/IOT-21-ingesta-eventos
```

### Paso 2: Desarrollar y commitear

- Trabajar en la rama `feature/*`
- Hacer commits frecuentes
- Seguir la **convención de commits** definida en `docs/commits-convention.md`

### Paso 3: Actualizar con develop antes del PR

```bash
# Traer cambios de otros compañeros que ya mergearon
git checkout develop
git pull origin develop
git checkout feature/IOT-21-ingesta-eventos
git merge develop
# Resolver conflictos si los hay
```

### Paso 4: Crear Pull Request

- Push de la rama al remoto
- Crear PR en GitHub hacia `develop`
- **Título del PR:** debe incluir la clave Jira (ej: `IOT-21: Implementa ingesta de eventos de sensores`)
- **Descripción:** mencionar qué se implementó, qué archivos se tocaron

### Paso 5: Revisión y Aprobación

- **Mínimo 2 aprobaciones** de personas distintas del equipo (configurado en GitHub)
- Revisar código, tests, linter, y que cumpla con el contrato OpenAPI

### Paso 6: Merge

- Una vez aprobado, se hace merge a `develop`
- Se elimina la rama `feature/*` después del merge

### Paso 7: Pasar a main (cuando todo esté integrado)

- Cuando un conjunto de features está estable en `develop`
- Se crea PR de `develop` → `main`
- Requiere las mismas aprobaciones

---

## 4. Criterio de Merge

Para que un PR pueda mergearse a `develop` o `main`:

1. **Aprobaciones:** Mínimo 2 aprobaciones (o 1 si el equipo tiene 2 integrantes)
2. **Tests:** Todos los tests unitarios deben pasar (backend, frontend, firmware)
3. **Linter:** El código debe pasar el linter (`pre-commit`)
4. **CI/CD:** GitHub Actions debe reportar checks exitosos (build + tests)
5. **Jira:** El PR debe referenciar la clave de historia de usuario

## 6. Relación entre Ramas y Jira

| Elemento | Vinculación con Jira |
|----------|---------------------|
| **Rama** | `feature/IOT-XX` → historia IOT-XX en Jira |
| **Commit** | `feat(backend): IOT-XX implementa...` → clave IOT-XX |
| **PR** | Título: `IOT-XX: descripción de la feature` |
| **Merge** | Al mergear, Jira puede detectar el PR y actualizar la historia |

---

## 7. Resumen Visual

```
        ┌─────────────────────────────────────────────────────────┐
        │                    main (protegida)                     │
        │              Código estable, evaluación                 │
        └─────────────────────────────────────────────────────────┘
                              ↑  PR con 2 aprobaciones
                              │  + tests pasando
                              │
        ┌─────────────────────────────────────────────────────────┐
        │                  develop (protegida)                    │
        │           Integración de todas las features             │
        └─────────────────────────────────────────────────────────┘
           ↑                    ↑                    ↑
           │ PR 2 aprobaciones  │ PR 2 aprobaciones  │ PR 2 aprobaciones
           │                    │                    │
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ feature/IOT- │    │ feature/IOT- │    │ feature/IOT- │
    │    21        │    │    25        │    │    29        │
    └──────────────┘    └──────────────┘    └──────────────┘
```

## 9. Notas para el Equipo

- **Nunca** commitear directo en `main` o `develop`
- **Siempre** crear rama `feature/*` desde `develop` actualizada
- **Siempre** incluir la clave Jira en commits y PRs
- **Revisar** PRs de otros antes de aprobar: código, tests, linter, documentación
- **Actualizar** Jira cuando se termine una subtarea (mover a "Finalizada")
