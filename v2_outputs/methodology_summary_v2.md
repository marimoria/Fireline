# FIRELINE DSA Baseline v2 — Methodology Summary

## Output decision

Checkpoint 1 uses a data-informed low-fidelity dashboard exported from Python. It is not a live BI dashboard.

## Verified data facts

- Raw observations: 61,583
- Used observations after minimal validity checks: 61,583
- Date range: 2024-08-01 to 2026-05-31
- Unique 0.1-degree grids: 2,954
- Grid-date rows: 27,411
- Historical peak: 2024-09-03 with 2,400 observations
- Grids without province boundary label: 180

## Feature engineering

Activity, trailing-seven-day persistence, FRP summary, nearest-school distance, province boundary label, confidence/day-night context, provisional priority score, reason, and quality status.

## Guardrails

No date-shifted climate correlation, predictive model, official risk category, peat-fire inference from night observation alone, or automatic response recommendation is included.
