import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

HISTORIAL = Path("data/raw/matches.csv")
LIMPIO = Path("data/processed/clean-data.csv")
SALIDA = Path("data/processed/features.csv")

VENTANA = 5          # partidos previos que se miran
TOPE_DESCANSO = 30   # un descanso mayor a 30 dias se trata como 30 (parón de verano)
NUEVAS = ["puntos_ult5", "goles_favor_ult5", "goles_contra_ult5", "dias_descanso"]
RENOMBRES = {
    "MatchDate": "match_date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHome": "ft_home_goals",
    "FTAway": "ft_away_goals",
    "FTResult": "ft_result",
}


def clave(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


inicio = time.time()

# 1. Historial: matches.csv (desde el año 2000) + partidos nuevos del dataset limpio
necesarias = ["match_date", "home_team", "away_team", "ft_home_goals", "ft_away_goals", "ft_result"]
h = pd.read_csv(HISTORIAL, low_memory=False)
h.columns = h.columns.str.replace("\ufeff", "", regex=False).str.strip()
h = h.rename(columns=RENOMBRES)
d = pd.read_csv(LIMPIO, low_memory=False)
for nombre, tabla in ((HISTORIAL, h), (LIMPIO, d)):
    faltan = [c for c in necesarias if c not in tabla.columns]
    assert not faltan, f"Faltan columnas en {nombre}: {faltan}"
h = pd.concat([h[necesarias], d[necesarias]], ignore_index=True).dropna()
h["match_date"] = pd.to_datetime(h["match_date"])
h["k_local"] = h.home_team.map(clave)
h["k_visit"] = h.away_team.map(clave)
h = h.drop_duplicates(["match_date", "k_local", "k_visit"])  # si se repite, vale matches.csv
h = h.sort_values(["match_date", "k_local"]).reset_index(drop=True)
h["id"] = h.index

# 2. Formato largo: una fila por equipo y partido
pts_local = np.select([h.ft_result == "H", h.ft_result == "D"], [3, 1], default=0)
pts_visit = np.select([h.ft_result == "A", h.ft_result == "D"], [3, 1], default=0)
largo = pd.concat([
    pd.DataFrame({"id": h.id, "lado": "local", "equipo": h.k_local, "fecha": h.match_date,
                    "gf": h.ft_home_goals, "gc": h.ft_away_goals, "pts": pts_local}),
    pd.DataFrame({"id": h.id, "lado": "visitante", "equipo": h.k_visit, "fecha": h.match_date,
                    "gf": h.ft_away_goals, "gc": h.ft_home_goals, "pts": pts_visit}),
]).sort_values(["equipo", "fecha", "id"]).reset_index(drop=True)

# 3. Variables: solo con partidos ANTERIORES (shift(1) deja fuera el partido actual)
g = largo.groupby("equipo")


def previos(col):
    desplazada = g[col].shift(1)
    return desplazada.groupby(largo["equipo"]).rolling(VENTANA, min_periods=VENTANA)


largo["puntos_ult5"] = previos("pts").sum().reset_index(level=0, drop=True)
largo["goles_favor_ult5"] = previos("gf").mean().reset_index(level=0, drop=True)
largo["goles_contra_ult5"] = previos("gc").mean().reset_index(level=0, drop=True)
largo["dias_descanso"] = (largo.fecha - g["fecha"].shift(1)).dt.days.clip(upper=TOPE_DESCANSO)

# 4. Volver a una fila por partido (variables del local y del visitante)
partes = []
for lado in ["local", "visitante"]:
    t = largo[largo.lado == lado].set_index("id")[NUEVAS]
    t.columns = [f"{c}_{lado}" for c in NUEVAS]
    partes.append(t)
por_partido = pd.concat(partes, axis=1)
h = h.join(por_partido, on="id")

# 5. Unir con el dataset limpio
filas_limpio = len(d)
d["match_date"] = pd.to_datetime(d["match_date"])
d["k_local"] = d.home_team.map(clave)
d["k_visit"] = d.away_team.map(clave)
nuevas_cols = [f"{c}_{lado}" for lado in ["local", "visitante"] for c in NUEVAS]
d = d.merge(h[["match_date", "k_local", "k_visit"] + nuevas_cols],
            on=["match_date", "k_local", "k_visit"], how="left", validate="one_to_one")
d = d.drop(columns=["k_local", "k_visit"])
assert len(d) == filas_limpio, "La unión cambió el número de filas"

# 6. Informe
print("INFORME DE VARIABLES")
print(f"Filas: {len(d)} | columnas: {d.shape[1]} (+{len(nuevas_cols)} nuevas)")
print("\nVacíos por variable nueva:")
print(d[nuevas_cols].isna().sum().to_string())
sin = d[nuevas_cols].isna().any(axis=1)
print(f"\nPartidos con alguna variable vacía: {int(sin.sum())}")
if sin.any():
    print(d[sin].groupby("division_name").size().to_string())

print("\nControl contra la forma del dataset (puntos de los últimos 5 partidos):")
for lado, col in [("local", "home_form5"), ("visitante", "away_form5")]:
    comp = d[f"puntos_ult5_{lado}"].notna() & d[col].notna()
    iguales = (d.loc[comp, f"puntos_ult5_{lado}"] == d.loc[comp, col]).mean() * 100
    print(f"- {lado}: coincide en {iguales:.2f}% de {int(comp.sum())} partidos")

print("\nResumen de las variables:")
print(d[nuevas_cols].describe().loc[["min", "mean", "max"]].round(2).T.to_string())

d.to_csv(SALIDA, index=False)
print(f"\nGuardado en {SALIDA} ({time.time() - inicio:.1f} s)")