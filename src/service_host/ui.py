from datetime import datetime, timedelta, timezone

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests
from dash import Input, Output, dash_table, dcc, html

API_BASE = "http://localhost:8000/api/v1"

TIME_RANGES = [
    ("5 minutes", 300),
    ("30 minutes", 1800),
    ("60 minutes", 3600),
    ("3 hours", 10_800),
    ("6 hours", 21_600),
    ("12 hours", 43_200),
    ("24 hours", 86_400),
    ("3 days", 259_200),
    ("7 days", 604_800),
    ("30 days", 2_592_000),
    ("All time", 31_536_000_000), # ~100 years
]


def fetch_messages(params=None) -> pd.DataFrame:
    resp = requests.get(f"{API_BASE}/messages", params=params or {})
    if resp.status_code != 200:
        print("Error fetching messages:", resp.text)
        return pd.DataFrame()

    data = resp.json()
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    return df


def build_filters_card():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Filters", className="mb-3"),
                dbc.Select(
                    id="time-range",
                    options=[
                        {"label": label, "value": str(sec)}
                        for label, sec in TIME_RANGES
                    ],
                    value=str(3600),
                    className="mb-2",
                ),
                dbc.Input(id="filter-user", placeholder="User ID", className="mb-2"),
                dbc.Input(id="filter-aggregate", placeholder="Aggregate ID"),
            ]
        ),
        className="shadow-sm h-100",
    )


def build_kpis_card():
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5("Key Metrics", className="mb-3"),
                html.P(
                    ["Total messages: ", html.Span(id="kpi-total", className="fw-bold")]
                ),
                html.P(
                    [
                        "Average tokens per message: ",
                        html.Span(id="kpi-tokens", className="fw-bold"),
                    ]
                ),
            ]
        ),
        className="shadow-sm h-100",
    )


def build_chart_card():
    return dbc.Card(
        dbc.CardBody(
            [html.H6("Messages & Tokens Over Time"), dcc.Graph(id="chart-over-time")]
        ),
        className="shadow-sm",
    )


def build_table_card():
    columns: list[dict] = [
        {"name": "Timestamp (UTC)", "id": "created_at"},
        {"name": "User", "id": "user_id"},
        {"name": "Aggregation", "id": "aggregate_id"},
        {"name": "Content", "id": "content"},
        {"name": "Role", "id": "role"},
        {"name": "Model", "id": "llm_model"},
        {"name": "Total tokens", "id": "token_count"},
    ]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H6("Messages"),
                dash_table.DataTable(
                    id="table-messages",
                    columns=columns,  # type: ignore[arg-type]
                    page_size=5,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "padding": "6px",
                        "fontFamily": "Arial",
                        "fontSize": "14px",
                    },
                    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                    style_data_conditional=[{"if": {"row_index": "odd"}}],
                ),
            ]
        ),
        className="shadow-sm",
    )


def get_time_params(seconds: int, user=None, aggregate=None) -> dict:
    end = datetime.now(timezone.utc)
    start = end - timedelta(seconds=seconds)
    params = {
        "start_date": start.isoformat().replace("+00:00", "Z"),
        "end_date": end.isoformat().replace("+00:00", "Z"),
    }
    if user:
        params["user_id"] = user
    if aggregate:
        params["aggregate_id"] = aggregate
    return params


def aggregate_over_time(df: pd.DataFrame, seconds: int) -> pd.DataFrame:
    if df.empty or "created_at" not in df.columns:
        return pd.DataFrame()

    if seconds <= 3600:
        rule = "1min"
    elif seconds <= 86400:
        rule = "1H"
    else:
        rule = "1D"

    grouped = (
        df.groupby(pd.Grouper(key="created_at", freq=rule))
        .agg(messages=("id", "count"), tokens=("token_count", "sum"))
        .reset_index()
    )
    return grouped


def create_dashboard() -> dash.Dash:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="Lucerna Dashboard",
        requests_pathname_prefix="/dashboard/",
    )

    app.layout = dbc.Container(
        [
            html.H2("AI Monitoring", className="my-3"),
            dbc.Row(
                [
                    dbc.Col(build_filters_card(), width=6),
                    dbc.Col(build_kpis_card(), width=6),
                ],
                className="mb-4",
                align="stretch",
            ),
            dbc.Row([dbc.Col(build_chart_card(), width=12)], className="mb-4"),
            dbc.Row([dbc.Col(build_table_card(), width=12)]),
        ],
        fluid=True,
    )

    @app.callback(
        [
            Output("kpi-total", "children"),
            Output("kpi-tokens", "children"),
            Output("table-messages", "data"),
            Output("chart-over-time", "figure"),
        ],
        [
            Input("time-range", "value"),
            Input("filter-user", "value"),
            Input("filter-aggregate", "value"),
        ],
    )
    def update_dashboard(time_range_seconds, user, aggregate):
        try:
            seconds = int(time_range_seconds) if time_range_seconds else 259200
        except ValueError:
            seconds = 259200

        params = get_time_params(seconds, user, aggregate)
        df = fetch_messages(params)

        total = len(df)
        avg_tokens = (
            df["token_count"].mean() if "token_count" in df and not df.empty else 0.0
        )

        if "created_at" in df.columns:
            df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

        fig = px.line(title="Messages & Token Usage Over Time")
        grouped = aggregate_over_time(fetch_messages(params), seconds)
        if not grouped.empty:
            fig = px.line(
                grouped,
                x="created_at",
                y=["messages", "tokens"],
                labels={
                    "value": "Count",
                    "created_at": "Time (UTC)",
                    "variable": "Metric",
                },
            )

        return f"{total:,}", f"{avg_tokens:.1f}", df.to_dict("records"), fig

    return app
