# AquaGuard AI

**Explainable water anomaly detection and demand planning for university campuses**

Prepared by **Farid Ahmad Khan** · Xylem Global Student Innovation Challenge 2026  
Track: **#1 Water Quantity – University Track**

A software-first prototype that turns CSV meter readings into understandable water-use information. It includes per-meter anomaly screening, explainable candidate events, a seven-day baseline forecast, response-delay scenario simulation, and synthetic-benchmark evaluation.

## Features

- Interactive Streamlit dashboard for campus and meter consumption.
- CSV import with timestamp, meter ID and volume validation; duplicate handling.
- Explainable high-side anomaly screening using a trailing rolling median and robust MAD scale.
- Grouping of consecutive flags into candidate events with estimated excess volume and review priority.
- Seven-day weekday-aware forecast: 70% recent same-weekday median + 30% recent 14-day median.
- Transparent response-delay calculator.
- TP, FP, FN, TN, precision, recall and F1 on the included synthetic benchmark.
- CSV export and automated core tests.

## Quick start (Windows / VS Code)

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Run the application:

   ```powershell
   streamlit run app.py
   ```

6. Open the local URL printed by Streamlit (normally `http://localhost:8501`).

## Run tests

```powershell
pytest -q
```

## CSV format

Required columns:

| Column | Meaning | Example |
|---|---|---|
| `timestamp` | Date/time of interval reading | `2026-10-01 00:00:00` |
| `meter_id` | Stable meter identifier | `Academic Block` |
| `volume_l` | Water volume in litres for that interval | `5.7` |

Each row represents the volume measured during one interval, not a cumulative meter counter. Timestamps should be consistent and ideally spaced 15 minutes apart. The prototype does not currently resample irregular intervals or infer units.

## Demonstration dataset

The reproducible demo generator creates five virtual meters over 28 days at 15-minute intervals: **13,440 readings**. It injects a few controlled high-flow events and retains synthetic ground-truth labels for evaluation. The dataset is not from a real university.

A copy is included at `data/demo_readings.csv`.

## Methods and transparency

### Anomaly screening

For each meter, AquaGuard AI calculates a trailing rolling median that excludes the current reading. Robust variability is estimated from the median absolute deviation (MAD), scaled by 1.4826. A reading is flagged when:

`observed > expected baseline + k × robust scale`

and its excess over baseline is at least the configured minimum. Consecutive flags are grouped into candidate events. This is an anomaly-screening mechanism, **not a leak classifier**. It may produce false positives and false negatives. The optional Isolation Forest described in the presentation is not enabled in this release; the core prototype uses the explainable robust detector.

### Forecasting

Daily campus totals are forecast seven days ahead with a weekday-aware baseline: 70% recent median for the same weekday and 30% recent 14-day median. Rolling-origin holdout MAE is shown as a descriptive measure for this sample history. Weather, occupancy, holidays and academic calendars are not modelled.

### Scenario simulator

`estimated water loss = assumed excess flow rate × response delay`

This is a hypothetical calculation. For example, 25 L/hour × 48 hours = 1,200 L; with an 8-hour response delay, the estimate is 200 L, so the scenario difference is 1,000 L.

## Limitations and responsible use

- Synthetic data only; no physical sensors, field deployment or measured water savings.
- A flagged reading is a candidate event and must be checked by authorized facilities staff.
- Forecast quality is limited by the short synthetic history and omitted external factors.
- Uploaded data without ground-truth labels is not assigned invented accuracy metrics.
- Before production use, add authentication, authorization, audit logs, secure storage, monitoring, backups, and security review.
- Validate units, intervals, meter behavior and alert thresholds during an authorized campus pilot.

## Project structure

```text
AquaGuard_AI/
├── app.py
├── aquaguard/
│   ├── data.py
│   ├── detector.py
│   ├── evaluation.py
│   ├── forecast.py
│   ├── simulator.py
│   └── validation.py
├── data/demo_readings.csv
├── tests/test_core.py
├── requirements.txt
└── README.md
```

## Suggested 3-minute narrated demo

1. **0:00–0:25 — Problem:** Explain that periodic readings and monthly bills can hide unusual campus water use.
2. **0:25–0:55 — Overview:** Open the dashboard and show five meters, daily consumption and total readings.
3. **0:55–1:30 — Anomaly review:** Show candidate flags, expected baseline, excess volume and grouped events. State that flags are not confirmed leaks.
4. **1:30–1:55 — Forecast:** Show the next seven days and explain the 70/30 weekday-aware baseline.
5. **1:55–2:20 — Simulator:** Enter 25 L/hour, 48 hours and 8 hours; show 1,200 L, 200 L and 1,000 L potential difference.
6. **2:20–2:45 — Evaluation/data:** Show synthetic benchmark metrics and CSV upload/export.
7. **2:45–3:00 — Close:** Explain the next step: an authorized pilot with real meter data and inspection-confirmed events.

## Author

**Farid Ahmad Khan**  
Student, Kabul University  
