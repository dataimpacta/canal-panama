"""Utility helpers for callbacks."""

from __future__ import annotations


def default_if_none(value, default):
    """Return ``default`` if ``value`` is ``None``."""
    return default if value is None else value


def resolve_date_indices(start_idx, end_idx, date_range):
    """Ensure start and end indices have a value using ``date_range`` defaults."""
    if start_idx is None:
        start_idx = date_range["min_index"]
    if end_idx is None:
        end_idx = date_range["max_index"]
    return start_idx, end_idx
