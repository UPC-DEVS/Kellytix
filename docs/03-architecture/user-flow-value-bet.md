# Recorrido del usuario: detección de una apuesta de valor

Este diagrama describe el flujo previsto del MVP desde que el usuario solicita analizar un partido hasta que recibe una predicción. La entrada combina los datos disponibles del partido y las cuotas 1X2; el modelo estima probabilidades y el sistema las contrasta con el mercado antes de calcular una sugerencia de inversión.

El resultado es informativo: Kellytix presenta una recomendación en unidades y no ejecuta la apuesta. El diagrama representa la arquitectura propuesta, no una funcionalidad ya implementada.

```mermaid
flowchart TD
    U[Usuario abre el dashboard] --> S[Selecciona un partido para analizar]
    S --> I[Entrada: liga, fecha, equipos y cuotas 1X2]
    I --> V{¿Datos completos y válidos?}
    V -- No --> E[Mostrar aviso y pedir corregir o completar los datos]
    E --> S
    V -- Sí --> R{¿Cuota seleccionada entre 1.50 y 1.80?}
    R -- No --> N[Informar que la cuota está fuera del rango operativo]
    R -- Sí --> P[Preparar variables disponibles antes del partido]
    P --> M[Enviar variables al modelo predictivo]
    M --> C{¿Modelo disponible y predicción válida?}
    C -- No --> F[Informar que no se pudo generar la predicción]
    C -- Sí --> PR[Obtener probabilidades estimadas para local, empate y visitante]
    PR --> O[Calcular valor esperado EV = probabilidad estimada × cuota − 1]
    O --> D{¿EV es positivo?}
    D -- No --> NV[Mostrar predicción y cuotas; indicar que no hay apuesta de valor]
    D -- Sí --> K[Calcular porcentaje de Kelly para el resultado con valor]
    K --> U1[Convertir el porcentaje sugerido a unidades según el bankroll configurado]
    U1 --> OUT[Mostrar resultado, probabilidad, cuota, EV y sugerencia en unidades]
    NV --> END[Usuario revisa el análisis]
    OUT --> END
    N --> END
    F --> END
```

## Datos de entrada y resultado

- **Entrada:** partido, liga, fecha, equipos y cuotas del mercado 1X2; se usan variables históricas disponibles antes del partido para evitar incorporar información posterior al resultado.
- **Evaluación:** el modelo estima la probabilidad de cada resultado. El motor compara esa probabilidad con la cuota seleccionada para calcular el valor esperado; para los casos con EV positivo, calcula el porcentaje Kelly.
- **Salida:** predicción, cuota evaluada, valor esperado e inversión sugerida en unidades. Si los datos no son válidos, la cuota queda fuera del rango operativo, falla el modelo o no hay EV positivo, se informa el motivo o la ausencia de una oportunidad.

El rango de cuotas de 1.50 a 1.80 y el uso de unidades siguen los objetivos y requisitos documentados del proyecto.
