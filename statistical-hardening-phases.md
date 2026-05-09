# MBV — Statistical Hardening & Implementation Phases

**Purpose:** Lock a defensible edge before complexity (sessions, regimes, ML).  
**Rule:** Do **not** add AI until Phase 1 produces **clean data**, **regime labels**, and a **stable baseline** validated out-of-sample.

**Baseline:** EA `MBV.mq5` **v4.32** (defaults aligned with `Profiles/Tester/MBV v4.31 PF.set`). Treat as **frozen hypothesis A** until a phase explicitly changes it.

---

## Phase 0 — Preconditions (complete before heavy work)

| Step | Action |
|------|--------|
| 0.1 | Freeze **inputs + symbol + model quality** (e.g. every tick, 100% history where possible). |
| 0.2 | Export and store **Strategy Tester report** + **.set** for each major run (date in filename). |
| 0.3 | Decide **optimization degrees of freedom** (small subset only, e.g. ADX cap, RSI band edges)—not the whole stack at once. |

---

## Phase 1 — Statistical Hardening (no AI)

### 1.1 Walk-forward analysis (WFA)

**Goal:** Prove the edge survives **time**, not one long in-sample window.

| Step | Action |
|------|--------|
| 1.1.1 | Define **in-sample (IS)** and **out-of-sample (OOS)** windows (example: **2020–2022** optimize → **2023** validate; then roll: **2021–2023** → **2024**, etc.). |
| 1.1.2 | **IS:** optimize only the **agreed small parameter set**; record best params + IS metrics. |
| 1.1.3 | **OOS:** run **fixed** params on the next window; record PF, max DD, trade count, long/short split. |
| 1.1.4 | Require **consistent OOS profitability** (or stable PF band) before promoting parameter changes to “production defaults.” |

**Deliverable:** Spreadsheet or table: window, params, IS PF/DD, OOS PF/DD, trade count.

---

### 1.2 Monte Carlo (execution stress)

**Goal:** Fragility to **spread**, **slippage**, and **trade order** noise.

| Step | Action |
|------|--------|
| 1.2.1 | Use **OOS trade list** (or full validated window), not only IS peaks. |
| 1.2.2 | Simulate **randomized execution**: spread variation, slippage distribution, **trade sequence reshuffling** where your tool supports it. |
| 1.2.3 | Report **distribution** of PF / max DD / worst streak—not a single headline number. |

**Deliverable:** MC summary (e.g. 5th / 50th / 95th percentile PF or ruin probability if defined).

---

### 1.3 Session studies

**Goal:** Sessions already move results; **isolate** edge by liquidity window.

| Step | Action |
|------|--------|
| 1.3.1 | Define **server-time** buckets: **Asia**, **London**, **NY**, **Overlap** (exact hours documented in one place). |
| 1.3.2 | Run **baseline v4.32** with **session masks** (four runs or one run + post-tag in logs). |
| 1.3.3 | Compare **PF, DD, trade count** per session; avoid tuning on the same window used for final claims. |

**Deliverable:** Session × metrics table; optional “session filter” recommendation for Phase 2 code.

---

### 1.4 Spread normalization (stronger than fixed points)

**Goal:** Current **max spread points** filter is weak vs volatility and rollover spikes.

| Step | Action |
|------|--------|
| 1.4.1 | Add metric: **spread / ATR** (or spread vs **rolling spread percentile**) at signal bar. |
| 1.4.2 | **Hard reject** windows with **rollover-style** spread spikes (document rule: e.g. minutes around roll). |
| 1.4.3 | Re-run WFA slice or OOS month with new rule; confirm fewer “toxic” entries without killing volume entirely. |

**Deliverable:** Spec for EA or log column `spread_atr` + rejection rule; before/after comparison.

---

### 1.5 Regime labeling (bridge to future ML, still deterministic)

**Goal:** Label each **entry** so you can slice **where the edge lives**—without training a model yet.

| Step | Action |
|------|--------|
| 1.5.1 | Define **coarse regimes** (example): `trending` / `ranging` / `high_vol` / `low_vol` / `expansion` / `compression` using rules (ADX bins, BB width percentile, ATR percentile, sign vs trend EMA). |
| 1.5.2 | Log **one row per trade** at entry: timestamp, side, features, **regime tags**, spread, session. |
| 1.5.3 | Offline: pivot **PF / expectancy / DD contribution** by regime and session. |

**Deliverable:** CSV schema + short doc mapping columns → definitions; regime × PF table.

---

## Phase 2 — Implementation in codebase (after Phase 1 design is clear)

| Priority | Implementation |
|----------|----------------|
| 2.1 | **CSV (or MT5 `FileWrite`)** on entry: features + session + spread/ATR + regime labels. |
| 2.2 | **Session inputs** (bool or hour ranges) aligned with Phase 1.3 definitions. |
| 2.3 | **Spread normalization** gate (ATR-relative and/or percentile; rollover skip). |
| 2.4 | Optional: **regime filter** inputs (trade only in regimes where OOS slice was positive)—keep behind flags. |

Do **not** expand signal logic until **Phase 1.5** shows where edge concentrates.

---

## Phase 3 — When AI becomes appropriate (later)

AI is useful **after**:

- clean, versioned logs;
- regime + session labels;
- stable **OOS** baseline;
- WFA + MC not collapsing the story.

Then AI can:

- classify **valid vs weak** setups;
- avoid **regimes** where OOS was negative;
- suggest **dynamic thresholds**—always validated again in WFA/OOS, not trusted blindly.

Until then, **AI mostly fits noise**.

---

## Suggested execution order (single thread)

1. **WFA skeleton** (1.1) on frozen core + small param set.  
2. **Log schema** + **session tag** + **spread/ATR** (feeds 1.3–1.5).  
3. **Regime labels** in log (1.5).  
4. **Session / regime slices** offline → decide filters for Phase 2.  
5. **Monte Carlo** (1.2) on **OOS** trades.  
6. **Spread normalization** in EA (1.4) once metric is validated in logs.

---

## References in this repo

| Asset | Role |
|-------|------|
| `MBV.mq5` | Current EA (v4.32 locked defaults). |
| `Profiles/Tester/MBV v4.31 PF.set` | Tester input snapshot matching v4.32 defaults. |
| `concept.md` / `plan.md` | Full MBV vision and phased plan (broader than current EA slice). |
| `EA- AI powered Design.md` | Future ML layer design (after Phase 1). |

---

*Document version: 2026-05-09 — implementation phases for statistical hardening; no AI in Phase 1.*
