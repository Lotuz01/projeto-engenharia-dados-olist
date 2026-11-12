"""Ponto de entrada do pipeline de dados."""

from __future__ import annotations

import logging

from sqlalchemy import create_engine

from olist_clima.config import get_settings
from olist_clima.ingest import load_orders, load_state_coordinates
from olist_clima.transform import build_monthly_mart
from olist_clima.weather import load_or_fetch_weather

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    settings.processed_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Lendo pedidos e coordenadas")
    orders = load_orders(settings.raw_dir)
    states = load_state_coordinates(settings.raw_dir)
    states = states[states["customer_state"].isin(orders["customer_state"].dropna().unique())]

    delivered = orders.loc[
        orders["order_status"].eq("delivered")
        & orders["order_estimated_delivery_date"].notna()
    ]
    if delivered.empty:
        raise ValueError("Não há pedidos entregues com data prevista válida.")
    start_date = delivered["order_estimated_delivery_date"].min().date()
    end_date = delivered["order_estimated_delivery_date"].max().date()

    LOGGER.info("Carregando clima de %s até %s", start_date, end_date)
    weather = load_or_fetch_weather(
        states=states,
        start_date=start_date,
        end_date=end_date,
        cache_path=settings.intermediate_dir / "weather_daily.csv",
        timeout_seconds=settings.open_meteo_timeout_seconds,
    )

    LOGGER.info("Construindo mart mensal")
    mart = build_monthly_mart(orders, weather)
    output_path = settings.processed_dir / "mart_state_delivery_weather_monthly.csv"
    mart.to_csv(output_path, index=False)

    LOGGER.info("Gravando %s linhas no PostgreSQL", len(mart))
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        mart.to_sql(
            "mart_state_delivery_weather_monthly",
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1_000,
            method="multi",
        )
    finally:
        engine.dispose()

    LOGGER.info("Concluído. Mart salvo em %s", output_path)


if __name__ == "__main__":
    main()
