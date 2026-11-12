"""Transformação do conjunto de pedidos em mart mensal por estado."""

from __future__ import annotations

import pandas as pd


def build_monthly_mart(orders: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    delivered = orders.loc[
        orders["order_status"].eq("delivered")
        & orders["order_delivered_customer_date"].notna()
        & orders["order_estimated_delivery_date"].notna()
        & orders["customer_state"].notna()
    ].copy()
    if delivered.empty:
        raise ValueError("Não há pedidos entregues com estado e datas válidas.")

    delivered["is_late"] = (
        delivered["order_delivered_customer_date"]
        > delivered["order_estimated_delivery_date"]
    )
    delivered["delivery_days"] = (
        delivered["order_delivered_customer_date"]
        - delivered["order_purchase_timestamp"]
    ).dt.total_seconds() / 86_400
    delivered["weather_date"] = delivered[
        "order_estimated_delivery_date"
    ].dt.date
    delivered["month"] = delivered[
        "order_estimated_delivery_date"
    ].dt.to_period("M").astype(str)

    weather = weather.copy()
    weather["weather_date"] = pd.to_datetime(weather["weather_date"]).dt.date
    enriched = delivered.merge(
        weather,
        on=["customer_state", "weather_date"],
        how="left",
        validate="many_to_one",
    )
    enriched["has_weather"] = enriched["precipitation_mm"].notna()

    mart = (
        enriched.groupby(["customer_state", "month"], as_index=False)
        .agg(
            delivered_orders=("order_id", "nunique"),
            late_orders=("is_late", "sum"),
            late_rate_pct=("is_late", "mean"),
            average_delivery_days=("delivery_days", "mean"),
            average_precipitation_mm=("precipitation_mm", "mean"),
            average_temperature_c=("temperature_mean_c", "mean"),
            orders_with_weather=("has_weather", "sum"),
        )
    )
    mart["late_rate_pct"] = (mart["late_rate_pct"] * 100).round(2)
    for column in (
        "average_delivery_days",
        "average_precipitation_mm",
        "average_temperature_c",
    ):
        mart[column] = mart[column].round(2)
    mart["delivered_orders"] = mart["delivered_orders"].astype(int)
    mart["late_orders"] = mart["late_orders"].astype(int)
    mart["orders_with_weather"] = mart["orders_with_weather"].astype(int)
    return mart.sort_values(["month", "customer_state"]).reset_index(drop=True)
