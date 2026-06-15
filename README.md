# 🛡️ Solvency II Stress Test Simulator

An interactive simulator that models the impact of market shocks on an insurance company's capital adequacy under the **Solvency II** regulatory framework (EU Directive 2009/138/EC).

Built with Python & Streamlit as a self-directed finance & coding project.

---

## What It Does

The tool lets you apply three simultaneous market stress scenarios — interest rate shifts, equity crashes, and credit spread widening — and instantly see how they affect:

- **Eligible Own Funds** (stressed)
- **Solvency Capital Requirement** (SCR) build-up
- **Solvency Ratio** (Own Funds / SCR)
- **Capital buffer** vs the regulatory minimum

Results update in real time as you adjust the shock parameters, with a dynamic written interpretation that changes based on whether the company is well-capitalised, under stress, or in regulatory breach.

---

## Features

### Market Shock Modules
| Module | Parameter | Range |
|---|---|---|
| Interest Rate Risk | Parallel yield curve shift | −300 to +300 bps |
| Equity Risk | Instantaneous market fall | −50% to −10% |
| Credit Spread Risk | Corporate spread widening | 0 to +200 bps |

### Outputs
- **Solvency gauge** — colour-coded (green / amber / red) against the 100% and 150% thresholds
- **Capital summary cards** — stressed own funds, total SCR, solvency ratio, capital buffer
- **SCR decomposition table** — shock-by-shock breakdown with P&L impact and cumulative SCR
- **Waterfall chart** — visual build-up from base SCR to total stressed SCR
- **Dynamic narrative** — auto-generated regulatory interpretation with management action guidance

### Sidebar Reference
Built-in Solvency II primer covering:
- What Solvency II is and who it applies to
- How the SCR is calculated (1-in-200 year VaR)
- Solvency ratio thresholds and regulatory consequences
- Market stress sub-module methodology (interest rate, equity, spread)

---

## Tech Stack

- **Python 3.x**
- **Streamlit** — interactive web app
- **Plotly** — gauge chart and waterfall chart
- **Pandas** — SCR decomposition table with conditional styling

---

## How to Run

**1. Install dependencies**
```bash
pip install streamlit plotly pandas
```

**2. Run the app**
```bash
streamlit run solvency_stress_test.py
```

**3. Adjust the sliders**

Use the three sliders to set your stress scenario. All outputs update instantly.

---

## Model Methodology

This simulator uses a **simplified standard formula** approach for educational purposes.

| Component | Methodology |
|---|---|
| Interest rate impact | Net duration mismatch × rate shock × liability pool |
| Equity impact | Direct markdown of equity portfolio value |
| Credit spread impact | Spread DV01 × spread duration × credit portfolio |
| SCR add-ons | IR: 60% of P&L hit · Equity: 1:1 · Credit: 75% haircut |
| Own funds (stressed) | Base own funds + sum of all P&L impacts |
| Solvency ratio | Stressed own funds / Total stressed SCR × 100 |

**Solvency ratio thresholds:**
- **≥ 150%** → Well-capitalised (management comfort zone)
- **100–150%** → Under stress (supervisory scrutiny likely)
- **< 100%** → SCR breach (regulatory intervention required)

> ⚠️ This tool uses illustrative sensitivities for educational purposes only. It does not constitute regulatory reporting or actuarial advice.

---

## Regulatory Context

Solvency II is the EU prudential framework for insurance companies, in force since January 2016. The SCR represents the capital needed to survive a **1-in-200 year** stress event (99.5% VaR over one year), covering market risk, underwriting risk, counterparty risk, and operational risk. Sub-modules are aggregated using a correlation matrix to give diversification credit.

---

## Author

**Khai Tran** — BBA student at KU Leuven  
[GitHub](https://github.com/KhaiTranKUL)
