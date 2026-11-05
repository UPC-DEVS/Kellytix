# Kellytix

## Descripción general del proyecto

### 1. Presentación

Kellytix es un sistema algorítmico de software propuesto para la identificación de apuestas de valor (Value Betting) y la gestión de riesgo financiero basado en Machine Learning. Su propósito es centralizar el análisis de datos deportivos y automatizar el cálculo de inversiones utilizando el Criterio de Kelly.

La solución busca desvincular el componente emocional de las apuestas deportivas, facilitando a los usuarios una visión matemática y organizada de su rentabilidad a largo plazo.

### 2. Módulos contemplados

**Procesamiento de datos e IA**
- Ingestar y limpiar datasets históricos en formato CSV de las 5 grandes ligas europeas.
- Entrenar modelos de Machine Learning para predecir probabilidades reales.
- Calcular el Valor Esperado (EV+) cruzando predicciones con cuotas de mercado.

**Gestión de riesgo (Criterio de Kelly)**
- Filtrar oportunidades enfocándose en cuotas intermedias (1.50 - 1.80).
- Calcular el porcentaje exacto del bankroll a invertir según la ventaja matemática.
- Convertir la moneda local a "Unidades" para estandarizar el rendimiento.

**Retención y enganche comercial**
- Generar combinadas de mayor riesgo y recompensa ("Picks Soñadores").
- Mostrar gráficos interactivos de la curva de rentabilidad (Yield).

### 3. Integración esperada

El sistema operará bajo una arquitectura estricta de 3 capas. El Backend (FastAPI) y la Base de Datos (SQLite) alimentarán directamente la capa de Presentación (Frontend en React), garantizando una experiencia 100% gráfica sin uso de terminales para el usuario final.

### 4. Beneficios esperados

- Independencia tecnológica al usar una API propia en lugar de servicios de terceros (Make/Zapier).
- Educación financiera del usuario al operar en "Unidades" y no en pesos.
- Reducción drástica de pérdidas por decisiones emocionales.
- Crecimiento sostenido del capital mediante rentabilidad comprobada (Yield).

### 5. Metodología de trabajo

El equipo desarrollará el proyecto utilizando Scrum adaptado. Se contemplan Sprints de 1 a 2 semanas, auditorías de código obligatorias por cada módulo cerrado y reglas estrictas de control de versiones.

### 6. Equipo

- Daniel (Backend / DB)
- Santiago (IA / Datos)
- Carlos (Frontend UI / QA)
- Diego (API Propia / Integración)

### 7. Estado y alcance

Este documento describe la propuesta general del producto en su Fase 00. La inclusión de un módulo en esta descripción define su arquitectura inicial basada en históricos CSV, pero no significa que su automatización en tiempo real ya esté implementada.