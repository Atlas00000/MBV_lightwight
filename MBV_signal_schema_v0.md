# MBV signal log schema v0.2

CSV files produced by `MBV_Log.mqh` (Milestone 1). Delimiter: **comma** (`FILE_CSV`). Encoding: **ANSI** (MetaTrader default).

## Files

| File pattern | Purpose |
|--------------|---------|
| `MBV_sig_<Symbol>_<YYYY.MM.DD>.csv` | Signal rows (`SIGNAL`) and optional boot row |
| Same file, rows with `event=OUTCOME` | Trade close outcomes (MFE/MAE in account currency, approximate) |

`Symbol` has non-alphanumeric stripped for filenames.

## QA checklist (P0)

Use before relying on logs for ML or reporting.

1. **`BOOT` row** — Present once when the daily file is created; `ea_version` matches `#property version` on the EA.
2. **`SIGNAL` ↔ `OUTCOME` join** — For each fill, find `SIGNAL` with `executed=1` and non-empty `signal_id`; the closing leg should have **`OUTCOME.signal_id`** equal to that id (from order comment). Check `pos_id` / `exit_deal_ticket` against the tester journal if needed.
3. **`skip=1` / `skip=4`** — From **MBV v4.35+**, rows logged for spread or cooldown should still have **shift-1 OHLC and indicators** filled (not all zeros), unless `skip=7` (insufficient bars).
4. **Schema version** — Column `schema` is `0.1` until a breaking column change; bump schema when columns change.

## `event` column

| Value | Meaning |
|-------|---------|
| `BOOT` | Written once when a new log file is opened (EA version, magic). |
| `SIGNAL` | One row per logged evaluation (see logging mode inputs). |
| `OUTCOME` | Position closed; includes `signal_id` from opening deal comment. |

## `skip_reason` (integer)

| Code | Meaning |
|------|---------|
| 0 | No skip / order attempted successfully (`executed=1`). |
| 1 | Spread too high (`InpMaxSpreadPoints`). |
| 2 | ADX above cap (`InpMaxAdx`). |
| 3 | Trend filter blocked a direction that was still alive after long-only rules (see notes). |
| 4 | Cooldown (`InpMinBarsSinceEntry`). |
| 5 | Max open positions (`InpMaxPos`). |
| 6 | Both buy and sell final intent (conflict). |
| 7 | Insufficient bars on chart. |
| 8 | Indicator buffer read failed. |
| 9 | Reserved — AI block (future). |
| 10 | No raw signal (touch+RSI did not arm either side). |
| 14 | Long-only extras removed a buy that was armed at `raw_buy` (`InpLongRequire*` / DI). |
| 15 | `OrderSend` failed (`ord_retcode` in `ord_ret`). |

**Notes (v4.35):** If both trend and long-only apply to the same “no trade” bar, **`skip=3` is preferred** when trend blocked a side that had passed long-only filters; **`skip=14`** when the buy was dropped only by long-only rules.

## Header ↔ schema names (same file)

| CSV header | Schema / docs name |
|------------|-------------------|
| `bb_u`, `bb_m`, `bb_l` | bb_upper, bb_middle, bb_lower |
| `pdi`, `mdi` | plus_di, minus_di |
| `trend_c`, `trend_ema` | trend_close, trend_ema |
| `spread` | spread_points |
| `touch_b`, `touch_s` | touch_buy, touch_sell |
| `raw_b`, `raw_s` | raw_buy, raw_sell |
| `fin_b`, `fin_s` | fin_buy, fin_sell |
| `skip` | skip_reason |
| `ord_ret` | ord_retcode |
| `dur_s` | duration_sec |
| `xdeal` | exit_deal_ticket |

## `ord_ret` when `skip=15` (P3)

Common MetaTrader 5 `TRADE_RETCODE` values seen in testing:

| Value | Constant (typical) | Meaning |
|-------|-------------------|---------|
| 10016 | `TRADE_RETCODE_INVALID_STOPS` | SL/TP violate stops/freeze or broker rules. |
| 10018 | `TRADE_RETCODE_MARKET_CLOSED` | Session / market closed for the symbol. |

Other retcodes are possible; always store the numeric `ord_ret` from `CTrade::ResultRetcode()`.

## SIGNAL columns (v0.1 file layout)

| Column | Type | Notes |
|--------|------|--------|
| event | text | `SIGNAL` |
| signal_id | text | Unique per attempted send; empty if not executed. |
| ea_version | text | `#property version` |
| bar_time | datetime | Time of **signal bar** (`iTime(InpTF,1)` when available else 0). |
| symbol | text | |
| chart_tf | text | `EnumToString(InpTF)` |
| o,h,l,c | double | M5 bar **shift 1** OHLC |
| bb_upper,bb_middle,bb_lower | double | Bands shift 1 (headers `bb_u`, `bb_m`, `bb_l`) |
| rsi | double | Shift 1 |
| atr | double | Shift 1 |
| adx,plus_di,minus_di | double | Shift 1 (`pdi`, `mdi` in CSV) |
| trend_close,trend_ema | double | `InpTrendTF` shift 1 |
| spread_points | int | (`spread` in CSV) |
| touch_buy,touch_sell | int | 0/1 |
| raw_buy,raw_sell | int | After touch + RSI |
| fin_buy,fin_sell | int | After long extras + trend |
| executed | int | 1 if market order succeeded |
| skip_reason | int | |
| ord_retcode | int | `TRADE_RETCODE` on failure; else 0 |
| side | text | `BUY` / `SELL` / `NONE` — final intent |
| pnl,dur_s,mfe,mae,pos_id,xdeal | varies | See `MBV_Log.mqh`; outcome fields zero on `SIGNAL` |
| schema | text | e.g. `0.1` |

## OUTCOME columns (v0.1)

| Column | Type | Notes |
|--------|------|--------|
| event | text | `OUTCOME` |
| signal_id | text | Parsed from position / deal comment |
| position_id | ulong | `DEAL_POSITION_ID` (`pos_id` in CSV) |
| pnl | double | Deal profit + swap + commission (close leg) |
| duration_sec | int | Approximate open→close (`dur_s`) |
| mfe_money | double | Max floating profit while tracked (`mfe`) |
| mae_money | double | Worst floating drawdown while tracked (`mae`) |
| exit_deal_ticket | ulong | (`xdeal`) |

## Lookahead policy

All features use **completed bar** or shift **≥ 1** indicators, aligned with `InpNewBarOnly` evaluation.

## Changelog

| Version | Change |
|---------|--------|
| v0.1 | Initial schema for MBV v4.32+ logging milestone |
| v0.2 | QA checklist; header map; `ord_ret` table; skip 3/14 notes; MBV v4.35 logging order |
