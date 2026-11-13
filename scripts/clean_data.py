import re
from pathlib import Path

import numpy as np
import pandas as pd

ENTRADA = Path("data/processed/matches_con_cuotas.csv")
SALIDA = Path("data/processed/clean_data.csv")

# Equipos que aparecen escritos de dos formas distintas en el dataset.
CANONICOS = {"MGladbach": "M'gladbach", "Nottm Forest": "Nott'm Forest"}
CUOTAS = ["B365H", "B365D", "B365A", "PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA"]


def clave(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


d = pd.read_csv(ENTRADA, low_memory=False)
filas_iniciales = len(d)
informe = {}

# 1. Fechas en un solo formato
d["match_date"] = pd.to_datetime(d["match_date"], errors="coerce")
informe["Fechas ilegibles (filas eliminadas)"] = int(d.match_date.isna().sum())
d = d.dropna(subset=["match_date"])

# 2. Nombres de equipos canónicos
informe["Nombres de equipo unificados"] = int(
    d.home_team.isin(CANONICOS).sum() + d.away_team.isin(CANONICOS).sum()
)
for col in ["home_team", "away_team"]:
    d[col] = d[col].replace(CANONICOS)
nombres = pd.concat([d.home_team, d.away_team]).drop_duplicates()
por_clave = nombres.groupby(nombres.map(clave)).size()
repetidos = por_clave[por_clave > 1]
assert repetidos.empty, f"Equipos con más de un nombre: {list(repetidos.index)}"

# 3. Duplicados (misma fecha, local y visitante)
llave = ["match_date", "home_team", "away_team"]
informe["Duplicados (filas eliminadas)"] = int(d.duplicated(llave).sum())
d = d.drop_duplicates(llave)

# 4. Cuotas válidas: sin vacíos, mayores que 1 y con probabilidad implícita razonable
mal = d[CUOTAS].isna().any(axis=1) | (d[CUOTAS] <= 1).any(axis=1)
d = d[~mal]
informe["Cuotas vacías o <= 1 (filas eliminadas)"] = int(mal.sum())
mal = pd.Series(False, index=d.index)
for casa in ["B365", "PS", "PSC"]:
    suma = 1 / d[f"{casa}H"] + 1 / d[f"{casa}D"] + 1 / d[f"{casa}A"]
    mal |= (suma < 0.99) | (suma > 1.25)
informe["Probabilidad implícita fuera de rango (filas eliminadas)"] = int(mal.sum())
d = d[~mal]

# 5. Coherencia de resultados y estadísticas
res = np.select(
    [d.ft_home_goals > d.ft_away_goals, d.ft_home_goals < d.ft_away_goals],
    ["H", "A"],
    default="D",
)
mal = res != d.ft_result
informe["Resultado incoherente con los goles (filas eliminadas)"] = int(mal.sum())
d = d[~mal]

mal = (d.ht_home_goals > d.ft_home_goals) | (d.ht_away_goals > d.ft_away_goals)
informe["Goles al descanso mayores que al final (filas eliminadas)"] = int(mal.sum())
d = d[~mal]

corregidos = 0
for lado in ["home", "away"]:
    mal = d[f"{lado}_target"] > d[f"{lado}_shots"]
    corregidos += int(mal.sum())
    d.loc[mal, f"{lado}_shots"] = d.loc[mal, f"{lado}_target"]
informe["Tiros a puerta > tiros (corregidos)"] = corregidos

# 6. Elo vacío: se rellena con el último Elo conocido del mismo equipo
d = d.sort_values(["match_date", "division_name", "home_team"]).reset_index(drop=True)
largo = pd.concat([
    pd.DataFrame({"i": d.index, "lado": "home", "equipo": d.home_team,
                  "fecha": d.match_date, "elo": d.home_elo}),
    pd.DataFrame({"i": d.index, "lado": "away", "equipo": d.away_team,
                  "fecha": d.match_date, "elo": d.away_elo}),
]).sort_values(["equipo", "fecha", "i"])
informe["Elo vacíos (valores)"] = int(largo.elo.isna().sum())
largo["elo"] = largo.groupby("equipo")["elo"].ffill()
d["home_elo"] = largo[largo.lado == "home"].set_index("i")["elo"]
d["away_elo"] = largo[largo.lado == "away"].set_index("i")["elo"]
sin_elo = d.home_elo.isna() | d.away_elo.isna()
informe["Elo sin valor previo (filas eliminadas)"] = int(sin_elo.sum())
d = d[~sin_elo].reset_index(drop=True)

# 7. Informe y guardado
print("INFORME DE CALIDAD")
for texto, valor in informe.items():
    print(f"- {texto}: {valor}")
print(f"\nFilas: {filas_iniciales} -> {len(d)}")
print("Equipos distintos:", pd.concat([d.home_team, d.away_team]).nunique())
d.to_csv(SALIDA, index=False)
print("Guardado en", SALIDA)