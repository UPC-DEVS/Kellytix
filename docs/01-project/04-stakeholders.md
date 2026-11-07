# Kellytix

## Interesados (Stakeholders)

### 1. Presentación

El desarrollo y despliegue del sistema Kellytix involucra a distintos grupos de interés que interactúan de forma directa o indirecta con la plataforma. Comprender sus necesidades es fundamental para alinear los objetivos del negocio con la arquitectura del software.

### 2. Grupos de Interesados Internos

**Equipo de Desarrollo (Core Team)**
- Conformado por Daniel, Santiago, Carlos y Diego.
- Responsables de la construcción técnica de las 3 capas del sistema (Frontend, Backend/API, Persistencia de Datos).
- Interesados en mantener un código limpio, auditable y libre de dependencias costosas (cero automatizaciones externas).

**Product Owner / Dirección de Negocio**
- Encargados de definir la visión comercial y la estrategia matemática.
- Interesados en asegurar que el algoritmo respete el enfoque en cuotas de 1.50 a 1.80 y en garantizar que la interfaz eduque al usuario sobre el uso de "Unidades" en lugar de dinero local.

### 3. Grupos de Interesados Externos

**Usuarios Finales (Inversores / Apostadores)**
- Personas que utilizarán la plataforma (Dashboard en React) para consultar pronósticos.
- Perfil dual: Inversores a largo plazo atraídos por la rentabilidad algorítmica (Yield), y apostadores recreacionales atraídos por el módulo de "Picks Soñadores".
- Necesitan una interfaz clara, estable y 100% visual.

**Proveedores de Datos Deportivos**
- En la fase inicial: Repositorios o proveedores del dataset histórico CSV de las 5 grandes ligas europeas.
- En fases posteriores: Servicios de API que proporcionarán resultados en vivo y variaciones de cuotas de mercado. Su impacto técnico será mitigado mediante el desarrollo de la API propia de integración.