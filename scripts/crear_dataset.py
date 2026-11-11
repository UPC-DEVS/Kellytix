import re
from pathlib import Path
import pandas as pd

LIGAS = ["E0", "SP1", "I1", "D1", "F1"]
COLS_CUOTAS = ["B365H", "B365D", "B365A", "PSH", "PSD", "PSA", "PSCH", "PSCD", "PSCA"]

def clave(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

m = pd.read_csv("data/raw/Matches.csv", low_memory=False)
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
union.to_csv("data/processed/matches_con_cuotas.csv", index=False)
print("\nGuardado:", union.shape)