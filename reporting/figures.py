"""Shared plotly figure builders, reused by the Streamlit dashboard and the
board-pack deck builder so both stay visually consistent. No Streamlit imports.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TRIPS_COLOR = "#4C78A8"
REVENUE_COLOR = "#F58518"


def build_daily_trend_fig(daily: pd.DataFrame, title: str = "Daily trips and revenue") -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=daily["trip_date"], y=daily["total_trips"], name="Trips", marker_color=TRIPS_COLOR),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=daily["trip_date"], y=daily["total_revenue_usd"], name="Revenue (USD)",
                   marker_color=REVENUE_COLOR, mode="lines+markers"),
        secondary_y=True,
    )
    fig.update_layout(title=title, legend=dict(orientation="h", y=1.1))
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Trips", secondary_y=False, tickformat=",")
    fig.update_yaxes(title_text="Revenue (USD)", secondary_y=True, tickformat="$,.0f")
    return fig


def build_top_zones_fig(top_zones: pd.DataFrame, title: str = "Top 10 zones by revenue") -> go.Figure:
    fig = px.bar(
        top_zones.sort_values("total_revenue_usd"),
        x="total_revenue_usd",
        y="pickup_zone",
        orientation="h",
        title=title,
        labels={"total_revenue_usd": "Revenue (USD)", "pickup_zone": "Pickup zone"},
        color_discrete_sequence=[TRIPS_COLOR],
    )
    fig.update_xaxes(tickformat="$,.0f")
    return fig


def build_hourly_heatmap_fig(
    hourly: pd.DataFrame, title: str = "Trips by day of week x pickup hour"
) -> go.Figure:
    pivot = hourly.pivot(index="pickup_day_of_week", columns="pickup_hour", values="total_trips")
    pivot = pivot.reindex(DAY_ORDER)
    fig = px.imshow(
        pivot,
        labels=dict(x="Hour of day", y="Day of week", color="Trips"),
        color_continuous_scale="Blues",
        aspect="auto",
        title=title,
    )
    fig.update_xaxes(dtick=1)
    return fig


def build_payment_mix_by_borough_fig(
    payment_mix: pd.DataFrame, title: str = "Payment mix by borough"
) -> go.Figure:
    fig = px.bar(
        payment_mix,
        x="pickup_borough",
        y="trip_share",
        color="payment_method",
        barmode="stack",
        title=title,
        labels={
            "trip_share": "Share of trips",
            "pickup_borough": "Borough",
            "payment_method": "Payment method",
        },
    )
    fig.update_yaxes(tickformat=".0%")
    return fig


def build_avg_tip_by_payment_method_fig(
    payment_mix: pd.DataFrame, title: str = "Average tip by payment method"
) -> go.Figure:
    fig = px.bar(
        payment_mix,
        x="payment_method",
        y="avg_tip_usd",
        color="pickup_borough",
        barmode="group",
        title=title,
        labels={
            "avg_tip_usd": "Avg tip (USD)",
            "payment_method": "Payment method",
            "pickup_borough": "Borough",
        },
    )
    fig.update_yaxes(tickformat="$.2f")
    return fig


def build_payment_split_by_hour_fig(
    hourly_mix: pd.DataFrame, title: str = "Payment mix by hour of day"
) -> go.Figure:
    fig = px.line(
        hourly_mix.sort_values("pickup_hour"),
        x="pickup_hour",
        y="trip_share",
        color="payment_method",
        title=title,
        labels={
            "pickup_hour": "Hour of day",
            "trip_share": "Share of trips",
            "payment_method": "Payment method",
        },
    )
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(dtick=1)
    return fig
