# src/service_host/ui.py
from datetime import datetime, timedelta, timezone

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests
from dash import Input, Output, dash_table, dcc, html

API_BASE = "http://localhost:8000/api/v1"

# --- Preset time ranges (label, seconds) ---
TIME_RANGES = [
    ("5 minutes", 5 * 60),
    ("30 minutes", 30 * 60),
    ("60 minutes", 60 * 60),
    ("3 hours", 3 * 3600),
    ("6 hours", 6 * 3600),
    ("12 hours", 12 * 3600),
    ("24 hours", 24 * 3600),
    ("3 days", 3 * 86400),
    ("7 days", 7 * 86400),
    ("30 days", 30 * 86400),
]


# --- Data fetching ---
def fetch_messages(params=None) -> pd.DataFrame:
    response = requests.get(f"{API_BASE}/messages", params=params or {})

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")

    return df


# --- App ---
app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.SPACELAB], title="Lucerna Dashboard"
)


app.layout = dbc.Container(
    [
        html.H2("AI Monitoring", className="my-3"),
        # --- Filters + KPIs Row ---
        dbc.Row(
            [
                # Filters card
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Filters", className="mb-3"),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Select(
                                                id="time-range",
                                                options=[
                                                    {
                                                        "label": label,
                                                        "value": str(seconds),
                                                    }
                                                    for label, seconds in TIME_RANGES
                                                ],
                                                value=str(60 * 60),
                                            ),
                                            width=12,
                                            className="mb-2",
                                        ),
                                        dbc.Col(
                                            dbc.Input(
                                                id="filter-user", placeholder="User ID"
                                            ),
                                            width=12,
                                            className="mb-2",
                                        ),
                                        dbc.Col(
                                            dbc.Input(
                                                id="filter-aggregate",
                                                placeholder="Aggregate ID",
                                            ),
                                            width=12,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    width=6,
                ),
                # KPIs card
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Key Metrics", className="mb-3"),
                                html.P(
                                    [
                                        "Total messages: ",
                                        html.Span(id="kpi-total", className="fw-bold"),
                                    ],
                                    className="mb-2",
                                ),
                                html.P(
                                    [
                                        "Average tokens per message: ",
                                        html.Span(id="kpi-tokens", className="fw-bold"),
                                    ],
                                    className="mb-0",
                                ),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
            align="stretch",
        ),
        # --- Chart Row ---
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Messages & Tokens Over Time"),
                                dcc.Graph(id="chart-over-time"),
                            ]
                        ),
                        className="shadow-sm",
                    ),
                    width=12,
                )
            ],
            className="mb-4",
        ),
        # --- Table Row ---
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6("Messages"),
                                dash_table.DataTable(
                                    id="table-messages",
                                    columns=[
                                        {"name": "Timestamp (UTC)", "id": "created_at"},
                                        {"name": "User", "id": "user_id"},
                                        {"name": "Aggregation", "id": "aggregate_id"},
                                        {"name": "Content", "id": "content"},
                                        {"name": "Role", "id": "role"},
                                        {"name": "Model", "id": "llm_model"},
                                        {"name": "Response", "id": "response"},
                                        {"name": "Total tokens", "id": "token_count"},
                                    ],
                                    page_size=5,
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "6px",
                                        "fontFamily": "Arial",
                                        "fontSize": "14px",
                                    },
                                    style_header={
                                        "backgroundColor": "#f8f9fa",
                                        "fontWeight": "bold",
                                    },
                                    style_data_conditional=[
                                        {"if": {"row_index": "odd"}}
                                    ],
                                ),
                            ]
                        ),
                        className="shadow-sm",
                    ),
                    width=12,
                )
            ]
        ),
    ],
    fluid=True,
)


# --- Callbacks ---
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
    # Compute start/end in UTC
    try:
        seconds = int(time_range_seconds) if time_range_seconds else 3 * 86400
    except Exception:
        seconds = 3 * 86400

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(seconds=seconds)

    params = {
        "start_date": start_dt.isoformat().replace("+00:00", "Z"),
        "end_date": end_dt.isoformat().replace("+00:00", "Z"),
    }
    if user:
        params["user_id"] = user
    if aggregate:
        params["aggregate_id"] = aggregate

    df = fetch_messages(params)

    # KPIs
    total = len(df)
    avg_tokens = (
        float(df["token_count"].mean()) if "token_count" in df and not df.empty else 0.0
    )

    # Table formatting
    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Chart (group by time buckets)
    fig = px.line(title="Messages & Token Usage Over Time")
    if not df.empty and "created_at" in df.columns:
        # Determine bucket size based on time range
        if seconds <= 3600:  # up to 1 hour → 1-min buckets
            rule = "1min"
        elif seconds <= 86400:  # up to 1 day → 1-hour buckets
            rule = "1H"
        else:  # longer → daily buckets
            rule = "1D"

        df_time = fetch_messages(params)  # fetch fresh with datetime intact
        df_time["created_at"] = pd.to_datetime(
            df_time["created_at"], utc=True, errors="coerce"
        )

        grouped = (
            df_time.groupby(pd.Grouper(key="created_at", freq=rule))
            .agg(
                messages=("id", "count"),
                tokens=("token_count", "sum"),
            )
            .reset_index()
        )

        fig = px.line(
            grouped,
            x="created_at",
            y=["messages", "tokens"],
            labels={"value": "Count", "created_at": "Time (UTC)", "variable": "Metric"},
        )

    return f"{total:,}", f"{avg_tokens:.1f}", df.to_dict("records"), fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
