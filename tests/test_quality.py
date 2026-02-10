import os
import pytest
import psycopg
from dotenv import load_dotenv

load_dotenv()

PG_URL = os.getenv("PG_URL")

def test_order_id_not_null():
    """Verifica se não há order_id nulo nas tabelas de staging."""
    query = "SELECT count(*) FROM stg.orders WHERE order_id IS NULL"
    with psycopg.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()[0]
            assert result == 0, "Existem order_id nulos em stg.orders"

def test_freight_value_non_negative():
    """Verifica se o valor do frete não é negativo."""
    query = "SELECT count(*) FROM stg.order_items WHERE freight_value < 0"
    with psycopg.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()[0]
            assert result == 0, "Existem valores de frete negativos em stg.order_items"

def test_lead_time_non_negative():
    """Verifica se o lead_time_days não é negativo em marts.fct_deliveries."""
    query = "SELECT count(*) FROM marts.fct_deliveries WHERE lead_time_days < 0"
    with psycopg.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()[0]
            assert result == 0, "Existem lead_time_days negativos em marts.fct_deliveries"
