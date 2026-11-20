"""Plotly climate charts using the same theme as existing SEAnalytics figures."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative

import theme

ENSO_OBS = "Niño 3.4 observed"
GATUN_OBS = "Gatun historical"
GATUN_FC = "Gatun projection"
ENSO_MEAN = "NMME_model_mean"


def _recent(df: pd.DataFrame, start: pd.Timestamp | None) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if start is None:
        return df
    return df.loc[df["date"] >= start]


def start_date(datasets: dict, years: str) -> pd.Timestamp | None:
    """Select a shared history window based on the newest observation available."""
    if years == "all":
        return None
    most_recent = []
    for name in ("hist_enso", "hist_gatun"):
        df = datasets.get(name)
        if df is not None and not df.empty:
            most_recent.append(df["date"].max())
    if not most_recent:
        return None
    return max(most_recent) - pd.DateOffset(years=int(years))


def _base(yaxis: str, *, dual: bool = False) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        height=300,
        template="plotly_white",
        plot_bgcolor="white",
        hovermode="x unified",
        dragmode="zoom",
        margin=dict(l=42, r=58 if dual else 15, t=34, b=50),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#e8edf3", type="date"),
        yaxis=dict(title=yaxis, zeroline=False, gridcolor="#e8edf3", tickfont_color=theme.DARK_GRAY),
        legend=dict(orientation="h", x=0, xanchor="left", y=1.16, yanchor="bottom", font=dict(size=10)),
        font=dict(family="Arial, Helvetica, sans-serif", color="#333"),
    )
    if dual:
        fig.update_layout(
            yaxis2=dict(
                title=dict(text="Gatun Lake level (m)", font=dict(color="#007f87")), overlaying="y", side="right",
                showgrid=False, zeroline=False, tickfont_color="#007f87",
            )
        )
    return fig


def _add_enso(fig: go.Figure, datasets: dict, start: pd.Timestamp | None) -> None:
    obs = _recent(datasets["hist_enso"], start)
    if not obs.empty:
        fig.add_trace(go.Scatter(
            x=obs.date, y=obs.value_c, mode="lines", name=ENSO_OBS,
            line=dict(color="#141414", width=2.7),
            hovertemplate="%{x|%b %Y}: %{y:.2f} °C<extra>%{fullData.name}</extra>",
        ))
    fc = datasets["forecast_enso"]
    if not fc.empty:
        models = sorted(fc.model.dropna().astype(str).unique())
        palette = qualitative.Dark24
        for ix, model in enumerate(m for m in models if m != ENSO_MEAN):
            group = fc.loc[fc.model.astype(str) == model].sort_values("date")
            fig.add_trace(go.Scatter(
                x=group.date, y=group.value_c, mode="lines+markers", name=model,
                line=dict(color=palette[ix % len(palette)], width=1.8),
                marker=dict(size=4),
                hovertemplate="%{x|%b %Y}: %{y:.2f} °C<extra>%{fullData.name}</extra>",
            ))
        mean = fc.loc[fc.model.astype(str) == ENSO_MEAN].sort_values("date")
        if not mean.empty:
            fig.add_trace(go.Scatter(
                x=mean.date, y=mean.value_c, mode="lines", name="NMME model mean",
                line=dict(color="#E21A1A", width=3, dash="dash"),
                hovertemplate="%{x|%b %Y}: %{y:.2f} °C<extra>%{fullData.name}</extra>",
            ))
    fig.add_hline(y=0.5, line_dash="dot", line_color="#b9b9b9", line_width=1)
    fig.add_hline(y=-0.5, line_dash="dot", line_color="#b9b9b9", line_width=1)
    fig.add_hline(y=0, line_color="#a0a0a0", line_width=1)


def _add_gatun(fig: go.Figure, datasets: dict, start: pd.Timestamp | None, *, secondary: bool) -> None:
    obs = _recent(datasets["hist_gatun"], start)
    yaxis = "y2" if secondary else "y"
    if not obs.empty:
        fig.add_trace(go.Scatter(
            x=obs.date, y=obs.level_mts, mode="lines", name=GATUN_OBS,
            yaxis=yaxis, line=dict(color="#008486", width=3),
            hovertemplate="%{x|%b %Y}: %{y:.2f} m<extra>%{fullData.name}</extra>",
        ))
    fc = datasets["forecast_gatun"]
    if not fc.empty:
        # A future ACP Parquet may contain alternative projection types.
        # Plot each type separately rather than dropping duplicate dates.
        types = fc["type"].dropna().astype(str).unique()
        if len(types) == 0:
            types = ["forecast"]
            fc = fc.copy()
            fc["type"] = "forecast"
        for idx, kind in enumerate(types):
            part = fc.loc[fc["type"].astype(str) == kind].sort_values("date")
            label = GATUN_FC if len(types) == 1 else f"Gatun projection: {kind}"
            fig.add_trace(go.Scatter(
                x=part.date, y=part.level_mts, mode="lines", name=label,
                yaxis=yaxis,
                line=dict(color=["#00AEE7", "#227FB5", "#78BCD7"][idx % 3],
                          width=3 if idx == 0 else 2, dash="dash"),
                hovertemplate="%{x|%b %Y}: %{y:.2f} m<extra>%{fullData.name}</extra>",
            ))


def _forecast_boundary(fig: go.Figure, datasets: dict) -> None:
    future_starts = [
        df["date"].min() for name in ("forecast_enso", "forecast_gatun")
        if not (df := datasets[name]).empty
    ]
    if future_starts:
        fig.add_vline(x=min(future_starts), line_dash="dot", line_width=1.5, line_color="#666")


def combined(datasets: dict, years: str = "5") -> go.Figure:
    """Niño 3.4 (°C, left) and Gatun Lake (m, right), observed and projected."""
    fig = _base("Niño 3.4 SST anomaly (°C)", dual=True)
    beginning = start_date(datasets, years)
    _add_enso(fig, datasets, beginning)
    _add_gatun(fig, datasets, beginning, secondary=True)
    _forecast_boundary(fig, datasets)
    return fig


def enso(datasets: dict, years: str = "5") -> go.Figure:
    fig = _base("Niño 3.4 SST anomaly (°C)")
    _add_enso(fig, datasets, start_date(datasets, years))
    _forecast_boundary(fig, datasets)
    return fig


def gatun(datasets: dict, years: str = "5") -> go.Figure:
    fig = _base("Gatun Lake level (m)")
    _add_gatun(fig, datasets, start_date(datasets, years), secondary=False)
    _forecast_boundary(fig, datasets)
    return fig
