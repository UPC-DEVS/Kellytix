gin i

# Guía para crear e iniciar la base de datos

Esta guía explica cómo preparar el entorno, generar el dataset procesado,
crear la base de datos SQLite e insertar los partidos históricos del proyecto
Kellytix desde cero.

## Requisitos

- Git.
- Python compatible con el proyecto.
- El repositorio actualizado.
- Los archivos de datos descargados manualmente.

La base de datos local se guarda en `kellytix.db`. Este archivo está ignorado
por Git y no debe subirse al repositorio.

## 1. Actualizar el repositorio

Desde la raíz del proyecto:

```bash
git pull origin <nombre-de-la-rama>
```

## 2. Activar el entorno virtual

### Linux o macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Si el entorno virtual todavía no existe, créalo con:

```bash
python -m venv .venv
```

## 3. Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

Las dependencias principales para esta guía son `pandas` y `SQLAlchemy`.

## 4. Preparar los datos de entrada

Descarga manualmente `Matches.csv` y guárdalo en:

```text
data/raw/Matches.csv
```

Descarga también los archivos de cuotas de football-data.co.uk de las
temporadas requeridas y descomprímelos siguiendo esta estructura:

```text
data/raw/odds/<temporada>/<liga>.csv
```

Ejemplo:

```text
data/raw/odds/2324/E0.csv
data/raw/odds/2324/SP1.csv
```

El dataset utilizado por Kellytix combina:

- Resultados, equipos, Elo, forma y estadísticas de `Matches.csv`.
- Cuotas 1X2 de Bet365 y Pinnacle.
- Las ligas `E0`, `SP1`, `I1`, `D1` y `F1`.
- Partidos desde julio de 2018.

## 5. Crear el dataset con cuotas

Ejecuta:

```bash
python scripts/crear_dataset.py
```

Este script cruza los partidos con las cuotas y genera:

```text
data/processed/matches_con_cuotas.csv
```

## 6. Limpiar y validar el dataset

Ejecuta el proceso de limpieza:

```bash
python scripts/clean_data.py
```

El resultado se guarda en:

```text
data/processed/clean_data.csv
```

Después puedes comprobar el dataset unido con:

```bash
python scripts/verificar_dataset.py
```

La limpieza elimina o corrige datos inválidos, unifica nombres de equipos,
valida cuotas y resultados, y completa Elo usando el último valor conocido
del equipo cuando es posible.

Luego genera las variables derivadas sin usar resultados futuros:

```bash
python scripts/build_features.py
```

Este proceso crea `data/processed/features.csv` con puntos de los últimos cinco
partidos, goles a favor y en contra y días de descanso, tanto para el equipo
local como para el visitante.

## 7. Crear la base de datos SQLite

Inicializa las tablas ejecutando:

```bash
python database/connection.py
```

Esto crea `kellytix.db` en la raíz del proyecto con las tablas definidas en
`database/models.py`, incluyendo:

- `usuarios`
- `partidos_historico`
- `modelos_predictivos`
- `predicciones_log`
- `apuestas_usuario`

## 8. Cargar los partidos históricos

Carga el dataset limpio en `partidos_historico`:

```bash
python scripts/load_db.py
```

El script:

- Lee `data/processed/clean_data.csv`.
- Valida las columnas obligatorias.
- Convierte fechas y valores numéricos.
- Inserta los datos por lotes usando SQLAlchemy.
- Evita duplicados en ejecuciones repetidas.
- Carga la hora si está disponible en el CSV.

Si necesitas reconstruir completamente la tabla de partidos:

```bash
python scripts/load_db.py --replace
```

`--replace` elimina únicamente los registros de `partidos_historico`; no
modifica las tablas de usuarios, modelos, predicciones ni apuestas. Ten en
cuenta que al volver a insertar se generan nuevos `id_partido`; por tanto,
puede romper las referencias de predicciones ya guardadas. Úsalo solo antes
de crear predicciones o cuando también puedas reconstruirlas.

También puedes especificar rutas o el tamaño del lote:

```bash
python scripts/load_db.py \
  --csv data/processed/clean_data.csv \
  --database kellytix.db \
  --batch-size 1000
```

## 9. Verificación final

Comprueba que el archivo existe:

```bash
ls -lh kellytix.db
```

Para comprobar la cantidad de partidos cargados:

```bash
sqlite3 kellytix.db \
  "SELECT COUNT(*) FROM partidos_historico;"
```

Para consultar un resumen:

```bash
sqlite3 kellytix.db \
  "SELECT liga, COUNT(*) FROM partidos_historico GROUP BY liga ORDER BY liga;"
```

## Reiniciar todo desde cero

Si necesitas una base completamente nueva, elimina únicamente el archivo
local de SQLite y repite los pasos de inicialización y carga:

```bash
rm kellytix.db
python database/connection.py
python scripts/load_db.py
```

En Windows:

```powershell
Remove-Item kellytix.db
python database/connection.py
python scripts/load_db.py
```

No elimines las carpetas del repositorio ni los archivos fuente. Los CSV de
`data/raw/` y `data/processed/` también están ignorados por Git y deben
conservarse localmente si se quiere repetir el proceso de generación.

## Orden resumido

```text
1. Activar .venv
2. Instalar requirements.txt
3. Colocar Matches.csv y las cuotas en data/raw/
4. Ejecutar scripts/crear_dataset.py
5. Ejecutar scripts/clean_data.py
6. Ejecutar scripts/verificar_dataset.py
7. Ejecutar database/connection.py
8. Ejecutar scripts/build_features.py
9. Ejecutar scripts/load_db.py
```

## Variables derivadas para el modelo

La racha, los promedios históricos de goles y los días de descanso no se
guardan como columnas del partido histórico. Deben calcularse en la etapa de
ingeniería de variables, usando únicamente partidos anteriores a la fecha de
cada partido para evitar fuga de información. En consecuencia:

- `partidos_historico` conserva los datos observados del partido y sus cuotas.
- El pipeline de features debe generar esas variables para entrenamiento y
  predicción.
- Si se requiere persistirlas para auditoría, debe crearse una tabla o dataset
  versionado de features, relacionado con `id_partido`, sin mezclarlas con el
  resultado posterior del partido.

Para reproducir el dataset, consulta también:

- `database/gu_a_de_inicializaci_n_de_base_de_datos_local.md`
- `docs/04-database/fuente-de-datos.md`
