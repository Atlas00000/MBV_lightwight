# Momentum + Breakout + Volatility Expansion

# Edge Discovery & Execution Engine Plan

## Converting Concepts Into Real Market Variables

The objective of this phase is NOT:

* optimization
* profitability smoothing
* low drawdown
* advanced filtering

The objective is:

# Convert abstract market concepts into measurable execution variables.

This transforms:

* “momentum”
* “compression”
* “breakout”
* “continuation”

into:

* quantifiable states
* executable triggers
* researchable data

---

# 1. CORE EXECUTION PHILOSOPHY

The EA should behave like a:

# Market State Detector

NOT a “perfect signal finder.”

At this stage the engine should:

* detect behavior
* participate frequently
* log aggressively
* expose edge characteristics

The system should intentionally:

* allow some bad trades
* allow false breakouts
* allow noisy conditions

because those losses reveal:

* where the edge fails
* why it fails
* which conditions matter

---

# 2. CORE MARKET MODEL

The market model becomes:

## STATE A — COMPRESSION

Low volatility + tight structure

↓

## STATE B — EXPANSION TRIGGER

Breakout + volatility increase

↓

## STATE C — MOMENTUM CONTINUATION

Directional persistence

↓

## STATE D — EXHAUSTION

Expansion decay / failed continuation

The EA’s job:

* detect transitions between these states

---

# 3. CONVERTING CONCEPTS INTO REAL MARKET VARIABLES

---

# A. COMPRESSION DETECTION

## Concept

“Market energy buildup”

## Real Market Variables

### 1. Bollinger Band Width Compression

Measure:

* current BB width
  vs
* average BB width over X candles

Real interpretation:

* volatility shrinking
* price coiling

Example:
Current BB width < 70% of average BB width

---

### 2. ATR Compression

Measure:
Current ATR vs rolling ATR average

Real interpretation:

* candle range suppression
* declining volatility

Example:
Current ATR < 0.8 × ATR average

---

### 3. Range Tightness

Measure:
Highest high − lowest low over N candles

Real interpretation:

* visible consolidation
* liquidity clustering

Example:
15-candle range < 1.2 × average candle range

---

### 4. Candle Body Contraction

Measure:
Average body size decreasing

Real interpretation:

* market indecision
* reduced aggression

---

# COMPRESSION SCORE

Instead of binary logic:

Create:

* Compression Score (0–100)

Based on:

* BB contraction
* ATR contraction
* range contraction
* candle contraction

This becomes a measurable market state.

---

# B. BREAKOUT DETECTION

## Concept

“Energy release”

## Real Market Variables

### 1. Range Break

Measure:
Close beyond recent range high/low

Real interpretation:

* liquidity boundary breached

Example:
Close > previous 10-bar high

---

### 2. Breakout Distance

Measure:
Distance beyond breakout level

Real interpretation:

* breakout strength

Weak breakouts:
tiny breaches

Strong breakouts:
clear displacement

---

### 3. Candle Expansion

Measure:
Current candle size vs average candle size

Real interpretation:

* aggressive repricing

Example:
Breakout candle > 1.5× average candle size

---

### 4. Velocity

Measure:
Rate of movement over short interval

Real interpretation:

* expansion acceleration

Important for:

* M1/M5 breakout quality

---

# BREAKOUT SCORE

Build:

* breakout quality score

Variables:

* breakout distance
* candle expansion
* velocity
* range escape strength

---

# C. MOMENTUM CONFIRMATION

## Concept

“Directional continuation probability”

## Real Market Variables

### 1. EMA Alignment

Measure:
EMA20 above EMA50
or below

Real interpretation:

* directional flow

---

### 2. RSI Directional State

Measure:
RSI > 50
or
RSI < 50

Real interpretation:

* directional pressure

NOT overbought/oversold.

---

### 3. MACD Histogram Expansion

Measure:
Current histogram > previous histogram

Real interpretation:

* acceleration increasing

This is critical.

Acceleration matters more than static trend.

---

### 4. Consecutive Directional Closes

Measure:
Bullish closes count
or bearish closes count

Real interpretation:

* continuation persistence

---

# MOMENTUM SCORE

Variables:

* EMA alignment
* RSI bias
* MACD expansion
* directional candle persistence

---

# D. VOLATILITY EXPANSION

## Concept

“Expansion phase activated”

## Real Market Variables

### 1. ATR Expansion

Measure:
Current ATR > ATR average

Real interpretation:

* volatility release active

---

### 2. Spread-to-ATR Ratio

Measure:
Spread relative to volatility

Real interpretation:

* trade efficiency

Critical for scalping.

---

### 3. Volatility Delta

Measure:
Rate ATR is increasing

Real interpretation:

* explosive environment detection

---

# E. PARTICIPATION / CONFIRMATION

## Concept

“Real move vs weak move”

## Real Market Variables

### 1. Tick Volume Spike

Measure:
Current volume vs average volume

Real interpretation:

* participation surge

---

### 2. Candle Displacement

Measure:
Body size relative to wick size

Real interpretation:

* conviction

Strong displacement:
large body, small wick

---

### 3. Retest Hold

Measure:
Price retests breakout level and holds

Real interpretation:

* breakout acceptance

Optional for later stages.

Do NOT over-prioritize now.

---

# 4. CORE EXECUTION ENGINE STRUCTURE

The execution engine should remain simple.

---

# PHASE 1 — MARKET SCAN

Every candle:
calculate:

* compression state
* breakout state
* momentum state
* volatility state

---

# PHASE 2 — STATE TRANSITION DETECTION

Detect:
Compression → Expansion

This is the key transition.

---

# PHASE 3 — EXECUTION TRIGGER

Entry occurs when:

## Minimal Conditions

* compression exists
* breakout occurs
* momentum confirms
* volatility expands

That’s enough for discovery phase.

---

# PHASE 4 — TRADE MANAGEMENT

Keep basic:

* SL
* TP
* optional trailing

No advanced logic yet.

---

# PHASE 5 — LOGGING ENGINE

Most important component.

---

# 5. THE MOST IMPORTANT COMPONENT: DATA LOGGING

Without logs:
there is no research.

Every trade should log:

## MARKET STRUCTURE

* range size
* breakout direction
* session
* compression score

---

## VOLATILITY

* ATR before breakout
* ATR after breakout
* BB width
* volatility delta

---

## MOMENTUM

* RSI state
* MACD histogram value
* EMA slope

---

## EXECUTION

* spread
* slippage
* entry latency
* RR achieved

---

## OUTCOME

* win/loss
* max favorable excursion
* max adverse excursion
* continuation distance
* failure type

---

# 6. WHAT YOU SHOULD ACTUALLY ANALYZE

NOT:
“Did the trade win?”

Instead:

# Why did it behave the way it behaved?

Analyze:

* which compressions produce strongest expansions
* which sessions produce best continuation
* which breakout types fail most
* which ATR states create noise
* how spread impacts expectancy
* where continuation collapses

---

# 7. REAL EDGE DISCOVERY GOALS

You are trying to discover:

## A. Which compressions matter most

Not all squeezes are equal.

---

## B. Which breakouts sustain momentum

Many breakouts are liquidity grabs.

---

## C. Which volatility states produce continuation

Some expansions immediately exhaust.

---

## D. Which sessions amplify edge

London/NY may dominate.

---

## E. Which failure patterns repeat

False breakout behavior is valuable data.

---

# 8. SUGGESTED INITIAL EXECUTION MODEL

Keep it lightweight.

---

# ENTRY

LONG:

* compression score high
* breakout above range
* ATR expanding
* RSI > 50
* MACD histogram increasing

SHORT:
inverse logic

---

# EXIT

Simple:

* fixed RR
  or
* ATR-based TP/SL

No advanced management yet.

---

# 9. WHAT SHOULD BE AVOIDED RIGHT NOW

Avoid:

* AI prediction layers
* deep multi-timeframe logic
* heavy filters
* news avoidance systems
* complex smart money logic
* excessive confirmations
* portfolio balancing
* adaptive optimization

These belong later.

---

# 10. WHAT THIS ENGINE REALLY IS

This is not yet:

* a production trading bot

This is:

# A Quantitative Market Behavior Research Engine

The purpose is:

* detect persistent expansion behavior
* expose repeatable patterns
* measure continuation quality
* identify structural edge

Profitability comes AFTER:

* behavior understanding
* statistical validation
* regime analysis
* execution refinement

Right now:

* frequency
* consistency
* clean measurements
* behavioral visibility

matter more than optimization.




note:
Quant Research Workflow
Professional system development often follows this order:

Stage 1 — Edge Discovery
Questions:
What market behavior exists?
Is it persistent?
Is it statistically repeatable?
Is it structurally explainable?
This is where your document sits.

Stage 2 — Signal Extraction
Questions:
How do we detect the edge?
Which indicators approximate it best?
Which structures confirm it?
This is your current stack research phase.

Stage 3 — Execution Engineering
Questions:
How do we enter efficiently?
How do spreads/slippage affect expectancy?
Which timeframe is optimal?

Stage 4 — Risk Architecture
Questions:
Position sizing?
Exposure?
Drawdown limits?
Volatility adaptation?
Correlation handling?

Stage 5 — Regime Adaptation
Questions:
When should the system activate?
When should it stand down?
Which edge works in which condition?

Stage 6 — Portfolio Layer
Questions:
Can multiple edges coexist?
Can systems hedge each other?
How do we smooth equity curves?


Focus on just execution engine and edge discovery 
# Edge Discovery & Execution Engine — Phase 1 Specification

## Momentum + Breakout + Volatility Expansion EA

This specification is intentionally:

* lightweight
* measurable
* high-frequency
* statistically useful

The purpose is:

* expose the edge
* generate large datasets
* isolate persistent behaviors

NOT:

* maximize Sharpe
* minimize DD
* optimize precision

---

# 1. CORE SCORE FORMULAS

All scores normalized:

* 0 → 100

This creates:

* consistent machine interpretation
* comparable market states
* future adaptability

---

# A. CompressionScore

Purpose:
Measure volatility suppression + structural coiling.

---

## Components

### 1. Bollinger Width Compression (35%)

Formula:

[
BBWidth = UpperBB - LowerBB
]

[
BBCompression = 1 - \frac{CurrentBBWidth}{AverageBBWidth_{20}}
]

Normalized:

* negative values clamped to 0
* values >1 clamped to 1

---

### 2. ATR Compression (30%)

[
ATRCompression = 1 - \frac{ATR(14)}{ATR_SMA(20)}
]

Clamp:
0 → 1

---

### 3. Range Compression (25%)

[
RangeCompression = 1 - \frac{Range_{10}}{AverageRange_{20}}
]

Where:

[
Range_{10} = HighestHigh(10) - LowestLow(10)
]

---

### 4. Candle Body Compression (10%)

[
BodyCompression = 1 - \frac{AvgBody_{5}}{AvgBody_{20}}
]

---

# Final CompressionScore

[
CompressionScore =
(BBCompression \times 35)
+
(ATRCompression \times 30)
+
(RangeCompression \times 25)
+
(BodyCompression \times 10)
]

---

# Entry Threshold

[
CompressionScore \ge 65
]

Aggressive enough for:

* higher frequency
* useful research density

---

# B. BreakoutScore

Purpose:
Measure breakout quality and expansion strength.

---

## Components

### 1. Breakout Distance (35%)

ATR-relative.

[
BreakoutDistance =
\frac{Close - RangeHigh}{ATR(14)}
]

For shorts:

[
\frac{RangeLow - Close}{ATR(14)}
]

Normalized:

0 ATR → 0 score
1 ATR → 100 score

Capped at 100.

---

### 2. Candle Expansion (30%)

[
CandleExpansion =
\frac{CurrentCandleRange}{AverageRange_{20}}
]

---

### 3. Candle Body Dominance (20%)

[
BodyDominance =
\frac{|Close - Open|}{High - Low}
]

Measures displacement efficiency.

---

### 4. Velocity (15%)

[
Velocity =
\frac{|Close - Close_{3}|}{ATR(14)}
]

---

# Final BreakoutScore

[
BreakoutScore =
(BreakoutDistance \times 35)
+
(CandleExpansion \times 30)
+
(BodyDominance \times 20)
+
(Velocity \times 15)
]

---

# Entry Threshold

[
BreakoutScore \ge 60
]

---

# C. MomentumScore

Purpose:
Measure continuation probability.

---

## Components

### 1. EMA Alignment (35%)

LONG:

* EMA20 > EMA50

SHORT:

* EMA20 < EMA50

Scoring:

* aligned = 100
* not aligned = 0

---

### 2. RSI Directional Bias (25%)

LONG:

[
RSI = \frac{RSI(14)-50}{20}
]

SHORT:
inverse.

Clamp:
0 → 1

---

### 3. MACD Histogram Expansion (25%)

[
MACDExpansion =
\frac{HistCurrent - HistPrev}{ATR(14)}
]

---

### 4. Consecutive Directional Closes (15%)

[
DirectionalPersistence =
\frac{DirectionalCloses_{3}}{3}
]

---

# Final MomentumScore

[
MomentumScore =
(EMAAlignment \times 35)
+
(RSIBias \times 25)
+
(MACDExpansion \times 25)
+
(DirectionalPersistence \times 15)
]

---

# Entry Threshold

[
MomentumScore \ge 55
]

Slightly looser for:

* increased sampling
* avoiding overfiltering

---

# D. VolatilityScore

Purpose:
Confirm expansion phase activation.

---

## Components

### 1. ATR Expansion (50%)

[
ATRExpansion =
\frac{ATR(14)}{ATR_SMA(20)}
]

---

### 2. Volatility Delta (30%)

[
VolDelta =
ATR(14) - ATR(14)_{5barsAgo}
]

---

### 3. Spread Efficiency (20%)

[
SpreadEfficiency =
1 - \frac{Spread}{ATR(14)}
]

---

# Final VolatilityScore

[
VolatilityScore =
(ATRExpansion \times 50)
+
(VolDelta \times 30)
+
(SpreadEfficiency \times 20)
]

---

# Entry Threshold

[
VolatilityScore \ge 50
]

---

# 2. LOOKBACK WINDOWS

| Component                | Value     |
| ------------------------ | --------- |
| Bollinger Bands          | 20 period |
| BB StdDev                | 2.0       |
| ATR                      | 14        |
| ATR Average              | 20        |
| Range Compression Window | 10        |
| Avg Range Window         | 20        |
| EMA Fast                 | 20        |
| EMA Slow                 | 50        |
| RSI                      | 14        |
| MACD                     | 12/26/9   |
| Velocity Window          | 3 candles |
| Body Compression Fast    | 5         |
| Body Compression Slow    | 20        |

---

# 3. VALID BREAKOUT DEFINITION

A breakout is valid ONLY if:

## LONG

### Structural Break

[
Close > HighestHigh(10)
]

NOT wick-only.

Must CLOSE beyond range.

---

### Minimum Breakout Distance

[
BreakoutDistance \ge 0.20 \times ATR(14)
]

---

### Minimum Candle Body %

[
BodyDominance \ge 0.60
]

Meaning:
body ≥ 60% of total candle.

Rejects:

* weak spikes
* wick sweeps

---

# SHORT

Inverse logic.

---

# 4. BREAKOUT DISTANCE MODEL

Use BOTH:

* ATR-relative
* absolute minimum pip filter

---

# Primary Metric

ATR-relative.

Because:

* cross-symbol normalization
* regime adaptation

---

# Minimum Absolute Threshold

To avoid micro-noise:

## Forex

* minimum 3 pips

## Indices

* symbol-specific minimum tick threshold

---

# 5. MARKET STATE MACHINE

---

# STATE A — COMPRESSION

Conditions:

* CompressionScore ≥ 65
* ATR below ATR average
* range contraction active

Exit A when:

* breakout detected

---

# STATE B — EXPANSION TRIGGER

Conditions:

* valid breakout
* BreakoutScore ≥ 60
* VolatilityScore ≥ 50

Entry occurs here.

Exit B when:

* MomentumScore confirms continuation

---

# STATE C — MOMENTUM CONTINUATION

Conditions:

* MomentumScore ≥ 55
* EMA alignment active
* ATR expansion sustained

Remain until:

* momentum decay

---

# STATE D — EXHAUSTION

Triggered when ANY:

[
ATR(14) < ATR(14)_{3barsAgo}
]

OR

[
MACDHistogram shrinking 3 consecutive bars
]

OR

[
2 opposite candles > 70% body dominance
]

Return to:

* neutral
  or
* compression state

---

# 6. TRADE DISQUALIFIERS

Even if scores pass:

Reject trade if:

---

## Spread Too High

[
Spread / ATR > 0.15
]

Critical for scalping.

---

## Slippage Too High

Reject if:

### Forex

> 1.5 pips

### Indices

> 20% of ATR

---

## Latency Too High

Reject if:
execution latency > 250ms

---

## Candle Too Extended

Reject if:
breakout candle > 2.5 ATR

Avoid late expansion chasing.

---

# 7. SESSION RULES

---

# Allowed Sessions

## London Open

07:00–11:00 UTC

---

## NY Open

13:00–16:00 UTC

---

# Overlap

Strong priority.

---

# Asian Session

NOT fully blocked.

Reason:
discovery requires data.

But:

Asian trades tagged separately.

Later analysis decides viability.

---

# 8. NEWS FILTER

For discovery phase:

## Minimal protection only.

Block:

* 5 minutes before
* 5 minutes after

high-impact news only.

Reason:
avoid unusable spike noise.

NOT optimization.

---

# 9. POSITION LIMITS (let's mak this flexible since we are loking to discover edges we need high trades for dats)

---

## Per Symbol

Max:
2 positions

---

## Total Account

Max:
6 positions

---

# Pyramiding

DISABLED in discovery.

Need clean isolated trade behavior.

---

# 10. RISK GUARDRAILS (also make flexible, we are testing with demo so no real monarty rsik)

---

## Risk Per Trade

0.5%

---

## Daily Loss Limit

3%

---

## Consecutive Loss Halt

5 losses

Cooldown:
2 hours

---

## Max Daily Trades

40

Need statistical density.

---

# 11. POSITION SIZING

Use:

# Fixed Risk %

NOT fixed lot.

Formula:

[
LotSize =
\frac{RiskAmount}{SLDistance \times TickValue}
]

---

# 12. EXIT MODEL — PHASE 1

Use:

# ATR-based SL + Fixed RR

---

## Stop Loss

[
SL = 1.2 \times ATR(14)
]

---

## Take Profit

Primary test set:

### RR Set A

1:1.5

### RR Set B

1:2.0

Run parallel research.

---

# Time Exit

Force close after:
20 candles

if neither TP nor SL hit.

Prevents dead trades.

---

# 13. TRAILING STOP

DISABLED initially.

Need clean expectancy measurement first.

---

# 14. LATE EXPANSION ENTRY DEFINITION

Log as:
LateExpansionEntry

If:

[
DistanceFromBreakout > 1.5 \times ATR(14)
]

OR

3 consecutive expansion candles already occurred.

---

# 15. FAILURE TAXONOMY ENUMS

Mandatory labels:

* FakeBreakout
* NoContinuation
* VolatilityCollapse
* SpreadInefficiency
* LateExpansion
* LiquidityWhipsaw
* NewsShock
* MomentumFailure
* SessionDrift
* ATRExhaustion
* SlippageFailure
* RangeReentry

---

# 16. FAILURE LABEL ASSIGNMENT RULES

---

## FakeBreakout

Price re-enters range within 3 candles.

---

## NoContinuation

MFE < 0.5R

---

## VolatilityCollapse

ATR falls below breakout ATR within 5 candles.

---

## MomentumFailure

MomentumScore drops below 40 within 3 candles.

---

## ATRExhaustion

Expansion candle > 2.5 ATR then reversal.

---

# 17. MINIMUM SAMPLE SIZE

Before conclusions:

## Per regime:

minimum 100 trades

Prefer:
300+

---

# 18. PRIMARY ANALYSIS SEGMENTS

Segment by:

* session
* ATR regime
* spread regime
* breakout direction
* breakout strength
* compression strength
* symbol
* timeframe
* volatility state

---

# 19. INSTRUMENT SCOPE (note, the ea is built on one symbol, i woudl maanaul select the pairs when testing)

Phase 1:

## Forex

* EURUSD
* GBPUSD
* USDJPY

## Indices

* NAS100
* US30
* GER40

## Metals

* XAUUSD

---

# Parameters

Shared core logic.

Minor symbol overrides allowed later.

---

# 20. TIMEFRAME SCOPE (i would select when testing, but M!, M5)

Primary:

# M5

Secondary:

# M1

Separate models/logs.

Do NOT merge behaviors initially.

---

# 21. RETEST CONFIRMATION

STRICTLY DISABLED in Phase 1.

Reason:

* reduces frequency
* hides breakout behavior
* delays edge discovery

Introduce later via:
A/B testing.

---

# 22. DISCOVERY → VALIDATION CRITERIA

Graduate only if:

Edge persists across:

* symbols
* sessions
* volatility regimes

WITHOUT heavy filtering.

---

# 23. REQUIRED VALIDATION METRICS

Mandatory:

---

## Expectancy

Positive net expectancy.

---

## Profit Factor

Target:

> 1.2 minimum

---

## MAE/MFE Stability

Continuation behavior consistent.

---

## Session Stability

Not dependent on one tiny window.

---

## Failure Consistency

Losses explainable structurally.

---

## Trade Count

Minimum:
1000+ total trades

---

## Regime Robustness

Edge survives:

* low volatility
* medium volatility
* high volatility

---

# FINAL DESIGN PRINCIPLE

This engine is NOT trying to:

* predict markets perfectly

It is trying to:

# Systematically observe and exploit volatility expansion behavior at scale.

That is the correct philosophy for professional edge discovery.
