# Legacy Workbook Provenance

The original macro-enabled workbook (`OBT_VIX_MOVE.25.05.xlsm`) was
**reverse-engineered and then removed from version control**. Binaries with VBA
macros are intentionally not shipped: they bloat clones, trigger security warnings,
and redistribute third-party material. The audited logic lives on as extracted text
in `vba_legacy/` and as the Python engine in `b3_vix/`.

| Item | Detail |
|---|---|
| Original file | `OBT_VIX_MOVE.25.05.xlsm` (~4.7 MB) |
| Sanitized copy (removed) | `excel_legacy/b3_vixbova_volatility_engine_legacy.xlsm` |
| Sheets | `VIXBOVA`, `VIXBOVA_NEXT` (30-day index), `Forward N&S` (variance strip), `GARCH`, `Curva` (DI curve), `GBM`, `TELA`, `Base de Dados GBM`, `CALLVOL`/`PUTVOL`, `RRVOL`, `VXOWZ`, `historico`, `tstat2`, `Feriados` |
| VBA | `BlackScholes_NewtonRaphson.bas`, `RTD_Formula_Manager.bas`, `Market_Recorder_AxesScaler.bas`, `Data_Scheduler_Cron.bas`, `ExportarGrafico_HD.bas`, `Servidor1_RTD_Selector.frm` |

## What the workbook got wrong (fixed in Python)

- `VIXBOVA!J14:J15`: rate-squared exponent counting time twice + 356-day base; correct CBOE form is `exp(R·T)` with `T = calendar_days/365`.
- `VIXBOVA!J16`: `ROUNDDOWN` is not CBOE `K0` (must be max strike ≤ F via grid lookup).
- `VIXBOVA!J20`: single-tenor print, no 30-day `T1/T2` interpolation (Python `calculate_vixbova` blends both terms on a unified calendar basis).
- `GARCH!D:F`: no demeaning (`ε² = (r-μ)²`), no `α+β<1` constraint (Python enforces both).
- Legacy `ImpliedVolatility` VBA exited on the derivative instead of price error (fixed version archived in `vba_legacy/`).

## Runtime note

The engine prices from user-supplied or exchange chains via `connectors/`; no legacy
binary is required to run or test this repo.
