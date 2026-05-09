"""Shared M3 helpers: feature lists, X/y prep, preprocessor, gate PnL, proba alignment."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "m2") not in sys.path:
    sys.path.insert(0, str(_ROOT / "m2"))

from split_qc import FEATURE_COLUMNS  # noqa: E402

CAT_FEATURES = ["symbol", "chart_tf", "side", "ea_version", "schema"]
NUM_FEATURES = [c for c in FEATURE_COLUMNS if c not in CAT_FEATURES]


def prepare_xy(df: pd.DataFrame, feature_columns: list[str] | None = None) -> tuple[pd.DataFrame, np.ndarray]:
    cols = feature_columns if feature_columns is not None else FEATURE_COLUMNS
    sub = df.loc[df["y_profitable"].notna()].copy()
    if sub.empty:
        raise ValueError("No rows with non-null y_profitable (need OUTCOME-joined data).")
    y = sub["y_profitable"].astype(np.int32).to_numpy()
    missing = [c for c in cols if c not in sub.columns]
    if missing:
        raise ValueError(f"Parquet missing feature columns: {missing}")
    X = sub[cols].copy()
    for c in CAT_FEATURES:
        if c in X.columns:
            X[c] = X[c].astype(str).fillna("NA")
    return X, y


def build_preprocessor(X_train: pd.DataFrame, feature_columns: list[str] | None = None) -> ColumnTransformer:
    cols = feature_columns if feature_columns is not None else FEATURE_COLUMNS
    X_train = X_train.copy()
    num_present = [c for c in cols if c not in CAT_FEATURES and c in X_train.columns]
    cat_present = [c for c in cols if c in CAT_FEATURES and c in X_train.columns]
    transformers = []
    if num_present:
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_present,
            )
        )
    if cat_present:
        transformers.append(
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=32),
                cat_present,
            )
        )
    if not transformers:
        raise ValueError("No features to train on.")
    return ColumnTransformer(transformers, remainder="drop")


def align_proba_to_val(val: pd.DataFrame, p_labeled: np.ndarray) -> np.ndarray:
    val_labeled = val["y_profitable"].notna()
    proba_full = np.zeros(len(val), dtype=float)
    pos = np.flatnonzero(val_labeled.to_numpy())
    proba_full[pos] = p_labeled
    return proba_full


def gate_pnl(df: pd.DataFrame, proba: np.ndarray, threshold: float) -> dict[str, float]:
    if len(proba) != len(df):
        raise ValueError("proba length mismatch")
    mask = df["out_pnl"].notna() & (df["executed"] == 1)
    if not mask.any():
        return {"n": 0.0, "all_sum": 0.0, "gate_sum": 0.0}
    pnl = df.loc[mask, "out_pnl"].to_numpy(dtype=float)
    take = proba[mask.to_numpy()] >= threshold
    return {
        "n": float(mask.sum()),
        "all_sum": float(pnl.sum()),
        "gate_sum": float(pnl[take].sum()),
    }
