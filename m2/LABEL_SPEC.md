# MBV Milestone 2 — Label spec v1

One-page definition of targets derived from **`SIGNAL`** rows joined to **`OUTCOME`** on `signal_id`.

## Horizon

- Labels describe the **closed position** linked to that `signal_id` (exit leg in MT5), not same-bar future price.
- **No same-row leakage:** `out_*` and `y_*` must never be used as inputs to predict the trade opened on that `signal_id`.

## Join

- Left join: all **`event=SIGNAL`** rows keep one row each.
- **`OUTCOME`** rows supply `out_pnl`, `out_dur_s`, `out_mfe`, `out_mae`, `out_pos_id`, `out_xdeal` when `signal_id` matches.
- Rows without a closing outcome keep `out_*` and `y_*` as **null** (censored / no label).

## Labels (v1)

| Column | Definition |
|--------|------------|
| `y_profitable` | `1` if `out_pnl > 0`, else `0`. Integer; null if no outcome. |
| `y_mfe_positive` | `1` if `out_mfe > 0`, else `0`. Null if no outcome. |
| `y_mfe_ge_abs_mae` | `1` if `out_mfe >= abs(out_mae)`. **Proxy** when true “1R in money” is not logged (no lot size in CSV). |
| `y_catastrophic` | `1` if `out_pnl <= -T` (default **T = 1.0** account currency); configurable via `--catastrophic-usd`. |

## Train / validation split

- **Time split:** `SIGNAL` rows with `bar_time > 0`, sorted by `bar_time`, first **80%** → `train.parquet`, remainder → `val.parquet` (default `--train-ratio 0.8`).
- **Walk-forward:** use chronological order only; no random shuffle.

## QC

- **Duplicate `signal_id`:** among `SIGNAL` with `executed=1` and non-empty `signal_id`, duplicates are an error (optional `--fail-on-dup-signal-id`).
- **Monthly PnL text:** `qc_report.txt` sums `out_pnl` by month (UTC from `bar_time`) for sanity.

## MFE / MAE caveat

`out_mfe` / `out_mae` are **approximate** floating extremes from the EA tracker (profit+swap on position), not broker-guaranteed 1R in money.
