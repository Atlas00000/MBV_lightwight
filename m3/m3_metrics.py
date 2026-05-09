"""Threshold sweep, profit factor, max drawdown on time-ordered PnL sequences."""
from __future__ import annotations

import numpy as np
import pandas as pd


def profit_factor(pnl: np.ndarray) -> float:
    pos = pnl[pnl > 0].sum()
    neg = -pnl[pnl < 0].sum()
    if neg <= 0:
        return float("inf") if pos > 0 else float("nan")
    return float(pos / neg)


def max_drawdown_cumulative(pnl_chrono: np.ndarray) -> float:
    """Max drop from running peak on cumulative equity (losses are positive drawdown)."""
    if pnl_chrono.size == 0:
        return 0.0
    eq = np.cumsum(pnl_chrono.astype(float))
    peak = np.maximum.accumulate(eq)
    dd = peak - eq
    return float(np.max(dd)) if dd.size else 0.0


def _gate_mask(df: pd.DataFrame) -> pd.Series:
    return df["out_pnl"].notna() & (df["executed"] == 1)


def threshold_sweep_table(
    val: pd.DataFrame,
    proba_full: np.ndarray,
    thresholds: np.ndarray,
) -> pd.DataFrame:
    """Per threshold: trades taken at p>=t among gate rows; PF and max DD on time-ordered taken PnL."""
    mask = _gate_mask(val)
    if not mask.any():
        return pd.DataFrame(
            columns=["threshold", "n_trades", "n_all", "sum_pnl", "pf", "max_dd", "win_rate"]
        )
    sub = val.loc[mask].copy()
    p = proba_full[mask.to_numpy()]
    pnl = sub["out_pnl"].to_numpy(dtype=float)
    bt = pd.to_numeric(sub.get("bar_time", pd.Series(np.arange(len(sub)))), errors="coerce").to_numpy()
    order = np.argsort(bt, kind="mergesort")
    pnl_chrono = pnl[order]
    p_chrono = p[order]

    rows = []
    n_all = int(len(pnl))
    for t in thresholds:
        take = p_chrono >= t
        k = int(take.sum())
        if k == 0:
            rows.append(
                {
                    "threshold": float(t),
                    "n_trades": 0,
                    "n_all": n_all,
                    "sum_pnl": 0.0,
                    "pf": float("nan"),
                    "max_dd": 0.0,
                    "win_rate": float("nan"),
                }
            )
            continue
        seq = pnl_chrono[take]
        wins = seq[seq > 0]
        wr = float(len(wins) / k) if k else float("nan")
        rows.append(
            {
                "threshold": float(t),
                "n_trades": k,
                "n_all": n_all,
                "sum_pnl": float(seq.sum()),
                "pf": profit_factor(seq),
                "max_dd": max_drawdown_cumulative(seq),
                "win_rate": wr,
            }
        )
    return pd.DataFrame(rows)
