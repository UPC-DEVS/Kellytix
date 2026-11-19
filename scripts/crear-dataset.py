import re
from pathlib import Path
import pandas as pd

LIGAS = ["E0", "SP1", "I1", "D1", "F1"]
COLS_CUOTAS = ["B365H", "B365D", "B365A", "PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA"]

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
        raise ValueError(f"Faltan columnas en matches.csv: {', '.join(sorted(faltantes))}")
    return df


m = renombrar_matches(pd.read_csv("data/raw/matches.csv", low_memory=False))
m["match_date"] = pd.to_datetime(m["match_date"])
m = m[m.division_name.isin(LIGAS) & (m.match_date >= "2018-07-01")].copy()
m["k_local"] = m.home_team.map(clave)
m["k_visit"] = m.away_team.map(clave)

partes = []
for f in Path("data/raw/odds").glob("*/*.csv"):
    if f.stem not in LIGAS:
        continue
    o = pd.read_csv(f, encoding="latin-1", on_bad_lines="skip")
    o = o.dropna(subset=["HomeTeam", "AwayTeam"])
    cols = ["Date", "HomeTeam", "AwayTeam"] + [c for c in COLS_CUOTAS if c in o.columns]
    o = o[cols].copy()
    o["Date"] = pd.to_datetime(o["Date"], dayfirst=True, errors="coerce")
    o["division_name"] = f.stem
    o["k_local"] = o.HomeTeam.map(clave)
    o["k_visit"] = o.AwayTeam.map(clave)
    partes.append(o.drop(columns=["HomeTeam", "AwayTeam"]))
odds = pd.concat(partes, ignore_index=True)

llave = ["division_name", "Date", "k_local", "k_visit"]
print("Duplicados en cuotas:", odds.duplicated(llave).sum())
odds = odds.drop_duplicates(llave)

union = m.merge(
    odds,
    left_on=["division_name", "match_date", "k_local", "k_visit"],
    right_on=llave,
    how="left", indicator=True,
)
print("Filas:", len(union), "| esperadas:", len(m))
print("\n% con cuotas por liga:")
print(union.groupby("division_name")["_merge"].apply(lambda s: round((s == "both").mean() * 100, 1)))
print("\nSin cruce:", (union["_merge"] != "both").sum())

union = union[union["_merge"] == "both"].drop(columns=["Date", "k_local", "k_visit", "_merge"])
Path("data/processed").mkdir(parents=True, exist_ok=True)
union.to_csv("data/processed/matches-con-cuotas.csv", index=False)
print("\nGuardado:", union.shape)