# Milestone 2 — dataset build

## One-shot run

From the **`MBV`** folder (or any cwd), install once then build:

```powershell
cd m2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python build_dataset.py --input "C:/Users/emili/AppData/Roaming/MetaQuotes/Terminal/Common/Files/MBV_sig_EURUSD_*.csv" --out-dir output
```

Outputs:

- `output/train.parquet`, `output/val.parquet`
- `output/qc_report.txt`

See **`LABEL_SPEC.md`** for label definitions and leakage rules.

## “Compile” check (syntax only)

```powershell
python -m py_compile ingest.py labels.py split_qc.py build_dataset.py
```
