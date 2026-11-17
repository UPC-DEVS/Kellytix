"""Carga masiva del dataset limpio en SQLite usando SQLAlchemy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, delete, insert, select
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import Base, PartidoHistorico  # noqa: E402


DEFAULT_CSV = PROJECT_ROOT / "data" / "processed" / "clean_data.csv"
DEFAULT_DATABASE = PROJECT_ROOT / "kellytix.db"

COLUMNAS = {
    "liga": ("division_name", "division", "liga"),
    "fecha": ("match_date", "date", "fecha"),
    "hora": ("match_time", "time", "hora"),
    "equipo_local": ("home_team", "equipo_local"),
    "equipo_visitante": ("away_team", "equipo_visitante"),
    "elo_local": ("home_elo", "elo_local"),
    "elo_visitante": ("away_elo", "elo_visitante"),
    "forma3_local": ("home_form3", "form3_home", "forma3_local"),
    "forma5_local": ("home_form5", "form5_home", "forma5_local"),
    "forma3_visitante": ("away_form3", "form3_away", "forma3_visitante"),
    "forma5_visitante": ("away_form5", "form5_away", "forma5_visitante"),
    "goles_local": ("ft_home_goals", "home_goals", "goles_local"),
    "goles_visitante": ("ft_away_goals", "away_goals", "goles_visitante"),
    "resultado_final": ("ft_result", "result", "resultado_final"),
    "goles_ht_local": ("ht_home_goals", "goles_ht_local"),
    "goles_ht_visitante": ("ht_away_goals", "goles_ht_visitante"),
    "resultado_ht": ("ht_result", "resultado_ht"),
    "tiros_local": ("home_shots", "tiros_local"),
    "tiros_visitante": ("away_shots", "tiros_visitante"),
    "tiros_puerta_local": ("home_target", "home_shots_on_target", "tiros_puerta_local"),
    "tiros_puerta_visitante": ("away_target", "away_shots_on_target", "tiros_puerta_visitante"),
    "faltas_local": ("home_fouls", "faltas_local"),
    "faltas_visitante": ("away_fouls", "faltas_visitante"),
    "corneres_local": ("home_corners", "corners_home", "corneres_local"),
    "corneres_visitante": ("away_corners", "corners_away", "corneres_visitante"),
    "amarillas_local": ("home_yellow", "home_yellows", "amarillas_local"),
    "amarillas_visitante": ("away_yellow", "away_yellows", "amarillas_visitante"),
    "rojas_local": ("home_red", "home_reds", "rojas_local"),
    "rojas_visitante": ("away_red", "away_reds", "rojas_visitante"),
    "cuota_b365_local": ("B365H", "cuota_b365_local"),
    "cuota_b365_empate": ("B365D", "cuota_b365_empate"),
    "cuota_b365_visitante": ("B365A", "cuota_b365_visitante"),
    "cuota_pinnacle_local": ("PSH", "cuota_pinnacle_local"),
    "cuota_pinnacle_empate": ("PSD", "cuota_pinnacle_empate"),
    "cuota_pinnacle_visitante": ("PSA", "cuota_pinnacle_visitante"),
    "cuota_pinnacle_cierre_local": ("PSCH", "cuota_pinnacle_cierre_local"),
    "cuota_pinnacle_cierre_empate": ("PSCD", "cuota_pinnacle_cierre_empate"),
    "cuota_pinnacle_cierre_visitante": ("PSCA", "cuota_pinnacle_cierre_visitante"),
}

COLUMNAS_NUMERICAS = {
    nombre
    for nombre in COLUMNAS
    if nombre
    not in {
        "liga",
        "fecha",
        "hora",
        "equipo_local",
        "equipo_visitante",
        "resultado_final",
        "resultado_ht",
    }
}
REQUERIDAS = {
    "liga",
    "fecha",
    "equipo_local",
    "equipo_visitante",
    "goles_local",
    "goles_visitante",
    "resultado_final",
}
CLAVE_PARTIDO = ("liga", "fecha", "equipo_local", "equipo_visitante")


def _resolver_columnas(csv_columns: list[str]) -> dict[str, str]:
    disponibles = set(csv_columns)
    faltantes: list[str] = []
    resolved: dict[str, str] = {}
    for destino, aliases in COLUMNAS.items():
        origen = next((alias for alias in aliases if alias in disponibles), None)
        if origen is not None:
            resolved[destino] = origen
        elif destino in REQUERIDAS:
            faltantes.append(f"{destino} ({', '.join(aliases)})")
    if faltantes:
        raise ValueError("Faltan columnas requeridas: " + "; ".join(faltantes))
    return resolved


def _normalizar(df: pd.DataFrame) -> list[dict[str, Any]]:
    columnas = _resolver_columnas(list(df.columns))
    datos = pd.DataFrame(index=df.index)
    for destino, origen in columnas.items():
        datos[destino] = df[origen]

    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce").dt.date
    if "hora" in datos:
        datos["hora"] = datos["hora"].astype("string").str.slice(0, 8)
    for columna in COLUMNAS_NUMERICAS & set(datos.columns):
        datos[columna] = pd.to_numeric(datos[columna], errors="coerce")

    invalidas = datos[list(REQUERIDAS)].isna().any(axis=1)
    if invalidas.any():
        filas = (datos.index[invalidas] + 2).tolist()
        raise ValueError(f"Hay filas inválidas en el CSV (líneas: {filas[:10]}).")
    duplicados = datos.duplicated(list(CLAVE_PARTIDO), keep=False)
    if duplicados.any():
        filas = (datos.index[duplicados] + 2).tolist()
        raise ValueError(
            "El CSV contiene partidos duplicados "
            f"(líneas: {filas[:10]})."
        )

    records = datos.to_dict(orient="records")
    return [
        {columna: (None if pd.isna(valor) else valor) for columna, valor in record.items()}
        for record in records
    ]


def cargar(csv_path: Path, database_path: Path, batch_size: int, replace: bool) -> tuple[int, int]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"No existe el CSV: {csv_path}")
    if batch_size < 1:
        raise ValueError("batch-size debe ser mayor que cero.")

    records = _normalizar(pd.read_csv(csv_path, low_memory=False))
    engine = create_engine(f"sqlite:///{database_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session, session.begin():
        if replace:
            session.execute(delete(PartidoHistorico))
        else:
            existentes = session.execute(
                select(
                    PartidoHistorico.liga,
                    PartidoHistorico.fecha,
                    PartidoHistorico.equipo_local,
                    PartidoHistorico.equipo_visitante,
                )
            ).all()
            claves_existentes = set(existentes)
            records = [
                record
                for record in records
                if tuple(record[columna] for columna in CLAVE_PARTIDO) not in claves_existentes
            ]
        for inicio in range(0, len(records), batch_size):
            session.execute(insert(PartidoHistorico), records[inicio : inicio + batch_size])
    engine.dispose()
    return len(records), len(records) if replace else len(existentes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="CSV limpio de partidos.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help="Archivo SQLite destino.")
    parser.add_argument("--batch-size", type=int, default=1000, help="Filas por inserción.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Vacía partidos_historico antes de cargar (las demás tablas no se modifican).",
    )
    args = parser.parse_args()

    try:
        total, existentes = cargar(args.csv, args.database, args.batch_size, args.replace)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        parser.error(str(error))
    if args.replace:
        print(f"Carga completada: {total} partidos en {args.database}")
    else:
        print(
            f"Carga completada: {total} partidos nuevos en {args.database} "
            f"({existentes} ya existentes omitidos)"
        )


if __name__ == "__main__":
    main()
