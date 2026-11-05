# Kellytix

## Objetivos del Proyecto

### 1. Propósito Principal

Desarrollar un sistema de software integral, estructurado en 3 capas, capaz de identificar apuestas de valor en el fútbol europeo y emitir recomendaciones de inversión matemáticamente rentables, centralizando la gestión de los datos a través de una API propietaria.

### 2. Objetivos Específicos

**Independencia de Datos y Arquitectura**
- Construir una API nativa en Python para el procesamiento y consulta de datos.
- Eliminar de forma absoluta la dependencia y los costos asociados a herramientas de automatización de terceros (Make/Zapier).
- Implementar una base de datos relacional robusta (SQLite/SQLAlchemy) descartando el uso de hojas de cálculo (Excel).

**Optimización Algorítmica (Criterio de Kelly)**
- Automatizar el cálculo matemático para determinar el tamaño exacto de la inversión.
- Limitar el modelo operativo principal a cuotas intermedias (1.50 - 1.80) para garantizar un equilibrio óptimo entre la tasa de acierto y el riesgo asumido.

**Educación Financiera y Experiencia de Usuario**
- Cambiar la narrativa financiera del sistema: migrar del uso de "moneda fiat" (ej. pesos colombianos) al concepto estandarizado de "Unidades".
- Enseñar al usuario final a enfocar su atención en la rentabilidad matemática a largo plazo (Yield) y no en las ganancias rápidas.
- Proveer una interfaz gráfica (UI Dashboard en React) completamente visual, prohibiendo la interacción del usuario mediante terminales de comandos.

**Retención Comercial**
- Desarrollar e implementar una sección secundaria de "Picks Soñadores".
- Identificar y sugerir combinadas de mayor riesgo y alta recompensa como mecanismo para captar y retener a los usuarios que buscan mayores emociones con menor inversión.

### 3. Metas de la Fase Inicial (MVP)

Alcanzar la validación del modelo de Machine Learning utilizando exclusivamente un dataset histórico preexistente en formato `.csv` (enfocado en las 5 grandes ligas), logrando simular un backtesting con rentabilidad positiva antes de conectar servicios en vivo.