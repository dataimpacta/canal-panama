"""Load the four climate Parquet datasets from the SEAnalytics S3 bucket.

No NOAA / ACP downloads occur here. S3 files are managed by a separate ETL.
"""
from __future__ import annotations

import io
import logging

import pandas as pd

LOG = logging.getLogger(__name__)

CLIMATE_BUCKET = "mtcclatamgen"
CLIMATE_PREFIX = "dash"
DATASET_NAMES = ("forecast_gatun", "forecast_enso", "hist_gatun", "hist_enso")

REQUIRED_COLUMNS = {
    "forecast_gatun": ("date", "level_mts", "type", "source"),
    "forecast_enso": ("date", "model", "value_c", "forecast_init", "lead_months", "source", "source_url", "n_models"),
    "hist_gatun": ("date", "level_mts", "type", "source"),
    "hist_enso": ("date", "value_c", "source"),
}


def object_key(dataset: str) -> str:
    """Build the exact S3 key for one of the four datasets."""
    if dataset not in DATASET_NAMES:
        raise ValueError(f"Unrecognized climate dataset: {dataset}")
    return f"{CLIMATE_PREFIX}/{dataset}/{dataset}_in.parquet"


def normalize(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Validate the supplied schemas; preserve their column names and units."""
    if dataset not in REQUIRED_COLUMNS:
        raise ValueError(f"Unrecognized climate dataset: {dataset}")
    missing = set(REQUIRED_COLUMNS[dataset]).difference(df.columns)
    if missing:
        raise ValueError(f"{dataset}: missing columns {sorted(missing)}; found {list(df.columns)}")

    result = df.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce", utc=True).dt.tz_localize(None)
    column = "level_mts" if dataset.endswith("gatun") else "value_c"
    result[column] = pd.to_numeric(result[column], errors="coerce")

    if dataset == "forecast_enso":
        result["forecast_init"] = pd.to_datetime(
            result["forecast_init"], errors="coerce", utc=True
        ).dt.tz_localize(None)
        # Preserve only the most recently initialized forecast cycle.
        if result["forecast_init"].notna().any():
            latest_cycle = result["forecast_init"].max()
            result = result.loc[result["forecast_init"] == latest_cycle].copy()
        result["model"] = result["model"].astype("string")
        result = result.dropna(subset=["model"])

    result = result.dropna(subset=["date", column])
    keys = (["date", "model"] if dataset == "forecast_enso"
            else ["date", "type"] if dataset.endswith("gatun") else ["date"])
    result = result.sort_values("date").drop_duplicates(subset=keys, keep="last")
    return result.reset_index(drop=True)


def load_one(s3_client, dataset: str) -> pd.DataFrame:
    """Read one Parquet file via the existing boto3 client."""
    key = object_key(dataset)
    obj = s3_client.get_object(Bucket=CLIMATE_BUCKET, Key=key)
    raw = obj["Body"].read()
    return normalize(pd.read_parquet(io.BytesIO(raw)), dataset)


def load_all(s3_client) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """Load available sources and retain individual errors for the tab alert."""
    datasets: dict[str, pd.DataFrame] = {}
    errors: dict[str, str] = {}
    for name in DATASET_NAMES:
        try:
            datasets[name] = load_one(s3_client, name)
            if datasets[name].empty:
                errors[name] = f"s3://{CLIMATE_BUCKET}/{object_key(name)} has no usable rows"
        except Exception as exc:  # Do not crash other dashboard tabs on S3 failures.
            datasets[name] = pd.DataFrame(columns=REQUIRED_COLUMNS[name])
            errors[name] = f"s3://{CLIMATE_BUCKET}/{object_key(name)}: {exc}"
            LOG.warning("Climate dataset %s cannot be loaded: %s", name, exc)
    return datasets, errors
