# Milestone 3 — baseline training & evaluation

## Install

```powershell
cd m3
pip install -r requirements.txt
```

## Step 0 — enough labeled data (do this before trusting metrics)

1. Run **Strategy Tester** over a longer window (or more symbols) with M1 logging enabled.
2. Point `m2/build_dataset.py` at the new CSV folder; regenerate **`train.parquet`** / **`val.parquet`** and **`qc_report.txt`**.
3. Re-run the scripts below. Small `n` makes PR-AUC / PF unstable.

## Run (after `m2/build_dataset.py`)

**Logistic baseline (M3-W1 + M3-W3 threshold sweep):**

```powershell
python m3_train_baseline.py --train ../m2/output_backtest_20260509/train.parquet --val ../m2/output_backtest_20260509/val.parquet
```

Writes next to `val.parquet`:

- **`m3_baseline_report.txt`** — PR-AUC, ROC-AUC, Brier (calibrated + uncalibrated LR), optional ECE line, gate PnL line.
- **`m3_threshold_sweep.csv`** — per threshold: trade count, sum PnL, profit factor, max drawdown (chronological by `bar_time`), win rate.
- **`m3_artifacts_baseline/model.joblib`** + **`m3_artifacts_baseline/train_config.yaml`** — fitted estimator (calibrated wrapper if enabled) and a small run manifest (paths, hyperparameters, val metrics). Override directory with `--artifact-dir`; skip with `--no-save`.

Options:

- `--calibration none|sigmoid|isotonic` (default `sigmoid`; skipped when labeled train rows are below `--min-train-cal`, default 24). On very small splits, calibration can distort ranking probabilities; compare with `--calibration none`.
- `--no-threshold-csv` — skip the CSV.
- `--threshold 0.5` — gate line only.

**Boosted tree (M3-W2, sklearn `HistGradientBoostingClassifier`):**

```powershell
python m3_train_boosted.py --train ../m2/output_backtest_20260509/train.parquet --val ../m2/output_backtest_20260509/val.parquet
```

Writes **`m3_boosted_report.txt`** next to `val.parquet` (permutation importance + drop top-3 ablation vs full model PR-AUC).

Also **`m3_artifacts_boosted/model.joblib`** + **`train_config.yaml`** unless `--no-save` (same `--artifact-dir` pattern as baseline).

## Modules

| File | Role |
|------|------|
| `m3_pipeline.py` | Feature columns, `prepare_xy`, preprocessor, gate helpers |
| `m3_metrics.py` | Threshold sweep, profit factor, max drawdown |
| `m3_train_baseline.py` | LR + calibration + threshold CSV |
| `m3_train_boosted.py` | HGBC + importance + ablation |
| `m3_save.py` | `joblib` + `train_config.yaml` writer |
