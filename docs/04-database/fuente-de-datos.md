# Fuente de datos del proyecto Kellytix

Documento de la tarea 0.8 (selección de fuente de datos). Describe de dónde salen los datos, cómo se unieron, qué contienen, qué se verificó y qué limitaciones tienen.

## 1. Decisión

El equipo usa datos históricos en CSV en lugar de una API deportiva. Motivos:

- Las APIs gratuitas limitan las peticiones diarias y las temporadas disponibles, lo que no alcanza para reunir miles de partidos con estadísticas y cuotas.
- El requisito RF-01 pide no depender de APIs externas de pago.
- Las cuotas históricas son indispensables para calcular el Valor Esperado (EV), el backtesting y el Criterio de Kelly.

## 2. Fuentes

| Fuente | Qué aporta | Cómo se obtuvo |
|---|---|---|
| Club Football Match Data 2000-2025 (Gábor, A., 2025). Repositorio: github.com/xgabora/Club-Football-Match-Data-2000-2025 | Resultados, Elo, forma y estadísticas de partido (`Matches.csv`) | El archivo se tomó de la copia del repositorio szabilukacs/Football-project, cuyo README indica que sus datos provienen de este dataset |
| football-data.co.uk | Cuotas de casas de apuestas por partido | Descarga manual de los zips por temporada (`data.zip`), de 2018/19 a 2025/26 |

## 3. Contenido de `Matches.csv`

- 230.554 partidos entre el 28/07/2000 y el 01/06/2025, de 38 divisiones.
- 28 columnas: división, fecha, equipos, Elo local y visitante, forma de los últimos 3 y 5 partidos, goles al final y al medio tiempo, resultado, tiros, tiros a puerta, faltas, córneres, tarjetas amarillas y rojas.
- Resultado final: 44,6% local, 26,5% empate, 28,9% visitante.
- Vacíos en el total: cerca de la mitad de las filas no tiene tiros, córneres ni tarjetas; el Elo falta en el 38,6% y el medio tiempo en el 23,7%.
- No incluye cuotas, árbitro ni partidos posteriores a junio de 2025.

## 4. Subconjunto de trabajo

Se filtraron las cinco grandes ligas (E0 Premier League, SP1 La Liga, I1 Serie A, D1 Bundesliga, F1 Ligue 1) desde el 01/07/2018. En ese tramo, Elo, forma, tiros, córneres y tarjetas están completos.

| División | Partidos |
|---|---|
| E0 | 2.660 |
| SP1 | 2.660 |
| I1 | 2.660 |
| F1 | 2.410 |
| D1 | 2.142 |
| **Total** | **12.532** |

## 5. Unión con las cuotas

- Clave de unión: división, fecha y equipos local y visitante, con los nombres normalizados (minúsculas y sin símbolos).
- Sin normalizar, la unión daba 96,5% en E0 y 89,8% en D1. La diferencia venía de dos nombres escritos distinto en cada fuente: MGladbach y Nottm Forest.
- Con los nombres normalizados: 12.532 de 12.532 partidos con cuotas (100% en las cinco ligas), sin duplicados y sin filas sin cruzar.
- Archivo resultante: `data/processed/matches_con_cuotas.csv`, con 37 columnas: las 28 de `Matches.csv` más 9 de cuotas.

Columnas de cuotas incluidas:

| Columnas | Significado |
|---|---|
| `B365H`, `B365D`, `B365A` | Bet365: local, empate y visitante (cuotas previas al cierre) |
| `PSH`, `PSD`, `PSA` | Pinnacle: local, empate y visitante (cuotas previas al cierre) |
| `PSCH`, `PSCD`, `PSCA` | Pinnacle al cierre del mercado |

Según la nota de football-data.co.uk, desde 2019/20 se recogen dos juegos de cuotas (tras la apertura del mercado y al cierre), y en temporadas anteriores solo hay cuotas previas al cierre. Para simular apuestas se usan las cuotas previas al cierre; las de cierre de Pinnacle sirven como referencia exigente del mercado.

## 6. Verificación

| Prueba | Resultado |
|---|---|
| Filas y rango de fechas | 12.532 filas, del 10/08/2018 al 25/05/2025 |
| Rango de cuotas | De 1,03 a 51, sin ceros ni valores imposibles |
| Margen medio de la casa | 5,32% en Bet365; 2,69% en Pinnacle al cierre |
| Yield apostando siempre al local (Bet365) | −7,8% |

El margen de Pinnacle al cierre (2,69%) es el costo mínimo que un modelo debe superar. Un modelo igual al mercado perdería esa cantidad.

## 7. Limitaciones

- Solo se incluyen cuotas del mercado 1X2. Los archivos de football-data.co.uk traen otros mercados (más/menos de 2,5 goles, hándicap asiático), que no se incluyeron.
- No hay cuotas de córneres ni de tarjetas, por lo que el nicho (RF-06) se puede explorar con estadísticas, pero no evaluar con EV.
- No hay datos de árbitro.
- Los datos llegan hasta mayo de 2025. Los zips de 2025/26 se descargaron, pero no tienen Elo ni forma.
- Elo y forma los calculó el autor del dataset y su método no está verificado. Pendiente: confirmar que no incluyen el resultado del propio partido (fuga de datos).
- Los goles finales, tiros, córneres, faltas y tarjetas de un partido solo se conocen después de jugarlo. No se pueden usar como variables para predecirlo; solo como resultado o para calcular promedios de partidos anteriores.

## 8. Licencia y uso

- football-data.co.uk indica que sus datos son gratuitos y que su uso está pensado para particulares, no para productos comerciales ni de entrenamiento de datos con bots, scrapers o IA. Por eso los archivos se descargan a mano. Pendiente: escribir al autor para confirmar que el uso en este proyecto de formación es aceptable y guardar su respuesta en `docs`.
- El autor del dataset de Gábor lo presenta como utilizable para entrenar modelos de aprendizaje automático. Pendiente: revisar la licencia del repositorio original.
- Los CSV de datos no se suben al repositorio público: `data/raw/` y `data/processed/` están en el `.gitignore`.
- Al citar los datos, indicar ambas fuentes.

## 9. Cómo reproducir el dataset

1. Descargar `Matches.csv` y guardarlo en `data/raw/`.
2. Descargar a mano los zips de football-data.co.uk (`mmz4281/AAAA/data.zip`) de 2018/19 a 2025/26 y descomprimirlos en `data/raw/odds/<temporada>/` (por ejemplo `data/raw/odds/2324/`).
3. Con el entorno virtual activo, ejecutar `python scripts/crear_dataset.py`.
4. Comprobar el resultado con `python scripts/verificar_dataset.py`.