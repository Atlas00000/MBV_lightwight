# MBV — AI-Powered Roadmap (`ai_powered.md`)

This document is the **implementation plan** for adding an AI layer on top of **MBV-Core** (deterministic EA). It is separate from high-level strategy docs (`concept.md`, `plan.md`) and from narrative AI rationale (`ai_plan.md`).

**Design principle:** Rules generate *hypotheses*; ML answers *“should we trade this instance?”* — not “where will price go?”

**Stop line:** You may **complete only Milestone 1** (structured logging) and pause. All later milestones assume Milestone 1 is **done and stable**.

---

## Executive summary

| Milestone | Scope | Outcome |
|-----------|--------|---------|
| **M1 — Structured logging** | EA + filesystem + schema + validation | Append-only, versioned **signal + outcome** dataset ready for Python |
| **M2 — Labels & QC** | Offline labeling rules, leakage checks, splits | Clean training tables + documented label definitions |
| **M3 — Baseline models** | sklearn / XGBoost or LightGBM, walk-forward | Trained classifiers + metrics + feature importance |
| **M4 — Integration** | API or exported rules, EA gate, fallbacks | Live/tester path: **allow / block / (optional) scale** |

---

## Architecture (target end state)

```text
Market data (MT5)
      ↓
MBV-Core (signals, SL/TP, risk)  ← frozen or version-pinned per experiment
      ↓
Feature snapshot at signal time  ← written in M1
      ↓
[Optional M4] AI score / regime   ← Python API or embedded rules
      ↓
Execute or skip (and log decision)
      ↓
Outcome + MFE/MAE at exit         ← joined in M1/M2
```

**Non-goals for v1:** LLM price prediction, RL inside MT5, continuous online retraining without human review.

---

## Milestone 1 — Structured logging (complete before any model)

**Objective:** Every **candidate** or **executed** signal produces one **wide, flat row** of features + identifiers + later-filled outcomes, with **no lookahead** and **reproducible** schema.

**Definition of done (M1):**

1. **Schema document** — single source of truth: column name, type, units, bar shift (e.g. “value at signal bar close”), and formula reference.
2. **CSV (or SQLite) writer** in MQL5 — append-only, header on new file, rotation by date or size.
3. **Signal ID** — unique per candidate (`Time + Symbol + Magic + Seq` or UUID-style counter persisted across restarts).
4. **Two row types (minimum):**
   - **Signal row:** written when a **candidate** is evaluated (even if trade skipped) *or* when an order is sent — pick one rule and document it.
   - **Outcome row:** written on **position close** (deal closure): P/L, duration, MFE/MAE if available, hit SL/TP/manual.
5. **Join key** — `signal_id` links signal row ↔ outcome row.
6. **Tester validation** — run Strategy Tester; confirm file grows, no empty critical fields, **same EA version + inputs** logged per row or per session header file.
7. **Privacy / path** — `FILE_COMMON` vs terminal-specific folder documented; path configurable via input.

**Suggested feature buckets for M1 (v0 schema):**

- **Identity:** `signal_id`, `dt_gmt`, `symbol`, `chart_tf`, `ea_version`, `magic`, serialized **inputs hash** or key inputs JSON string (bounded length).
- **Signal:** `side` (buy/sell/none), `touch_mode`, prices, BB upper/mid/lower, RSI, ATR, ADX, +DI, −DI, spread points, bar OHLC used (shift 1).
- **Trend filter:** trend TF, EMA value, trend close, `trend_ok_buy`, `trend_ok_sell` booleans.
- **Risk:** SL/TP distance in price and in ATR multiples, lots, `max_pos`, `open_count_at_signal`.
- **Context:** hour (server), weekday, optional session tag (manual enum from hour if no calendar yet).

**Out of scope for M1:** Python training, HTTP calls from EA, model files.

---

## Weekly plan — Milestone 1 only (structured logging)

Adjust calendar to your availability; order is fixed.

### Week 1 — Schema + file layout

| Task | Deliverable |
|------|-------------|
| Freeze “what is a signal?” | Written rule: log **every new-bar evaluation** vs **only when gate passes** vs **only on order send** — pick one for v0. |
| Define column list v0 | `MBV_signal_schema_v0.md` in this folder **or** an annex section at end of `ai_powered.md` |
| Choose storage | CSV append vs SQLite; encoding UTF-8; delimiter `;` or `,` per locale |
| Inputs | `InpLogEnable`, `InpLogPath` (relative name), `InpLogMaxMb` or daily file name pattern |

**Exit:** Reviewable schema table; no code required yet if you prefer spec-first.

### Week 2 — Writer module in MQL5

| Task | Deliverable |
|------|-------------|
| Implement `FileOpen` / flush / error handling | Log failures to `Experts` without breaking trading |
| Session header optional | Small `.json` or `.txt` per run: EA version, build, inputs |
| `signal_id` generator | Monotonic + persistent file counter or time-based + `_Symbol` + `_Period` |

**Exit:** EA compiles; empty or test log file created on tester run.

### Week 3 — Feature snapshot + signal rows

| Task | Deliverable |
|------|-------------|
| Centralize indicator reads | One function fills a struct / parallel arrays for one row |
| Log **numeric** features at signal time | BB/RSI/ATR/ADX/EMA trend series, spread, booleans |
| Log **decision** | `executed` 0/1, `retcode` if failed, `skip_reason` enum (spread, adx, trend, cooldown, maxpos, none) |

**Exit:** Tester produces rows with stable columns; manual eyeball 20 lines in Excel.

### Week 4 — Outcome rows + join + hardening

| Task | Deliverable |
|------|-------------|
| `OnTradeTransaction` or position history polling | On flat, write outcome row with `signal_id` |
| MFE/MAE | If not using MT5’s built-in tester columns in CSV, define: **tester-only** vs **simplified** (e.g. store max favorable excursion via OnTick max — document accuracy tradeoff) |
| Rotation + disk safety | New file per day; cap rows; handle `FILE_WRITE` errors |
| **M1 sign-off checklist** | Runbook: “How to run one month test and produce one clean CSV for Python” |

**Exit:** Milestone 1 **complete** — you can hand a CSV + schema to a Python notebook with confidence.

---

## Milestone 2 — Labels & dataset QC (after M1)

**Objective:** Turn raw logs into **training-ready** tables without leakage.

**Weekly sketch (2–3 weeks typical):**

| Week | Focus |
|------|--------|
| M2-W1 | Python ingest script: parse CSV, dtypes, time sort, duplicate `signal_id` check |
| M2-W2 | Label definitions v1: e.g. `y_profitable` (net R > 0), `y_mfe_gt_1r`, catastrophic flags; document horizon |
| M2-W3 | Walk-forward split by **time**; sanity plots (PF by month without ML); **leakage audit** (no future columns) |

**Definition of done:** `train.parquet` / `val.parquet` + one-page **Label spec** PDF or markdown.

---

## Milestone 3 — Baseline models (after M2)

**Objective:** Prove uplift vs “always trade” on **held-out** periods.

| Week | Focus |
|------|--------|
| M3-W1 | Logistic regression + calibration; metrics: PR-AUC, Brier, PF on **filtered** vs raw (simulated gate) |
| M3-W2 | XGBoost or LightGBM; SHAP or gain-based importance; ablation (remove top 3 features) |
| M3-W3 | Threshold sweep: trade if `p > t`; report PF, DD, trade count vs baseline |

**Definition of done:** Saved model artifact + training config YAML + evaluation notebook committed (repo of your choice).

---

## Milestone 4 — AI integration (after M3)

Pick **one** path first:

| Path | Pros | Cons |
|------|------|------|
| **A. Python FastAPI** | Flexible, fast iteration | Latency, uptime, auth, tester vs live parity |
| **B. Exported rules** | No network; tester-friendly | Weaker than full model; maintenance |

**Weekly sketch (3–4 weeks):**

| Week | Focus |
|------|--------|
| M4-W1 | Contract: JSON in/out, timeout, **fallback** if unreachable (`skip_trade` or `trade_unfiltered`) |
| M4-W2 | EA: `WebRequest` or socket bridge (document MT5 allowlist); log **model version** + **score** on each decision |
| M4-W3 | Shadow mode: log score but **do not** filter; compare offline |
| M4-W4 | Go-live filter: enforce `p_min`; monitor drift |

**Definition of done:** Single symbol live/demo or tester with **gated** execution and full audit log.

---

## Risk register (short)

| Risk | Mitigation |
|------|------------|
| Lookahead in features | Only closed-bar data; code review checklist |
| Overfit to one symbol | Second symbol + walk-forward before trusting PF |
| Log volume | Sample or log only candidates over threshold |
| API failure | Explicit fallback policy; never silent hang |

---

## Annex — Suggested `skip_reason` enum (v0)

| Code | Meaning |
|------|---------|
| 0 | None — trade attempted |
| 1 | Spread too high |
| 2 | ADX too high |
| 3 | Trend filter blocked |
| 4 | Cooldown bars |
| 5 | Max positions |
| 6 | Both buy and sell true |
| 7 | Insufficient bars |
| 8 | Indicator buffer fail |
| 9 | (Reserved) AI blocked — use after M4 |

---

## Document control

| Field | Value |
|-------|--------|
| File | `ai_powered.md` |
| Companion | `ai_plan.md` (rationale), `EA- AI powered Design.md` (stack) |
| MBV-Core reference | `MBV.mq5` — pin `#property version` in logs when M1 starts |

When Milestone 1 is complete, add a line here: **M1 completed: `<date>` — schema version `v0.x` — sample artifact path.**
