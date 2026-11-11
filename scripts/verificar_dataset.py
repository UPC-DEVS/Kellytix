import pandas as pd

d = pd.read_csv("data/processed/matches_con_cuotas.csv", parse_dates=["match_date"])
print(d.shape, d.match_date.min().date(), d.match_date.max().date())
print(d[["B365H", "B365D", "B365A", "PSCH", "PSCD", "PSCA"]].describe().loc[["min", "max"]])

for p in ["B365", "PSC"]:
    imp = 1 / d[[f"{p}H", f"{p}D", f"{p}A"]]
    print(p, "margen medio de la casa (%):", round((imp.sum(axis=1) - 1).mean() * 100, 2))

g = (d.ft_result == "H").astype(int)
ganancia = g * (d.B365H - 1) - (1 - g)
print("Yield apostando siempre al local (B365):", round(ganancia.mean() * 100, 2), "%")