# MBV EA — Development Roadmap (Scaffold → Compile)

This roadmap turns the empty `MBV.mq5` scaffold into a **Phase 1 Edge Discovery & Execution Engine** that matches the specification in `plan.md` (scores, thresholds, state machine, disqualifiers, logging, failure taxonomy).

**Success criterion for “done enough to compile”:** MetaEditor **Compile** succeeds with **0 errors** (warnings documented or eliminated). **Success criterion for Phase 1 research:** Strategy Tester runs, trades execute under rules, and logs capture segments + outcomes.

---

## Phase 0 — Repository & project scaffold

| Step | Task |
|------|------|
| 0.1 | Confirm `MBV.mq5` + `MBV.mqproj` live under `MQL5\Experts\MBV\`; decide whether to split logic into `#include` files later (e.g. `MBV_Scores.mqh`, `MBV_Risk.mqh`) for readability. |
| 0.2 | Add a minimal header comment block: EA name, Phase 1 purpose, link to `plan.md` spec version/date. |
| 0.3 | Define `#property` directives as needed (`strict`, `copyright`, `version`). |
| 0.4 | Choose execution model: **new bar only** on signal timeframe (recommended for discovery consistency) vs tick-level entries — document in code comments. |

**Compile checkpoint:** unchanged skeleton still compiles.

---

## Phase 1 — Inputs, constants, and symbol metadata

| Step | Task |
|------|------|
| 1.1 | Map **input parameters** to spec: score thresholds (65 / 60 / 55 / 50), ATR period 14, BB 20/2.0, EMA 20/50, RSI 14, MACD 12/26/9, range windows (10 / 20), velocity 3 bars, RR sets A/B, time exit 20 bars, risk 0.5%, daily loss 3%, max trades 40, position caps (2 per symbol / 6 total), spread/ATR cap 0.15, slippage limits, latency limit 250 ms, news ±5 min (toggle). |
| 1.2 | Implement **pip/tick helpers**: `_Point`, `_Digits`, `SymbolInfoDouble(SYMBOL_TRADE_TICK_SIZE)` / tick value for sizing; **Forex minimum 3 pips** breakout floor from plan (indices: configurable ticks). |
| 1.3 | Add **instrument tag** input or auto-detect category for slippage rules (Forex vs index vs metal). |

**Compile checkpoint:** `OnInit` / `OnTick` compile with inputs only.

---

## Phase 2 — Time & session layer

| Step | Task |
|------|------|
| 2.1 | Implement **UTC session windows**: London 07:00–11:00, NY 13:00–16:00; define “overlap” flag if both allowed. |
| 2.2 | **Asian tagging**: do not hard-block; set `sessionSegment = Asian | London | NY | Overlap | Other` for logging. |
| 2.3 | Optional stub: **news filter** — calendar integration or manual CSV/blackout list; if deferred, `input bool UseNewsFilter = false` until data source exists. |

**Compile checkpoint:** session helpers compile; no indicator dependency yet.

---

## Phase 3 — Indicator & series layer

| Step | Task |
|------|------|
| 3.1 | Create indicator handles: **ATR(14)**, **BB(20,2)**, **EMA20**, **EMA50**, **RSI(14)**, **MACD(12,26,9)** on the **signal timeframe** (M5 primary per plan; M1 as separate test profile). |
| 3.2 | Centralize **CopyBuffer** / `BarsCalculated` checks; require minimum bars before trading (e.g. max lookback + buffer). |
| 3.3 | Implement safe accessors for **closed bar** vs forming bar (discovery: typically evaluate on bar open using **previous completed bar** data). |

**Compile checkpoint:** `OnInit` creates handles; `OnDeinit` releases handles.

---

## Phase 4 — Score engines (0–100)

Implement exactly the structures in `plan.md`:

| Step | Task |
|------|------|
| 4.1 | **CompressionScore**: BB width compression, ATR compression, range(10) vs avg range(20), body compression (5 vs 20); weights 35/30/25/10; clamp subcomponents 0–1; threshold ≥ 65. |
| 4.2 | **BreakoutScore**: ATR-relative distance beyond 10-bar range, candle expansion vs avg range(20), body dominance, velocity vs ATR(14); weights 35/30/20/15; threshold ≥ 60. |
| 4.3 | **MomentumScore**: EMA alignment binary map to 0/100, RSI bias from 50 scaled/clamped, MACD hist expansion normalized consistently with spec, directional closes 3/3; weights 35/25/25/15; threshold ≥ 55. |
| 4.4 | **VolatilityScore**: ATR vs ATR SMA(20), volatility delta (ATR − ATR[5]), spread efficiency `1 − Spread/ATR` clamped; weights 50/30/20; threshold ≥ 50. |
| 4.5 | Unit-test in Strategy Tester: print scores once per bar to verify ranges (no NaNs, clamped 0–100). |

**Compile checkpoint:** all score functions compile and return doubles.

---

## Phase 5 — Valid breakout & disqualifiers

| Step | Task |
|------|------|
| 5.1 | **LONG**: `Close > HighestHigh(10)` (close beyond range, not wick-only); **SHORT** inverse. |
| 5.2 | **Minimum breakout distance:** ≥ `0.20 × ATR(14)` **and** absolute minimum (Forex 3 pips; indices configurable ticks). |
| 5.3 | **Body dominance** ≥ 0.60 on signal candle. |
| 5.4 | **Disqualify** if: `Spread/ATR > 0.15`; slippage estimate > 1.5 pips (FX) or > 20% ATR (indices); latency > 250 ms (if measurable); breakout candle range > 2.5× ATR (“too extended”). |

**Compile checkpoint:** gate functions pure logic, no order calls yet.

---

## Phase 6 — Market state machine (A → D)

| Step | Task |
|------|------|
| 6.1 | Track **state enum**: `Compression | ExpansionTrigger | Continuation | Exhaustion | Neutral`. |
| 6.2 | Transitions per plan: compression exit on breakout; expansion requires valid breakout + BreakoutScore + VolatilityScore; continuation requires MomentumScore + alignment + sustained ATR; exhaustion triggers (ATR decline vs 3 bars ago, MACD hist shrink 3 bars, or two opposite strong-body candles). |
| 6.3 | **Entry rule:** allow entry when transition **Compression → Expansion** conditions satisfied **and** all four score thresholds pass **and** no disqualifier. |

**Compile checkpoint:** state updates once per new bar; log state changes optionally.

---

## Phase 7 — Risk, sizing, and orders

| Step | Task |
|------|------|
| 7.1 | **Position limits:** max 2 per symbol, 6 total; **no pyramiding**; skip new signal if caps reached. |
| 7.2 | **Fixed risk %** sizing: `Lots = RiskAmount / (SL distance × tick value)` with broker min/max/step normalization. |
| 7.3 | **SL:** `1.2 × ATR(14)` from entry; **TP:** RR 1.5 **or** 2.0 (run as input or magic-number lane for parallel tests). |
| 7.4 | **Time exit:** force close after **20 bars** if neither TP nor SL hit. |
| 7.5 | Use `CTrade` (or OrderSend) with validated stops/freeze level; handle **invalid stops**, requotes, no money. |
| 7.6 | **Daily guardrails:** 0.5% risk/trade, 3% daily loss halt, **5 consecutive losses → 2h cooldown**, max **40 trades/day**. |

**Compile checkpoint:** compiles with `#include <Trade\Trade.mqh>` if used.

---

## Phase 8 — Logging engine (critical for research)

| Step | Task |
|------|------|
| 8.1 | Choose sink: **CSV in `MQL5\Files`** (recommended for analysis) plus `Print` for debug. |
| 8.2 | On **entry**, log: timestamp, symbol, timeframe, direction, all scores, range size, breakout distance, ATR before/after, BB width, spread, session segment, Asian flag, volatility delta, SL/TP prices, RR variant. |
| 8.3 | On **exit**, log: win/loss, MAE/MFE (in R or points), continuation distance, holding bars, exit reason (TP/SL/Time/Critical). |
| 8.4 | Persist **magic number** + comment tag for RR lane (A vs B). |

**Compile checkpoint:** file open/close uses `FILE_COMMON` or terminal-local consistently.

---

## Phase 9 — Failure taxonomy & post-trade classification

| Step | Task |
|------|------|
| 9.1 | Encode enums from plan: `FakeBreakout`, `NoContinuation`, `VolatilityCollapse`, `SpreadInefficiency`, `LateExpansion`, `LiquidityWhipsaw`, `NewsShock`, `MomentumFailure`, `SessionDrift`, `ATRExhaustion`, `SlippageFailure`, `RangeReentry`. |
| 9.2 | Implement **deterministic rules** for each label (extend partial rules in plan §16 — add missing mappings for spread/session/news/slippage/range). |
| 9.3 | **LateExpansionEntry** flag when price > `1.5 × ATR` from breakout OR after **3 consecutive expansion candles**. |

**Compile checkpoint:** classifier runs on closed trades only.

---

## Phase 10 — Strategy Tester harness & compile/release checklist

| Step | Task |
|------|------|
| 10.1 | Run Visual Mode on **M5** primary symbol (e.g. EURUSD); verify trades appear only in allowed sessions if enforced. |
| 10.2 | Verify **minimum bars**, **no trade on first bars**, and **retest logic absent** (Phase 1). |
| 10.3 | **Compile checklist:** `Tools → Options → Compiler` warnings reviewed; `#property strict` clean; no unused handles; `OnDeinit` releases indicators. |
| 10.4 | Export presets: `.set` files for **RR A**, **RR B**, **M1 vs M5** — separate logs as plan requires. |

**Done:** EA compiles, runs in Tester, produces structured logs suitable for edge discovery (≥1000 trades aggregate goal per plan before validation conclusions).

---

## Dependency summary

| Artifact | Purpose |
|----------|---------|
| `plan.md` | Single source of truth for thresholds, formulas, and Phase 1 scope |
| `concept.md` | Thesis / rationale (does not override measurable spec) |
| MetaTrader 5 SDK docs | `CTrade`, indicator buffers, symbol properties, calendar |

---

## Suggested module split (optional, anytime after Phase 4)

- `MBV_Config.mqh` — inputs + enums  
- `MBV_Indicators.mqh` — handles + buffers  
- `MBV_Scores.mqh` — all score math  
- `MBV_Gates.mqh` — breakout validity + disqualifiers  
- `MBV_State.mqh` — state machine  
- `MBV_Risk.mqh` — sizing, limits, cooldowns  
- `MBV_Log.mqh` — CSV schema  
- `MBV_Failure.mqh` — taxonomy + classification  

Keeps `MBV.mq5` thin: `OnInit` / `OnDeinit` / `OnTick` orchestration only.
