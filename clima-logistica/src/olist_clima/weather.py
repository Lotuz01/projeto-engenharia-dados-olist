"""Cliente simples para o arquivo histórico da API Open-Meteo."""

from __future__ import annotations

import logging
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

LOGGER = logging.getLogger(__name__)
API_URL = "https://archive-api.open-meteo.com/v1/archive"


def _fetch_state(
    state: str,
    latitude: float,
    longitude: float,
    start_date: date,
    end_date: date,
    timeout_seconds: int,
) -> pd.DataFrame:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "precipitation_sum,temperature_2m_mean",
        "timezone": "America/Sao_Paulo",
    }

    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.get(API_URL, params=params, timeout=timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            daily = payload.get("daily", {})
            if not daily.get("time"):
                raise ValueError(f"A API não retornou dias para {state}.")
            return pd.DataFrame(
                {
                    "customer_state": state,
                    "weather_date": pd.to_datetime(daily["time"]).date,
                    "precipitation_mm": daily["precipitation_sum"],
                    "temperature_mean_c": daily["temperature_2m_mean"],
                }
            )
        except (requests.RequestException, ValueError, KeyError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(attempt * 2)

    raise RuntimeError(f"Falha ao consultar clima para {state}: {last_error}")


def load_or_fetch_weather(
    states: pd.DataFrame,
    start_date: date,
    end_date: date,
    cache_path: Path,
    timeout_seconds: int,
) -> pd.DataFrame:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        cache = pd.read_csv(cache_path, parse_dates=["weather_date"])
        cache["weather_date"] = cache["weather_date"].dt.date
    else:
        cache = pd.DataFrame(
            columns=[
                "customer_state",
                "weather_date",
                "precipitation_mm",
                "temperature_mean_c",
            ]
        )

    expected_days = (end_date - start_date).days + 1
    cached_by_state = {
        state: group
        for state, group in cache.groupby("customer_state")
    }

    fetched: list[pd.DataFrame] = []
    for row in states.itertuples(index=False):
        state = row.customer_state
        state_cache = cached_by_state.get(state, pd.DataFrame())
        covers_window = (
            not state_cache.empty
            and state_cache["weather_date"].min() <= start_date
            and state_cache["weather_date"].max() >= end_date
            and len(state_cache[
                state_cache["weather_date"].between(start_date, end_date)
            ]) >= expected_days
        )
        if covers_window:
            continue

        LOGGER.info("Consultando clima histórico para %s", state)
        fresh = _fetch_state(
            state,
            float(row.latitude),
            float(row.longitude),
            start_date,
            end_date,
            timeout_seconds,
        )
        cache = cache[cache["customer_state"] != state]
        fetched.append(fresh)

    if fetched:
        cache = pd.concat([cache, *fetched], ignore_index=True)
        cache = cache.drop_duplicates(["customer_state", "weather_date"])
        cache = cache.sort_values(["customer_state", "weather_date"])
        cache.to_csv(cache_path, index=False)

    return cache[
        cache["customer_state"].isin(states["customer_state"])
        & cache["weather_date"].between(start_date, end_date)
    ].copy()

