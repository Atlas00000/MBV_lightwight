"""M2-W2: join OUTCOME onto SIGNAL rows and add label columns (v1)."""
from __future__ import annotations

import numpy as np
import pandas as pd

OUTCOME_KEEP = ["signal_id", "pnl", "dur_s", "mfe", "mae", "pos_id", "xdeal"]


def outcomes_table(df: pd.DataFrame) -> pd.DataFrame:
    o = df.loc[df["event"] == "OUTCOME", OUTCOME_KEEP].copy()
    o = o[o["signal_id"].str.len() > 0]
    # One row per signal_id (last wins if duplicates)
    o = o.drop_duplicates(subset=["signal_id"], keep="last")
    return o.rename(
        columns={
            "pnl": "out_pnl",
            "dur_s": "out_dur_s",
            "mfe": "out_mfe",
            "mae": "out_mae",
            "pos_id": "out_pos_id",
            "xdeal": "out_xdeal",
        }
    )


def signal_table(df: pd.DataFrame) -> pd.DataFrame:
    s = df.loc[df["event"] == "SIGNAL"].copy()
    return s


def join_outcomes(
    signals: pd.DataFrame,
    outcomes: pd.DataFrame,
    catastrophic_usd: float = 1.0,
) -> pd.DataFrame:
    merged = signals.merge(outcomes, on="signal_id", how="left")
    return add_label_columns(merged, catastrophic_usd=catastrophic_usd)


def add_label_columns(df: pd.DataFrame, catastrophic_usd: float = 1.0) -> pd.DataFrame:
    """Add y_* only where `out_pnl` is present (closed leg known)."""
    out = df.copy()
    has = out["out_pnl"].notna()
    out["y_profitable"] = pd.NA
    out.loc[has, "y_profitable"] = (out.loc[has, "out_pnl"] > 0).astype(np.int8)

    out["y_mfe_positive"] = pd.NA
    out.loc[has, "y_mfe_positive"] = (out.loc[has, "out_mfe"].fillna(0.0) > 0).astype(np.int8)

    # Proxy for "at least ~1R favorable vs adverse excursion" when 1R money not in log:
    # True if peak floating >= absolute worst drawdown magnitude (both from OUTCOME).
    mae_abs = out.loc[has, "out_mae"].fillna(0.0).abs()
    mfe = out.loc[has, "out_mfe"].fillna(0.0)
    out["y_mfe_ge_abs_mae"] = pd.NA
    out.loc[has, "y_mfe_ge_abs_mae"] = (mfe >= mae_abs).astype(np.int8)

    out["y_catastrophic"] = pd.NA
    out.loc[has, "y_catastrophic"] = (out.loc[has, "out_pnl"] <= -float(catastrophic_usd)).astype(np.int8)

    return out


def labels_summary(df: pd.DataFrame, catastrophic_usd: float = 1.0) -> str:
    has = df["out_pnl"].notna()
    n = int(has.sum())
    if n == 0:
        return "No OUTCOME joins (n=0)."
    sub = df.loc[has]
    pos_rate = float(sub["y_profitable"].mean())
    cat_rate = float(sub["y_catastrophic"].mean())
    return (
        f"rows_with_outcome={n}\n"
        f"mean(y_profitable)={pos_rate:.3f}\n"
        f"mean(y_catastrophic|pnl<=-{catastrophic_usd})={cat_rate:.3f}"
    )
