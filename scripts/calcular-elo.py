import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

HISTORIAL = Path("data/raw/matches.csv")
FEATURES = Path("data/processed/features.csv")

K = 12                # cuánto se mueve el rating después de cada partido
VENTAJA_LOCAL = 50    # puntos de Elo que se suman al equipo local
INICIAL = 1500        # rating de un equipo la primera vez que aparece


def clave(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


inicio = time.time()

# 1. Historial: matches.csv (desde el año 2000, todas las divisiones) + partidos nuevos de features.csv
ALIASES = {
    "match_date": ("match_date", "MatchDate", "Date", "fecha"),
    "home_team": ("home_team", "HomeTeam", "equipo_local"),
    "away_team": ("away_team", "AwayTeam", "equipo_visitante"),
    "ft_home_goals": ("ft_home_goals", "FTHome", "FTHG", "goles_local"),
    "ft_away_goals": ("ft_away_goals", "FTAway", "FTAG", "goles_visitante"),
    "ft_result": ("ft_result", "FTResult", "FTR", "resultado_final"),
}


def normalizar_columnas(df, nombre):
    renombres = {}
    for destino, opciones in ALIASES.items():
        encontrada = next((col for col in opciones if col in df.columns), None)
        assert encontrada is not None, (
            f"Falta columna equivalente a '{destino}' en {nombre} "
            f"(disponibles: {list(df.columns)[:10]})"
        )
        renombres[encontrada] = destino
    return df.rename(columns=renombres)


necesarias = list(ALIASES.keys())
h = normalizar_columnas(pd.read_csv(HISTORIAL, low_memory=False), HISTORIAL)
f = normalizar_columnas(pd.read_csv(FEATURES, low_memory=False), FEATURES)

h = pd.concat([h[necesarias], f[necesarias]], ignore_index=True).dropna()
h["match_date"] = pd.to_datetime(h["match_date"])
h["k_local"] = h.home_team.map(clave)
h["k_visit"] = h.away_team.map(clave)
h = h.drop_duplicates(["match_date", "k_local", "k_visit"])  # si se repite, vale matches.csv
h = h.sort_values(["match_date", "k_local"]).reset_index(drop=True)

# 2. Elo en orden cronológico. Se guarda el rating ANTES de cada partido
diferencia = (h.ft_home_goals - h.ft_away_goals).abs().to_numpy()
resultado = np.select([h.ft_result == "H", h.ft_result == "D"], [1.0, 0.5], default=0.0)
multiplicador = np.where(diferencia <= 1, 1.0, np.where(diferencia == 2, 1.5, (11 + diferencia) / 8))
locales, visitantes = h.k_local.to_numpy(), h.k_visit.to_numpy()

rating = {}
previo_local = np.empty(len(h))
previo_visita = np.empty(len(h))
for i in range(len(h)):
    a = rating.get(locales[i], INICIAL)
    b = rating.get(visitantes[i], INICIAL)
    previo_local[i], previo_visita[i] = a, b
    esperado = 1 / (1 + 10 ** (-(a + VENTAJA_LOCAL - b) / 400))
    cambio = K * multiplicador[i] * (resultado[i] - esperado)
    rating[locales[i]] = a + cambio
    rating[visitantes[i]] = b - cambio
h["elo_propio_local"] = previo_local
h["elo_propio_visitante"] = previo_visita

# 3. Añadir las dos columnas a features.csv
nuevas = ["elo_propio_local", "elo_propio_visitante"]
f = f.drop(columns=nuevas, errors="ignore")
filas = len(f)
f["match_date"] = pd.to_datetime(f["match_date"])
f["k_local"] = f.home_team.map(clave)
f["k_visit"] = f.away_team.map(clave)
f = f.merge(
    h[["match_date", "k_local", "k_visit"] + nuevas],
    on=["match_date", "k_local", "k_visit"],
    how="left",
    validate="one_to_one",
)
f = f.drop(columns=["k_local", "k_visit"])
assert len(f) == filas, "La unión cambió el número de filas"

# 4. Informe
print("INFORME DEL ELO PROPIO")
print(f"Parámetros: K={K}, ventaja de local={VENTAJA_LOCAL}, rating inicial={INICIAL}")
print(f"Filas: {len(f)} | partidos en el historial: {len(h)} | equipos: {len(rating)}")
print("Vacíos:", int(f[nuevas].isna().sum().sum()))
print(f"Rating propio: mínimo {f[nuevas].min().min():.0f}, media {f[nuevas].mean().mean():.0f}, máximo {f[nuevas].max().max():.0f}")

comp = f.home_elo.notna() & f.away_elo.notna()
real = np.select([f.ft_result == "H", f.ft_result == "D"], [1.0, 0.5], default=0.0)


def brier(local, visita):
    esperado = 1 / (1 + 10 ** (-(local + VENTAJA_LOCAL - visita) / 400))
    return float(np.mean((esperado[comp] - real[comp]) ** 2))


print(f"\nComparación con el Elo del dataset ({int(comp.sum())} partidos que tienen los dos):")
print(f"- correlación local: {f.loc[comp, 'elo_propio_local'].corr(f.loc[comp, 'home_elo']):.3f}")
print(f"- correlación visitante: {f.loc[comp, 'elo_propio_visitante'].corr(f.loc[comp, 'away_elo']):.3f}")
print(f"- diferencia media absoluta: {(f.loc[comp, 'elo_propio_local'] - f.loc[comp, 'home_elo']).abs().mean():.0f} puntos")
print(
    f"- error de predicción (Brier, menor es mejor): propio {brier(f.elo_propio_local, f.elo_propio_visitante):.4f}"
    f" | dataset {brier(f.home_elo, f.away_elo):.4f} | sin información (siempre 0,5) {float(np.mean((0.5 - real[comp]) ** 2)):.4f}"
)

nuevos = f.match_date >= "2025-07-01"
print(f"\nPartidos desde 2025-07-01: {int(nuevos.sum())} | Elo propio medio: {f.loc[nuevos, nuevas].mean().mean():.0f}")

f.to_csv(FEATURES, index=False)
print(f"\nGuardado en {FEATURES} ({f.shape[1]} columnas, {time.time() - inicio:.1f} s)")