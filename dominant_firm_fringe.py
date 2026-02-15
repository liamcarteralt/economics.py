import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 1. Page Config
st.set_page_config(
    page_title="Dominant Firm & Competitive Fringe",
    layout="wide",
)

# Custom CSS to hide default Streamlit elements for a cleaner look
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { font-family: 'IBM Plex Sans', sans-serif; font-size: 1.5rem; }
    .stSlider { padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("Dominant Firm & Competitive Fringe")

# ──────────────────────────────────────────────
# 2. THE MATH (Your Python Logic)
# ──────────────────────────────────────────────
class DFModel:
    def __init__(self, a, b, cF, dF, n, mc0, mcS, FC):
        self.a, self.b = a, b
        self.cF, self.dF, self.n = cF, dF, n
        self.mc0, self.mcS, self.FC = mc0, mcS, FC

    # Market Demand
    def market_demand_P(self, Q): return self.a - self.b * Q
    def market_demand_Q(self, P): return max(0, (self.a - P) / self.b)

    # Fringe Supply
    def fringe_supply_Q(self, P): return self.n * (P - self.cF) / self.dF if P >= self.cF else 0
    def fringe_supply_P(self, Qf): return self.cF + (self.dF * Qf) / self.n
    
    # Costs
    def mc_at(self, q): return self.mc0 + self.mcS * q
    def total_cost(self, q): return self.FC + self.mc0 * q + (self.mcS * q * q) / 2
    def atc_at(self, q): return self.total_cost(q) / q if q > 0.1 else float('inf')
    def fringe_firm_MC(self, q): return self.cF + self.dF * q
    def fringe_firm_ATC(self, q): return self.cF + self.dF * q / 2 if q > 0.1 else float('inf')

    # Residual Demand Logic
    def kink_Q(self): return max(0, (self.a - self.cF) / self.b)
    def upper_seg(self):
        d = self.dF / self.n
        A = (self.a * d + self.cF * self.b) / (self.b + d)
        B = (self.b * d) / (self.b + d)
        return A, B
    
    def residual_demand_P(self, Qd):
        Qk = self.kink_Q()
        if Qd >= Qk: return max(0, self.a - self.b * Qd)
        A, B = self.upper_seg()
        return max(0, A - B * Qd)

    def competitive_price(self):
        return (self.dF * self.a + self.n * self.b * self.cF) / (self.n * self.b + self.dF)

    def solve(self):
        Qk = self.kink_Q()
        A, B = self.upper_seg()
        
        # MC intersections for upper and lower segments
        Q1 = (A - self.mc0) / (2 * B + self.mcS) if (2 * B + self.mcS) > 0 else float("inf")
        Q2 = (self.a - self.mc0) / (2 * self.b + self.mcS) if (2 * self.b + self.mcS) > 0 else float("inf")

        if Q1 >= 0 and Q1 < Qk: Qd = Q1
        elif Q2 >= 0 and Q2 > Qk: Qd = Q2
        else: Qd = Qk
        
        Qd = max(0, Qd)
        Pd = self.residual_demand_P(Qd)
        Qf = self.fringe_supply_Q(Pd)
        qf = Qf / self.n if self.n > 0 else 0
        
        profitD = Pd * Qd - self.total_cost(Qd)
        
        # Welfare
        Qt = Qd + Qf
        CS = 0.5 * (self.a - Pd) * Qt if Qt > 0 else 0
        
        # Simple DWL calc (approximation)
        QdComp = (A - self.mc0) / (B + self.mcS) # simplified efficient Q for dominant firm
        DWL = 0 
        
        Pc = self.competitive_price()
        
        return {
            "Pd": Pd, "Qd": Qd, "Qf": Qf, "qf": qf, "Qt": Qt,
            "profitD": profitD, "CS": CS, "DWL": DWL, "Pc": Pc,
            "Qk": Qk, "A": A, "B": B
        }

# ──────────────────────────────────────────────
# 3. SIDEBAR CONTROLS
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("Market Demand")
    a = st.slider("Intercept (a)", 50, 200, 100)
    b = st.slider("Slope (b)", 0.2, 3.0, 1.0, 0.05)

    st.header("Fringe Supply")
    cF = st.slider("Min Price (cF)", 0, 80, 20)
    dF = st.slider("Slope (dF)", 0.2, 5.0, 1.5, 0.05)
    n = st.slider("Num. Firms (n)", 1, 20, 5)

    st.header("Dominant Firm")
    mc0 = st.slider("MC Base", 0, 80, 10)
    mcS = st.slider("MC Slope", 0.0, 3.0, 0.3, 0.05)
    FC = st.slider("Fixed Cost", 0, 1000, 50, 10)
    
    st.divider()
    st.caption("Visualization Options")
    show_cs = st.checkbox("Show Consumer Surplus", value=True)
    show_profit = st.checkbox("Show Dominant Profit", value=False)


# ──────────────────────────────────────────────
# 4. PLOTTING WITH PLOTLY
# ──────────────────────────────────────────────

# -- Solve --
model = DFModel(a, b, cF, dF, n, mc0, mcS, FC)
eq = model.solve()

# -- Setup Data Arrays for Smooth Curves --
MAX_Q = 120
MAX_P = 120
q_range = np.linspace(0, MAX_Q, 200)

# Colors from your HTML version
C_DEMAND = "#c62828"
C_MR = "#e65100"
C_MC_DOM = "#2e7d32"
C_MC_FRINGE = "#0277bd"
C_CS = "rgba(66, 133, 244, 0.2)"
C_PROFIT = "rgba(251, 188, 4, 0.3)"

# -- Create Figure --
fig = make_subplots(
    rows=1, cols=2, 
    shared_yaxes=True,
    subplot_titles=("Fringe Firm (Representative)", "Dominant Firm & Market"),
    horizontal_spacing=0.05
)

# === LEFT PLOT: FRINGE FIRM ===
# 1. Fringe MC
mc_f_vals = [model.fringe_firm_MC(q) for q in q_range]
fig.add_trace(go.Scatter(x=q_range, y=mc_f_vals, name="MC Fringe", line=dict(color=C_MC_FRINGE, width=2)), row=1, col=1)

# 2. Fringe ATC
atc_f_vals = [model.fringe_firm_ATC(q) for q in q_range]
fig.add_trace(go.Scatter(x=q_range, y=atc_f_vals, name="ATC Fringe", line=dict(color="#4a148c", width=2), visible="legendonly"), row=1, col=1)

# 3. Equilibrium Markers (Left)
if eq['qf'] > 0:
    # Dashed line to axis
    fig.add_trace(go.Scatter(
        x=[eq['qf'], eq['qf']], y=[0, eq['Pd']], 
        mode="lines", line=dict(color="#333", dash="dash", width=1), showlegend=False
    ), row=1, col=1)
    
    # Point
    fig.add_trace(go.Scatter(
        x=[eq['qf']], y=[eq['Pd']], 
        mode="markers", marker=dict(color="#333", size=8), showlegend=False,
        hovertemplate=f"qf: {eq['qf']:.1f}<br>P: {eq['Pd']:.1f}"
    ), row=1, col=1)


# === RIGHT PLOT: DOMINANT FIRM ===

# 1. Residual Demand (Dr) - The Kinked Curve
# We build this carefully: Upper segment, then Lower segment
Qk = eq['Qk']
A, B = eq['A'], eq['B']

# Generate points for Dr
dr_x = []
dr_y = []
for q in q_range:
    if q < Qk:
        p = A - B*q
    else:
        p = a - b*q
    if p >= 0:
        dr_x.append(q)
        dr_y.append(p)

fig.add_trace(go.Scatter(x=dr_x, y=dr_y, name="Residual Demand (Dr)", line=dict(color=C_DEMAND, width=3)), row=1, col=2)

# 2. Market Demand (D(p)) - Dotted line above the kink
dem_x = np.linspace(0, Qk, 50)
dem_y = [a - b*q for q in dem_x]
fig.add_trace(go.Scatter(x=dem_x, y=dem_y, name="Market Demand", line=dict(color=C_DEMAND, width=2, dash="dot")), row=1, col=2)

# 3. Marginal Revenue (MR)
# MR has a vertical gap at the kink. We plot two segments.
mr_upper_x = np.linspace(0, Qk, 50)
mr_upper_y = [A - 2*B*q for q in mr_upper_x]

mr_lower_x = np.linspace(Qk, MAX_Q, 50)
mr_lower_y = [a - 2*b*q for q in mr_lower_x]

# Combine with None to break the line visually
mr_x = list(mr_upper_x) + [None] + list(mr_lower_x)
mr_y = list(mr_upper_y) + [None] + list(mr_lower_y)

fig.add_trace(go.Scatter(x=mr_x, y=mr_y, name="Marginal Revenue", line=dict(color=C_MR, width=2)), row=1, col=2)

# 4. Dominant MC
mc_d_vals = [model.mc_at(q) for q in q_range]
fig.add_trace(go.Scatter(x=q_range, y=mc_d_vals, name="MC Dominant", line=dict(color=C_MC_DOM, width=3)), row=1, col=2)

# 5. Dominant ATC
atc_d_vals = [model.atc_at(q) for q in q_range]
fig.add_trace(go.Scatter(x=q_range, y=atc_d_vals, name="ATC Dominant", line=dict(color="#6a1b9a", width=2), visible="legendonly"), row=1, col=2)

# 6. SHADING (Areas)
if show_cs and eq['Qd'] > 0:
    # Fill area under Residual Demand and above Price
    # We define the polygon coordinates
    poly_x = [0] + [q for q in dr_x if q <= eq['Qd']] + [0]
    poly_y = [eq['Pd']] + [p for idx, p in enumerate(dr_y) if dr_x[idx] <= eq['Qd']] + [eq['Pd']]
    
    fig.add_trace(go.Scatter(
        x=poly_x, y=poly_y, fill="toself", fillcolor=C_CS, 
        line=dict(width=0), name="Consumer Surplus", hoverinfo="skip"
    ), row=1, col=2)

if show_profit and eq['Qd'] > 0:
    atc_val = model.atc_at(eq['Qd'])
    if eq['Pd'] > atc_val:
        fig.add_trace(go.Scatter(
            x=[0, eq['Qd'], eq['Qd'], 0],
            y=[atc_val, atc_val, eq['Pd'], eq['Pd']],
            fill="toself", fillcolor=C_PROFIT,
            line=dict(width=0), name="Dominant Profit", hoverinfo="skip"
        ), row=1, col=2)

# 7. Equilibrium Markers (Right)
if eq['Qd'] > 0:
    # Dashed line to axis
    fig.add_trace(go.Scatter(
        x=[eq['Qd'], eq['Qd']], y=[0, eq['Pd']], 
        mode="lines", line=dict(color="#333", dash="dash", width=1), showlegend=False
    ), row=1, col=2)
    
    # Point at Eq
    fig.add_trace(go.Scatter(
        x=[eq['Qd']], y=[eq['Pd']], 
        mode="markers", marker=dict(color="#333", size=8, line=dict(color="white", width=1)), showlegend=False,
        hovertemplate=f"Qd: {eq['Qd']:.1f}<br>P*: {eq['Pd']:.1f}"
    ), row=1, col=2)


# ──────────────────────────────────────────────
# 5. LAYOUT STYLING (The "Clean White" Look)
# ──────────────────────────────────────────────
fig.update_layout(
    template="simple_white", # Base template closest to your HTML
    height=600,
    hovermode="x unified",
    xaxis=dict(range=[0, MAX_Q], title="Fringe Output (q)"),
    xaxis2=dict(range=[0, MAX_Q], title="Dominant Output (Q)"),
    yaxis=dict(range=[0, MAX_P], title="Price"),
    legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    margin=dict(l=20, r=20, t=60, b=40),
)

# Add gridlines (simple_white template removes them, but we want soft grids)
grid_style = dict(showgrid=True, gridcolor="#f0f0f0", gridwidth=1)
fig.update_xaxes(**grid_style)
fig.update_yaxes(**grid_style)

# Render
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ──────────────────────────────────────────────
# 6. METRICS ROW
# ──────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Market Price (P*)", f"${eq['Pd']:.2f}")
m2.metric("Dominant Qty (Qd)", f"{eq['Qd']:.2f}")
m3.metric("Fringe Total Qty", f"{eq['Qf']:.2f}")
m4.metric("Dominant Profit", f"${eq['profitD']:.0f}")
