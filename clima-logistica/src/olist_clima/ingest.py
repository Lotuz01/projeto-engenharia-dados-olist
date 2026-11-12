"""Leitura dos CSVs públicos e preparação das entidades de análise."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ORDERS_FILE = "olist_orders_dataset.csv"
CUSTOMERS_FILE = "olist_customers_dataset.csv"
GEOLOCATION_FILE = "olist_geolocation_dataset.csv"


def _read_csv(path: Path, required_columns: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo ausente: {path}. Consulte a seção 'Dados' do README."
        )
    frame = pd.read_csv(path, dtype="string", low_memory=False)
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {path.name}: {sorted(missing)}")
    return frame


def load_orders(raw_dir: Path) -> pd.DataFrame:
    orders = _read_csv(
        raw_dir / ORDERS_FILE,
        {
            "order_id",
            "customer_id",
            "order_purchase_timestamp",
            "order_estimated_delivery_date",
            "order_delivered_customer_date",
            "order_status",
        },
    )
    customers = _read_csv(
        raw_dir / CUSTOMERS_FILE,
        {"customer_id", "customer_state"},
    )

    orders = orders.merge(
        customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )
    for column in (
        "order_purchase_timestamp",
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
    ):
        orders[column] = pd.to_datetime(orders[column], errors="coerce")

    orders["customer_state"] = orders["customer_state"].str.strip().str.upper()
    return orders


def load_state_coordinates(raw_dir: Path) -> pd.DataFrame:
    geo = _read_csv(
        raw_dir / GEOLOCATION_FILE,
        {"geolocation_state", "geolocation_lat", "geolocation_lng"},
    )
    geo["geolocation_lat"] = pd.to_numeric(geo["geolocation_lat"], errors="coerce")
    geo["geolocation_lng"] = pd.to_numeric(geo["geolocation_lng"], errors="coerce")
    geo["geolocation_state"] = geo["geolocation_state"].str.strip().str.upper()
    geo = geo.dropna(subset=["geolocation_state", "geolocation_lat", "geolocation_lng"])

    # A mediana reduz a influência de coordenadas extremas no centro aproximado.
    states = (
        geo.groupby("geolocation_state", as_index=False)
        .agg(
            latitude=("geolocation_lat", "median"),
            longitude=("geolocation_lng", "median"),
        )
        .rename(columns={"geolocation_state": "customer_state"})
    )
    return states
