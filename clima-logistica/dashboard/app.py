"""Dashboard exploratório do mart mensal."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Olist | Clima e logística", page_icon="🌦️", layout="wide")
st.title("Clima e desempenho logístico")
st.caption("Exploração mensal dos atrasos de entrega no conjunto público Olist.")

project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "processed" / "mart_state_delivery_weather_monthly.csv"

if not data_path.exists():
    st.info(
        "Ainda não encontrei o mart. Siga os passos de instalação e execução no README."
    )
    st.stop()

data = pd.read_csv(data_path)
if data.empty:
    st.warning("O mart não contém linhas para exibir.")
    st.stop()

states = sorted(data["customer_state"].dropna().unique())
selected_states = st.multiselect(
    "Estados",
    options=states,
    default=states,
    help="Filtre os estados exibidos nos gráficos.",
)
filtered = data[data["customer_state"].isin(selected_states)].copy()

if filtered.empty:
    st.warning("Selecione pelo menos um estado.")
    st.stop()

total_orders = int(filtered["delivered_orders"].sum())
late_orders = int(filtered["late_orders"].sum())
weighted_late_rate = (late_orders / total_orders * 100) if total_orders else 0
weather_coverage = (
    filtered["orders_with_weather"].sum() / total_orders * 100 if total_orders else 0
)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Pedidos entregues", f"{total_orders:,}".replace(",", "."))
kpi2.metric("Taxa ponderada de atraso", f"{weighted_late_rate:.1f}%")
kpi3.metric("Pedidos com clima", f"{weather_coverage:.1f}%")

monthly = (
    filtered.groupby("month", as_index=False)
    .agg(
        delivered_orders=("delivered_orders", "sum"),
        late_orders=("late_orders", "sum"),
        precipitation_mm=("average_precipitation_mm", "mean"),
        temperature_c=("average_temperature_c", "mean"),
    )
)
monthly["late_rate_pct"] = (
    monthly["late_orders"] / monthly["delivered_orders"] * 100
).round(2)

st.subheader("Taxa de atraso por mês")
figure = px.line(
    monthly,
    x="month",
    y="late_rate_pct",
    markers=True,
    labels={"month": "Mês", "late_rate_pct": "Pedidos atrasados (%)"},
)
figure.update_layout(xaxis_tickangle=-45, yaxis_ticksuffix="%")
st.plotly_chart(figure, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Chuva média na data prevista")
    figure = px.bar(
        monthly,
        x="month",
        y="precipitation_mm",
        labels={"month": "Mês", "precipitation_mm": "Chuva média (mm)"},
    )
    figure.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(figure, use_container_width=True)

with right:
    st.subheader("Temperatura média na data prevista")
    figure = px.line(
        monthly,
        x="month",
        y="temperature_c",
        markers=True,
        labels={"month": "Mês", "temperature_c": "Temperatura média (°C)"},
    )
    figure.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(figure, use_container_width=True)

st.subheader("Detalhamento por estado e mês")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.caption(
    "A localização do clima é aproximada por estado. A associação observada não demonstra causalidade."
)
