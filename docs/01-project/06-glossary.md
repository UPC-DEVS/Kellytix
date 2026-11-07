# Kellytix

## Glosario de Términos

### 1. Propósito

Este documento establece un vocabulario estandarizado para asegurar la correcta comunicación técnica y de negocio entre todos los integrantes del proyecto y futuros colaboradores.

### 2. Términos de Negocio y Estrategia

**Value Betting (Apuesta de Valor)**
- Situación que ocurre cuando la probabilidad real de que suceda un evento (calculada por el modelo de IA) es superior a la probabilidad implícita que refleja la cuota de la casa de apuestas. Posee esperanza matemática positiva (EV+).

**Criterio de Kelly**
- Fórmula matemática de gestión de riesgo que determina el porcentaje exacto y óptimo del capital total (bankroll) que se debe invertir en una apuesta de valor para maximizar el crecimiento a largo plazo y evitar la bancarrota. En Kellytix, se restringirá a cuotas entre 1.50 y 1.80.

**Unidades**
- Medida estándar que representa un porcentaje del capital total del usuario (ej. 1 Unidad = 1% del Bankroll). Se utiliza para desvincular las decisiones de inversión del apego emocional asociado al dinero local (fiat).

**Picks Soñadores**
- Pronósticos combinados diseñados para ofrecer una recompensa financiera alta asumiendo un riesgo mayor. Se implementan como estrategia de marketing y retención de usuarios.

**Yield**
- Métrica que expresa la rentabilidad matemática o retorno de inversión (ROI) sobre el monto total apostado en el largo plazo.

### 3. Términos Técnicos y de Software

**Arquitectura de 3 Capas**
- Modelo de desarrollo estructurado en: Capa de Presentación (UI Dashboard / React), Capa de Lógica (Servidor FastAPI) y Capa de Persistencia (Base de Datos Relacional).

**API Propia**
- Sistema nativo de comunicación desarrollado internamente para evitar costos y dependencias operativas de plataformas comerciales de automatización como Make o Zapier.

**Dataset Histórico**
- Conjunto de datos en formato CSV que contiene información pasada de partidos de fútbol (resultados y cuotas) de las 5 ligas europeas más grandes, utilizado para el entrenamiento inicial del modelo.

**Pull Request (PR)**
- Solicitud formal en GitHub para fusionar el código desarrollado por un integrante a la rama principal, la cual requiere la aprobación explícita de los demás miembros del equipo.