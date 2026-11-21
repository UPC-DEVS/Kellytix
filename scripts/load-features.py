"""Carga las variables previas al partido (features.csv) en la tabla partidos_features."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, delete, insert, select
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Base, PartidoFeatures, PartidoHistorico  # noqa: E402

DEFAULT_CSV = PROJECT_ROOT / "data" / "processed" / "features.csv"
DEFAULT_DATABASE = PROJECT_ROOT / "kellytix.db"

VARIABLES = [
    "puntos_ult5_local",
    "puntos_ult5_visitante",
    "goles_favor_ult5_local",
    "goles_favor_ult5_visitante",
    "goles_contra_ult5_local",
    "goles_contra_ult5_visitante",
    "dias_descanso_local",
    "dias_descanso_visitante",
    "elo_propio_local",
    "elo_propio_visitante",
]
# Columnas del CSV que identifican el partido en partidos_historico
CLAVE = ["division_name", "match_date", "home_team", "away_team"]


def cargar(csv_path: Path, database_path: Path, version: str, batch_size: int, replace: bool) -> tuple[int, int]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"No existe el CSV: {csv_path}")
    if batch_size < 1:
        raise ValueError("batch-size debe ser mayor que cero.")

    df = pd.read_csv(csv_path, low_memory=False)
    faltan = [c for c in CLAVE + VARIABLES if c not in df.columns]
    if faltan:
        raise ValueError("Faltan columnas en el CSV: " + ", ".join(faltan) + ". ¿Ejecutaste calcular-elo.py?")
    df["match_date"] = pd.to_datetime(df["match_date"]).dt.date

    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session, session.begin():
        partidos = session.execute(
            select(
                PartidoHistorico.id_partido,
                PartidoHistorico.liga,
                PartidoHistorico.fecha,
                PartidoHistorico.equipo_local,
                PartidoHistorico.equipo_visitante,
            )
        ).all()
        if not partidos:
            raise ValueError("partidos_historico está vacía. Ejecuta antes scripts/load-db.py.")
        ids = pd.DataFrame(partidos, columns=["id_partido"] + CLAVE)
        union = df.merge(ids, on=CLAVE, how="left")
        sin_id = union["id_partido"].isna()
        if sin_id.any():
            raise ValueError(
                f"{int(sin_id.sum())} filas del CSV no están en partidos_historico "
                "(¿se cargó otra versión del dataset?)."
            )

        if replace:
            session.execute(delete(PartidoFeatures).where(PartidoFeatures.version == version))
        else:
            existentes = set(
                session.execute(
                    select(PartidoFeatures.id_partido).where(PartidoFeatures.version == version)
                ).scalars()
            )
            union = union[~union["id_partido"].isin(existentes)]

        registros = []
        for fila in union[["id_partido"] + VARIABLES].itertuples(index=False):
            registro = {"id_partido": int(fila[0]), "version": version}
            for nombre, valor in zip(VARIABLES, fila[1:]):
                registro[nombre] = None if pd.isna(valor) else float(valor)
            registros.append(registro)
        for inicio in range(0, len(registros), batch_size):
            session.execute(insert(PartidoFeatures), registros[inicio : inicio + batch_size])
    engine.dispose()
    return len(registros), len(df) - len(registros)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="CSV con las variables.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help="Archivo SQLite destino.")
    parser.add_argument("--version", default="v1", help="Versión de la definición de las variables.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Filas por inserción.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Borra las filas de esa versión antes de cargar (otras versiones no se tocan).",
    )
    args = parser.parse_args()

    try:
        nuevas, omitidas = cargar(args.csv, args.database, args.version, args.batch_size, args.replace)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        parser.error(str(error))
    print(
        f"Carga completada: {nuevas} filas de la versión {args.version} en {args.database} "
        f"({omitidas} ya existentes omitidas)"
    )


if __name__ == "__main__":
    main()