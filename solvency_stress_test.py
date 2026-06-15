import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solvency II Stress Test",
    page_icon="🛡️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(90deg, #1a3a5c, #2e86c1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle { color: #5d6d7e; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .metric-card {
        background: #f8f9fa; border-radius: 10px;
        padding: 1rem 1.2rem; border-left: 4px solid #2e86c1;
        margin-bottom: 0.8rem;
    }
    .metric-card h4 { margin: 0; font-size: 0.8rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card p  { margin: 0; font-size: 1.6rem; font-weight: 700; color: #1a3a5c; }
    .interp-box {
        border-radius: 10px; padding: 1rem 1.4rem;
        font-size: 0.95rem; font-weight: 500; line-height: 1.6;
    }
    .green  { background:#eafaf1; border-left:4px solid #27ae60; color:#1e8449; }
    .amber  { background:#fef9e7; border-left:4px solid #f39c12; color:#b7770d; }
    .red    { background:#fdedec; border-left:4px solid #e74c3c; color:#c0392b; }
    .sidebar-section { background:#f0f4f8; border-radius:8px; padding:0.8rem 1rem; margin-bottom:1rem; }
    .sidebar-section h4 { color:#1a3a5c; margin-top:0; font-size:0.9rem; }
    .sidebar-section p, .sidebar-section li { color:#4a5568; font-size:0.82rem; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar – Solvency II explainer ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📘 Solvency II Primer")

    st.markdown("""
    <div class="sidebar-section">
    <h4>🏛️ What is Solvency II?</h4>
    <p>Solvency II is the EU prudential regulatory framework for insurance companies, 
    in force since 2016. It is risk-based: capital requirements scale with the 
    actual risks an insurer faces.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
    <h4>📐 Solvency Capital Requirement (SCR)</h4>
    <p>The SCR is the amount of capital needed to survive a <b>1-in-200 year</b> stress 
    event (99.5% VaR over one year). It covers:</p>
    <ul>
        <li><b>Market risk</b> – interest rates, equities, credit spreads, FX</li>
        <li><b>Underwriting risk</b> – mortality, longevity, P&C catastrophes</li>
        <li><b>Counterparty risk</b> – reinsurance, bank deposits</li>
        <li><b>Operational risk</b>  – internal process failures</li>
    </ul>
    <p>Sub-modules are aggregated using a <b>correlation matrix</b> (not simple addition), 
    giving diversification credit.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
    <h4>📊 Solvency Ratio</h4>
    <p><b>Solvency Ratio = Eligible Own Funds / SCR</b></p>
    <ul>
        <li><b>> 150 %</b> → Well-capitalised (regulatory comfort zone)</li>
        <li><b>100–150 %</b> → Under stress; supervisor attention</li>
        <li><b>&lt; 100 %</b> → Breach; regulatory intervention likely</li>
    </ul>
    <p>EIOPA guidelines recommend companies hold a <b>management buffer</b> above 100 %.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
    <h4>⚡ Market Stress Modules</h4>
    <ul>
        <li><b>Interest rate</b> – tests parallel shifts up & down on the yield curve, 
        applied to both assets (bonds) and liabilities (duration mismatch).</li>
        <li><b>Equity</b> – standard shock is −39 % (Type 1) or −49 % (Type 2); 
        symmetric adjustment applies.</li>
        <li><b>Spread</b> – widens credit spreads on corporate bonds and structured 
        products; haircut depends on rating and duration.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section">
    <h4>⚠️ Disclaimer</h4>
    <p>This tool uses <b>simplified, illustrative</b> sensitivities for educational 
    purposes. It does not constitute regulatory reporting or actuarial advice.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🛡️ Solvency II Stress Test Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulate market shocks and observe their impact on capital adequacy under the Solvency II standard formula.</div>', unsafe_allow_html=True)

# ── Base balance sheet assumptions (€m) ──────────────────────────────────────
BASE_OWN_FUNDS   = 850   # Eligible Own Funds
BASE_SCR         = 500   # Base SCR (pre-stress)
ASSET_DURATION   = 8     # years (bond portfolio average duration)
LIABILITY_DUR    = 12    # years (insurance liability duration)
BOND_PORTFOLIO   = 3_000 # market value of fixed-income assets
EQUITY_PORTFOLIO = 600   # market value of equity holdings
CREDIT_PORTFOLIO = 1_200 # corporate bond / credit exposure

# ── Sliders ───────────────────────────────────────────────────────────────────
st.markdown("### ⚙️ Market Shock Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    ir_shock_bps = st.slider(
        "📈 Interest Rate Shock (bps)",
        min_value=-300, max_value=300, value=0, step=25,
        help="Parallel shift in the risk-free yield curve. Positive = rates rise."
    )

with col2:
    eq_shock_pct = st.slider(
        "📉 Equity Shock (%)",
        min_value=-50, max_value=-10, value=-20, step=5,
        help="Instantaneous fall in equity market values."
    )

with col3:
    cs_shock_bps = st.slider(
        "💳 Credit Spread Widening (bps)",
        min_value=0, max_value=200, value=50, step=10,
        help="Widening of corporate credit spreads, reducing bond market values."
    )

st.markdown("---")

# ── Sensitivity calculations ──────────────────────────────────────────────────
# Interest rate: net duration mismatch drives P&L
# DV01 of liabilities > assets → rising rates help, falling hurt (typical life insurer)
ir_shock_decimal = ir_shock_bps / 10_000
net_duration_mismatch = LIABILITY_DUR - ASSET_DURATION          # 4 years net
liability_base       = BASE_SCR * 8                              # simplified liability pool
ir_capital_impact    = -net_duration_mismatch * ir_shock_decimal * liability_base
# Rising rates → positive for this balance sheet; falling → negative

# Equity: direct markdown of equity portfolio
eq_shock_decimal  = eq_shock_pct / 100
eq_capital_impact = eq_shock_decimal * EQUITY_PORTFOLIO          # always negative/zero

# Credit spread: spread DV01 ≈ spread_change × modified_duration × notional
# Use asset duration (bonds), average rating assumes ~6yr spread duration
SPREAD_DURATION   = 6
cs_shock_decimal  = cs_shock_bps / 10_000
cs_capital_impact = -cs_shock_decimal * SPREAD_DURATION * CREDIT_PORTFOLIO

# SCR add-ons: each shock module feeds into the SCR
# The stressed SCR includes the base SCR plus incremental capital charges
# using a simplified (no diversification for clarity) additive approach
ir_scr_addon = max(abs(ir_capital_impact) * 0.6, 0)              # capital charge ≈ 60% of P&L hit
eq_scr_addon = abs(eq_capital_impact)                            # 1:1 for equity
cs_scr_addon = abs(cs_capital_impact) * 0.75                    # haircut for recoveries

total_scr = BASE_SCR + ir_scr_addon + eq_scr_addon + cs_scr_addon

# Own funds also move with market: subtract realised P&L hits
own_funds_stressed = (
    BASE_OWN_FUNDS
    + ir_capital_impact        # could be + or −
    + eq_capital_impact        # always ≤ 0
    + cs_capital_impact        # always ≤ 0
)
own_funds_stressed = max(own_funds_stressed, 0)

solvency_ratio = (own_funds_stressed / total_scr * 100) if total_scr > 0 else 999

# ── Colour thresholds ─────────────────────────────────────────────────────────
if solvency_ratio >= 150:
    status, colour, emoji, interp_class = "Well-Capitalised", "green", "✅", "green"
elif solvency_ratio >= 100:
    status, colour, emoji, interp_class = "Under Stress", "orange", "⚠️", "amber"
else:
    status, colour, emoji, interp_class = "In Breach", "red", "🚨", "red"

gauge_color = {"green": "#27ae60", "orange": "#f39c12", "red": "#e74c3c"}[colour]

# ── Layout: gauge + metrics ────────────────────────────────────────────────────
gcol, mcol = st.columns([1.4, 1])

with gcol:
    st.markdown("#### Solvency Ratio Gauge")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=solvency_ratio,
        number={"suffix": "%", "font": {"size": 44, "color": gauge_color}},
        delta={"reference": 150, "suffix": "%",
               "increasing": {"color": "#27ae60"}, "decreasing": {"color": "#e74c3c"}},
        gauge={
            "axis": {"range": [0, 300], "tickwidth": 1,
                     "tickcolor": "#aab7c4", "ticksuffix": "%",
                     "tickvals": [0, 50, 100, 150, 200, 250, 300]},
            "bar": {"color": gauge_color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 100],   "color": "#fce8e8"},
                {"range": [100, 150], "color": "#fef9e7"},
                {"range": [150, 300], "color": "#eafaf1"},
            ],
            "threshold": {
                "line": {"color": "#1a3a5c", "width": 3},
                "thickness": 0.8,
                "value": 150,
            },
        },
        title={"text": f"{emoji} {status}", "font": {"size": 20, "color": gauge_color}},
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=30, r=30, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )
    st.plotly_chart(fig, use_container_width=True)

with mcol:
    st.markdown("#### Capital Summary")
    def card(label, value, suffix="€m"):
        return f"""<div class="metric-card"><h4>{label}</h4><p>{value:,.0f} {suffix}</p></div>"""

    st.markdown(card("Stressed Own Funds", own_funds_stressed), unsafe_allow_html=True)
    st.markdown(card("Total SCR (stressed)", total_scr), unsafe_allow_html=True)
    st.markdown(card("Solvency Ratio", solvency_ratio, suffix="%"), unsafe_allow_html=True)
    st.markdown(card("Capital Buffer vs SCR", own_funds_stressed - total_scr), unsafe_allow_html=True)

# ── Waterfall / breakdown table ────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📋 SCR Shock Decomposition")

rows = [
    {
        "Shock Module":        "Base SCR (pre-stress)",
        "Shock Applied":       "–",
        "Capital P&L Impact (€m)": 0.0,
        "SCR Add-On (€m)":    BASE_SCR,
        "Cumulative SCR (€m)": BASE_SCR,
    },
    {
        "Shock Module":        "Interest Rate Risk",
        "Shock Applied":       f"{ir_shock_bps:+d} bps",
        "Capital P&L Impact (€m)": round(ir_capital_impact, 1),
        "SCR Add-On (€m)":    round(ir_scr_addon, 1),
        "Cumulative SCR (€m)": round(BASE_SCR + ir_scr_addon, 1),
    },
    {
        "Shock Module":        "Equity Risk",
        "Shock Applied":       f"{eq_shock_pct:+d}%",
        "Capital P&L Impact (€m)": round(eq_capital_impact, 1),
        "SCR Add-On (€m)":    round(eq_scr_addon, 1),
        "Cumulative SCR (€m)": round(BASE_SCR + ir_scr_addon + eq_scr_addon, 1),
    },
    {
        "Shock Module":        "Credit Spread Risk",
        "Shock Applied":       f"+{cs_shock_bps} bps",
        "Capital P&L Impact (€m)": round(cs_capital_impact, 1),
        "SCR Add-On (€m)":    round(cs_scr_addon, 1),
        "Cumulative SCR (€m)": round(total_scr, 1),
    },
]

df = pd.DataFrame(rows)

# Style the table
def style_impact(val):
    try:
        v = float(val)
        if v < 0:   return "color: #c0392b; font-weight:600"
        elif v > 0: return "color: #1e8449; font-weight:600"
    except:
        pass
    return ""

styled = (
    df.style
      .applymap(style_impact, subset=["Capital P&L Impact (€m)"])
      .format({"Capital P&L Impact (€m)": "{:+.1f}", "SCR Add-On (€m)": "{:.1f}", "Cumulative SCR (€m)": "{:.1f}"})
      .set_properties(**{"text-align": "center"})
      .set_table_styles([
          {"selector": "th", "props": [
              ("background-color", "#1a3a5c"), ("color", "white"),
              ("font-size", "0.82rem"), ("text-align", "center"),
              ("padding", "8px 12px"),
          ]},
          {"selector": "td", "props": [("padding", "8px 12px"), ("font-size", "0.88rem")]},
          {"selector": "tr:nth-child(even)", "props": [("background-color", "#f8f9fa")]},
          {"selector": "tr:hover",            "props": [("background-color", "#eaf2ff")]},
      ])
)
st.dataframe(styled, use_container_width=True, height=210)

# ── Waterfall bar chart ────────────────────────────────────────────────────────
st.markdown("#### 📊 SCR Build-Up Waterfall")

modules     = ["Base SCR", "Interest Rate", "Equity", "Credit Spread", "Total SCR"]
add_ons     = [BASE_SCR, ir_scr_addon, eq_scr_addon, cs_scr_addon, total_scr]
measures    = ["absolute", "relative", "relative", "relative", "total"]
bar_colours = [
    "#2e86c1",
    "#27ae60" if ir_scr_addon == 0 else "#e74c3c",
    "#e74c3c",
    "#e67e22" if cs_scr_addon > 0 else "#27ae60",
    gauge_color,
]

wfig = go.Figure(go.Waterfall(
    orientation="v",
    measure=measures,
    x=modules,
    y=add_ons,
    connector={"line": {"color": "#aab7c4", "dash": "dot"}},
    decreasing={"marker": {"color": "#e74c3c"}},
    increasing={"marker": {"color": "#e74c3c"}},
    totals={"marker": {"color": gauge_color}},
    text=[f"€{v:,.0f}m" for v in add_ons],
    textposition="outside",
))
wfig.add_hline(
    y=BASE_OWN_FUNDS, line_dash="dash", line_color="#2e86c1", line_width=2,
    annotation_text=f"Stressed Own Funds: €{own_funds_stressed:,.0f}m",
    annotation_position="right",
)
wfig.update_layout(
    height=360,
    yaxis_title="€m",
    xaxis_title="",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#eaecee"),
    font={"family": "Inter, sans-serif", "size": 13},
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False,
)
st.plotly_chart(wfig, use_container_width=True)

# ── Dynamic written interpretation ────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 🗣️ Interpretation")

buffer_pct  = solvency_ratio - 100
excess_funds = own_funds_stressed - total_scr

if solvency_ratio >= 150:
    narrative = (
        f"Under these market conditions, the company is **well-capitalised** with a solvency ratio of "
        f"**{solvency_ratio:.1f}%**, comfortably exceeding the 150% management buffer. "
        f"Eligible own funds of €{own_funds_stressed:,.0f}m cover the stressed SCR of €{total_scr:,.0f}m "
        f"with a surplus of €{excess_funds:,.0f}m ({buffer_pct:.0f}pp above the 100% minimum). "
        f"The dominant driver of capital consumption is "
        f"{'equity risk' if eq_scr_addon >= max(ir_scr_addon, cs_scr_addon) else 'interest rate risk' if ir_scr_addon >= cs_scr_addon else 'credit spread risk'}. "
        f"No immediate management action is required, though continued monitoring is advisable."
    )
elif solvency_ratio >= 100:
    narrative = (
        f"Under these market conditions, the company is **under stress** with a solvency ratio of "
        f"**{solvency_ratio:.1f}%**. The ratio remains above the 100% regulatory minimum but has fallen below "
        f"the 150% management buffer, meaning supervisory scrutiny is likely. "
        f"Own funds of €{own_funds_stressed:,.0f}m cover SCR of €{total_scr:,.0f}m, leaving only "
        f"€{excess_funds:,.0f}m of capital headroom. "
        f"Management should consider capital preservation actions — reducing equity exposure, "
        f"asset-liability rebalancing, or reinsurance — to restore the buffer before conditions deteriorate further."
    )
else:
    narrative = (
        f"Under these market conditions, the company is **in breach** of the Solvency Capital Requirement "
        f"with a solvency ratio of **{solvency_ratio:.1f}%**. Eligible own funds of €{own_funds_stressed:,.0f}m "
        f"are insufficient to cover the stressed SCR of €{total_scr:,.0f}m — a shortfall of "
        f"€{abs(excess_funds):,.0f}m. "
        f"Under Solvency II, the company would be required to notify the regulator immediately and submit "
        f"a recovery plan within two months. Emergency capital raising, forced asset sales, or regulatory "
        f"intervention are probable outcomes under sustained stress of this magnitude."
    )

st.markdown(f'<div class="interp-box {interp_class}">{emoji} {narrative}</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("")
st.markdown(
    "<p style='text-align:center; color:#aab7c4; font-size:0.78rem;'>"
    "Solvency II Stress Test Simulator · Illustrative model only · Not for regulatory use"
    "</p>",
    unsafe_allow_html=True,
)
