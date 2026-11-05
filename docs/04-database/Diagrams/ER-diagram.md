# Diagrama Relacional de la Base de Datos (Kellytix)

Este diagrama representa la estructura de la base de datos local SQLite utilizando SQLAlchemy, alineada a los requerimientos de la Fase 00 (MVP).

# Diagrama Relacional de la Base de Datos (Kellytix)

```mermaid
erDiagram
    usuarios {
        INTEGER id_usuario PK
        VARCHAR nombre_usuario
        VARCHAR email UK
        VARCHAR password_hash
        DECIMAL bankroll_fiat
        DECIMAL bankroll_unidades
        DATETIME fecha_registro
    }

    partidos_historico {
        INTEGER id_partido PK
        DATE fecha
        VARCHAR liga
        VARCHAR equipo_local
        VARCHAR equipo_visitante
        INTEGER goles_local
        INTEGER goles_visitante
        DECIMAL cuota_local
        DECIMAL cuota_empate
        DECIMAL cuota_visitante
    }

    modelos_predictivos {
        INTEGER id_modelo PK
        VARCHAR archivo_pkl
        VARCHAR algoritmo_base
        DECIMAL accuracy_test
        DECIMAL yield_esperado
        DATETIME fecha_entrenamiento
        BOOLEAN en_produccion
    }

    predicciones_log {
        INTEGER id_prediccion PK
        INTEGER id_partido FK
        INTEGER id_modelo FK
        DECIMAL probabilidad_ia
        DECIMAL cuota_mercado
        DECIMAL valor_esperado
        DECIMAL porcentaje_kelly
        DECIMAL inversion_unidades
        VARCHAR tipo_pick
        VARCHAR resultado
    }

    apuestas_usuario {
        INTEGER id_apuesta PK
        INTEGER id_usuario FK
        INTEGER id_prediccion FK
        DECIMAL unidades_invertidas
        DECIMAL cuota_tomada
        VARCHAR estado
        DATETIME fecha_apuesta
    }

    partidos_historico ||--o{ predicciones_log : "registra"
    modelos_predictivos ||--o{ predicciones_log : "calcula"
    usuarios ||--o{ apuestas_usuario : "realiza"
    predicciones_log ||--o{ apuestas_usuario : "tiene"
```
