import re
from pathlib import Path

import numpy as np
import pandas as pd

LIGAS = ["E0", "SP1", "I1", "D1", "F1"]
COLS_CUOTAS = ["B365H", "B365D", "B365A", "PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA"]
DESDE = "2018-07-01"

# Estadísticas de los archivos de football-data -> nombres que usa el pipeline
ESTADISTICAS = {
    "FTHG": "ft_home_goals", "FTAG": "ft_away_goals", "FTR": "ft_result",
    "HTHG": "ht_home_goals", "HTAG": "ht_away_goals", "HTR": "ht_result",
    "HS": "home_shots", "AS": "away_shots", "HST": "home_target", "AST": "away_target",
    "HF": "home_fouls", "AF": "away_fouls", "HC": "home_corners", "AC": "away_corners",
    "HY": "home_yellow", "AY": "away_yellow", "HR": "home_red", "AR": "away_red",
}
# Columnas que solo trae el dataset de Gábor (los partidos nuevos no las tienen)
SOLO_DATASET = ["home_elo", "away_elo", "home_form3", "home_form5", "away_form3", "away_form5"]

RENOMBRES_MATCHES = {
    "Division": "division_name",
    "MatchDate": "match_date",
    "MatchTime": "match_time",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "HomeElo": "home_elo",
    "AwayElo": "away_elo",
    "Form3Home": "home_form3",
    "Form5Home": "home_form5",
    "Form3Away": "away_form3",
    "Form5Away": "away_form5",
    "FTHome": "ft_home_goals",
    "FTAway": "ft_away_goals",
    "FTResult": "ft_result",
    "HTHome": "ht_home_goals",
    "HTAway": "ht_away_goals",
    "HTResult": "ht_result",
    "HomeShots": "home_shots",
    "AwayShots": "away_shots",
    "HomeTarget": "home_target",
    "AwayTarget": "away_target",
    "HomeFouls": "home_fouls",
    "AwayFouls": "away_fouls",
    "HomeCorners": "home_corners",
    "AwayCorners": "away_corners",
    "HomeYellow": "home_yellow",
    "AwayYellow": "away_yellow",
    "HomeRed": "home_red",
    "AwayRed": "away_red",
}


def clave(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def renombrar_matches(df):
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
    df = df.rename(columns=RENOMBRES_MATCHES)
    requeridas = {"division_name", "match_date", "home_team", "away_team"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en Matches.csv: {', '.join(sorted(faltantes))}")
    return df


# 1. Estadísticas del dataset de Gábor (5 grandes ligas desde 2018)
m = renombrar_matches(pd.read_csv("data/raw/Matches.csv", low_memory=False))
m["match_date"] = pd.to_datetime(m["match_date"])
m = m[m.division_name.isin(LIGAS) & (m.match_date >= DESDE)].copy()
m["k_local"] = m.home_team.map(clave)
m["k_visit"] = m.away_team.map(clave)

# 2. Archivos de football-data (cuotas y, para partidos nuevos, estadísticas)
partes = []
for f in Path("data/raw/odds").glob("*/*.csv"):
    if f.stem not in LIGAS:
        continue
    o = pd.read_csv(f, encoding="latin-1", on_bad_lines="skip")
    o = o.dropna(subset=["HomeTeam", "AwayTeam"])
    cols = (["Date", "HomeTeam", "AwayTeam"]
            + [c for c in ESTADISTICAS if c in o.columns]
            + [c for c in COLS_CUOTAS if c in o.columns])
    o = o[cols].copy()
    o["Date"] = pd.to_datetime(o["Date"], dayfirst=True, errors="coerce")
    o["division_name"] = f.stem
    o["k_local"] = o.HomeTeam.map(clave)
    o["k_visit"] = o.AwayTeam.map(clave)
    partes.append(o)
odds = pd.concat(partes, ignore_index=True)

llave = ["division_name", "Date", "k_local", "k_visit"]
print("Duplicados en cuotas:", odds.duplicated(llave).sum())
odds = odds.drop_duplicates(llave)

# 3. Partidos que están en las dos fuentes: estadísticas del dataset + cuotas
solo_cuotas = odds[llave + COLS_CUOTAS]
union = m.merge(
    solo_cuotas,
    left_on=["division_name", "match_date", "k_local", "k_visit"],
    right_on=llave,
    how="left", indicator=True,
)
print("Partidos del dataset:", len(m))
print("\n% con cuotas por liga:")
print(union.groupby("division_name")["_merge"].apply(lambda s: round((s == "both").mean() * 100, 1)))
print("Sin cruce:", (union["_merge"] != "both").sum())
union = union[union["_merge"] == "both"].drop(columns=["Date", "k_local", "k_visit", "_merge"])

# 4. Partidos que solo están en football-data (los posteriores al dataset de Gábor)
en_dataset = m[["division_name", "match_date", "k_local", "k_visit"]].rename(columns={"match_date": "Date"})
nuevos = odds.merge(en_dataset, on=llave, how="left", indicator=True)
nuevos = nuevos[(nuevos["_merge"] == "left_only") & (nuevos.Date >= DESDE)].drop(columns="_merge")
assert {"FTHG", "FTAG", "FTR"} <= set(nuevos.columns), "Los archivos de football-data no traen FTHG, FTAG y FTR"
sin_resultado = nuevos[["FTHG", "FTAG", "FTR"]].isna().any(axis=1)
print(f"\nPartidos solo en football-data: {len(nuevos)} (sin resultado, descartados: {int(sin_resultado.sum())})")
nuevos = nuevos[~sin_resultado]

filas = pd.DataFrame({
    "division_name": nuevos.division_name,
    "match_date": nuevos.Date,
    "home_team": nuevos.HomeTeam,
    "away_team": nuevos.AwayTeam,
})
for origen, destino in ESTADISTICAS.items():
    filas[destino] = nuevos[origen] if origen in nuevos.columns else np.nan
for c in SOLO_DATASET:
    filas[c] = np.nan
for c in COLS_CUOTAS:
    filas[c] = nuevos[c] if c in nuevos.columns else np.nan
print(filas.groupby("division_name").size().to_string())

# 5. Dataset final
final = pd.concat([union, filas], ignore_index=True)[list(union.columns)]
final = final.sort_values(["match_date", "division_name", "home_team"]).reset_index(drop=True)

# Pinnacle: desde el 23/07/2025 sus cuotas no son fiables (aviso de football-data.co.uk)
cols_pinnacle = ["PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA"]
final.loc[final.match_date >= pd.Timestamp("2025-07-23"), cols_pinnacle] = np.nan

Path("data/processed").mkdir(parents=True, exist_ok=True)
final.to_csv("data/processed/matches_con_cuotas.csv", index=False)
print(f"\nGuardado: {final.shape} ({len(union)} del dataset + {len(filas)} de football-data)")