# Kellytix

## Roles y Estructura del Equipo

### 1. Presentación de la Metodología

El equipo desarrollará el proyecto utilizando un enfoque híbrido Scrum/Kanban. Para garantizar un aprendizaje integral y evitar la sobreescritura de código, las responsabilidades estarán divididas por capas arquitectónicas, pero se requerirá aprobación cruzada para integrar avances.

### 2. Roles y Responsabilidades

**Daniel (Scrum Master / Backend)**
- Liderar las ceremonias (Planificación los sábados, Dailys extendidos los miércoles).
- Diseñar la base de datos relacional (SQLite) y mapearla con SQLAlchemy.
- Programar la lógica central del servidor en FastAPI.
- Dirigir las sesiones de auditoría técnica al cerrar módulos importantes.

**Santiago (Product Owner / IA & Datos)**
- Definir la estrategia comercial y el enfoque en "Unidades".
- Entrenar el modelo de Machine Learning y validar el Yield en backtesting.
- Procesar y limpiar el dataset histórico CSV de las 5 ligas.
- Ajustar matemáticamente la fórmula del Criterio de Kelly (enfocado en cuotas 1.50 - 1.80).

**Carlos (QA / Frontend UI)**
- Liderar el diseño e implementación de la Interfaz Gráfica (React).
- Garantizar que el usuario final interactúe con dashboards visuales y jamás mediante terminales.
- Realizar pruebas de interfaz y diseño, graficando las curvas de rentabilidad.

**Diego (Integración / API Propia)**
- Liderar el desarrollo de la API interna para eliminar la dependencia de terceros (Make/Zapier).
- Crear scripts nativos de Python para ingestar los datos a la base local.
- Estructurar el módulo secundario de los "Picks Soñadores".
- Ejecutar pruebas integrales End-to-End (E2E).

### 3. Reglas de Colaboración (GitHub)

- **Aislamiento de Ramas:** Cero push directo a la rama `main`. Cada desarrollador trabajará en ramas de funcionalidades locales (`feature/tarea`).
- **Code Review Estricto:** Toda solicitud de integración (Pull Request) hacia `main` requerirá obligatoriamente la revisión técnica y aprobación de los otros 3 miembros del equipo en la plataforma.