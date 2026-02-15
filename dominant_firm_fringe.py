"""
Dominant Firm & Competitive Fringe — Interactive Visualization
Streamlit + Plotly implementation

Run with:  streamlit run dominant_firm_app.py
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dominant Firm & Competitive Fringe",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal custom CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 0; }
    h1 { font-size: 1.6rem !important; margin-bottom: 0.3rem !important; }
    .stMetric { background: #f8f8f8; border-radius: 8px; padding: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("Dominant Firm & Competitive Fringe")


# ──────────────────────────────────────────────
# Model
# ──────────────────────────────────────────────
class DFModel:
    def __init__(self, a, b, cF, dF, n, mc0, mcS, FC):
        self.a = a
        self.b = b
        self.cF = cF
        self.dF = dF
        self.n = n
        self.mc0 = mc0
        self.mcS = mcS
        self.FC = FC

    def market_demand_P(self, Q):
        return self.a - self.b * Q

    def market_demand_Q(self, P):
        return max(0, (self.a - P) / self.b)

    def fringe_supply_Q(self, P):
        return self.n * (P - self.cF) / self.dF if P >= self.cF else 0

    def fringe_supply_P(self, Qf):
        return self.cF + (self.dF * Qf) / self.n

    def fringe_firm_Q(self, P):
        return (P - self.cF) / self.dF if P >= self.cF else 0

    def mc_at(self, q):
        return self.mc0 + self.mcS * q

    def total_cost(self, q):
        return self.FC + self.mc0 * q + (self.mcS * q * q) / 2

    def atc_at(self, q):
        return self.total_cost(q) / q if q > 0.5 else 9999

    def fringe_firm_MC(self, q):
        return self.cF + self.dF * q

    def fringe_firm_ATC(self, q):
        return self.cF + self.dF * q / 2 if q > 0.5 else 9999

    def kink_Q(self):
        return max(0, (self.a - self.cF) / self.b)

    def upper_seg(self):
        d = self.dF / self.n
        A = (self.a * d + self.cF * self.b) / (self.b + d)
        B = (self.b * d) / (self.b + d)
        return A, B

    def residual_demand_P(self, Qd):
        Qk = self.kink_Q()
        if Qd >= Qk:
            return max(0, self.a - self.b * Qd)
        A, B = self.upper_seg()
        return max(0, A - B * Qd)

    def competitive_price(self):
        return (self.dF * self.a + self.n * self.b * self.cF) / (self.n * self.b + self.dF)

    def solve(self):
        a, b, cF, dF, mc0, mcS, n, FC = (
            self.a, self.b, self.cF, self.dF,
            self.mc0, self.mcS, self.n, self.FC,
        )
        Qk = self.kink_Q()
        A, B = self.upper_seg()

        Q1 = (A - mc0) / (2 * B + mcS) if (2 * B + mcS) > 0 else float("inf")
        Q2 = (a - mc0) / (2 * b + mcS) if (2 * b + mcS) > 0 else float("inf")

        if Q1 >= 0 and Q1 < Qk:
            Qd, seg = Q1, "upper"
        elif Q2 >= 0 and Q2 > Qk:
            Qd, seg = Q2, "lower"
        else:
            Qd, seg = Qk, "kink"
        Qd = max(0, Qd)

        Pd = self.residual_demand_P(Qd)
        Qf = self.fringe_supply_Q(Pd)
        qf = self.fringe_firm_Q(Pd)
        Qt = Qd + Qf
        mcQd = self.mc_at(Qd)
        profitD = Pd * Qd - self.total_cost(Qd)
        atcQd = self.atc_at(Qd)

        fringeATCqf = cF + dF * qf / 2 if qf > 0.5 else 0
        fringeProfitPerFirm = (Pd - fringeATCqf) * qf if qf > 0 else 0
        CS = 0.5 * (a - Pd) * Qt if Qt > 0 else 0

        # Efficient Q on residual demand
        QdCU = (A - mc0) / (B + mcS) if (B + mcS) > 0 else 0
        QdCL = (a - mc0) / (b + mcS) if (b + mcS) > 0 else 0
        QdComp = QdCU if (QdCU >= 0 and QdCU <= Qk) else max(0, QdCL)
        PdComp = self.residual_demand_P(QdComp)

        # DWL
        DWL = 0
        if Qd < QdComp:
            steps = 200
            for i in range(steps):
                q = Qd + (i + 0.5) / steps * (QdComp - Qd)
                dq = (QdComp - Qd) / steps
                pR = self.residual_demand_P(q)
                mcQ = self.mc_at(q)
                if pR > mcQ:
                    DWL += (pR - mcQ) * dq

        Pc = self.competitive_price()
        QcMarket = self.market_demand_Q(Pc)
        QcFringe = self.fringe_supply_Q(Pc)
        mrT = A - 2 * B * Qk
        mrB = a - 2 * b * Qk

        return dict(
            Pd=Pd, Qd=Qd, Qf=Qf, qf=qf, Qt=Qt, seg=seg,
            mcQd=mcQd, atcQd=atcQd, profitD=profitD,
            fringeProfitPerFirm=fringeProfitPerFirm,
            CS=CS, DWL=DWL, Qk=Qk, QdComp=QdComp, PdComp=PdComp,
            Pc=Pc, QcMarket=QcMarket, QcFringe=QcFringe,
            mrT=mrT, mrB=mrB,
        )


# ──────────────────────────────────────────────
# Sidebar controls
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("Market Demand")
    a = st.slider("Intercept (a)", 50, 200, 100, 1)
    b = st.slider("Slope (b)", 0.20, 3.00, 1.00, 0.05)

    st.header("Fringe Supply")
    cF = st.slider("Min Price (cF)", 0, 80, 20, 1)
    dF = st.slider("Slope (dF)", 0.20, 5.00, 1.50, 0.05)
    n = st.slider("Num. Firms (n)", 1, 20, 5, 1)

    st.header("Dominant Firm")
    mc0 = st.slider("MC Base", 0, 80, 10, 1)
    mcS = st.slider("MC Slope", 0.00, 3.00, 0.30, 0.05)
    FC = st.slider("Fixed Cost", 0, 1000, 50, 10)

    st.header("Display Options")
    col1, col2 = st.columns(2)
    with col1:
        show_cs = st.checkbox("Consumer Surplus", True)
        show_ps = st.checkbox("Producer Surplus", True)
        show_dwl = st.checkbox("Deadweight Loss", True)
    with col2:
        show_profit = st.checkbox("Profit", False)
        show_atc = st.checkbox("ATC", False)
        show_comp = st.checkbox("Competitive", False)


# ──────────────────────────────────────────────
# Solve model
# ──────────────────────────────────────────────
model = DFModel(a, b, cF, dF, n, mc0, mcS, FC)
eq = model.solve()
Qk = eq["Qk"]
A_u, B_u = model.upper_seg()
MAX_Q, MAX_P = 120, 120


# ──────────────────────────────────────────────
# Helper: generate curve arrays (stop when P < 0)
# ──────────────────────────────────────────────
def make_curve(fn, q_min, q_max, n_pts=500):
    qs, ps = [], []
    for i in range(n_pts + 1):
        q = q_min + (i / n_pts) * (q_max - q_min)
        p = fn(q)
        if p < 0:
            # Interpolate the exact zero crossing
            if qs:
                q_prev, p_prev = qs[-1], ps[-1]
                if p_prev > 0:
                    q_zero = q_prev + (q - q_prev) * p_prev / (p_prev - p)
                    qs.append(q_zero)
                    ps.append(0)
            break
        if p <= MAX_P:
            qs.append(q)
            ps.append(p)
    return np.array(qs), np.array(ps)


# ──────────────────────────────────────────────
# Build the figure
# ──────────────────────────────────────────────
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Fringe Firm", "Dominant Firm"),
    shared_yaxes=True,
    horizontal_spacing=0.06,
)

COLORS = dict(
    demand="#c62828",
    mc_dom="#2e7d32",
    mc_fringe="#0277bd",
    mr="#e65100",
    atc="#6a1b9a",
    fringe_supply="#2e7d32",
    cs="rgba(66,133,244,0.25)",
    ps="rgba(52,168,83,0.25)",
    dwl="rgba(234,67,53,0.25)",
    profit="rgba(251,188,4,0.30)",
)


# ═══════════════════════════════════════════════
# RIGHT PANEL — Dominant Firm
# ═══════════════════════════════════════════════

# -- Shaded regions --
Pd, Qd = eq["Pd"], eq["Qd"]

if show_cs and Qd > 0:
    qr = np.linspace(0, Qd, 100)
    p_top = np.array([model.residual_demand_P(q) for q in qr])
    p_bot = np.full_like(qr, Pd)
    fig.add_trace(go.Scatter(
        x=np.concatenate([qr, qr[::-1]]),
        y=np.concatenate([p_top, p_bot[::-1]]),
        fill="toself", fillcolor=COLORS["cs"], line=dict(width=0),
        name="CS", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

if show_ps and Qd > 0:
    qr = np.linspace(0, Qd, 100)
    p_top = np.full_like(qr, Pd)
    p_bot = np.array([model.mc_at(q) for q in qr])
    fig.add_trace(go.Scatter(
        x=np.concatenate([qr, qr[::-1]]),
        y=np.concatenate([p_top, p_bot[::-1]]),
        fill="toself", fillcolor=COLORS["ps"], line=dict(width=0),
        name="PS_d", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

if show_dwl and Qd > 0 and eq["QdComp"] > Qd:
    qr = np.linspace(Qd, eq["QdComp"], 100)
    p_res = np.array([model.residual_demand_P(q) for q in qr])
    p_mc = np.array([model.mc_at(q) for q in qr])
    # Only where residual demand > MC
    valid = p_res > p_mc
    if np.any(valid):
        qv = qr[valid]
        pr_v = p_res[valid]
        pm_v = p_mc[valid]
        fig.add_trace(go.Scatter(
            x=np.concatenate([qv, qv[::-1]]),
            y=np.concatenate([pr_v, pm_v[::-1]]),
            fill="toself", fillcolor=COLORS["dwl"], line=dict(width=0),
            name="DWL", showlegend=False, hoverinfo="skip",
        ), row=1, col=2)

if show_profit and Qd > 0:
    atcV = model.atc_at(Qd)
    if Pd > atcV:
        qr = np.linspace(0, Qd, 50)
        fig.add_trace(go.Scatter(
            x=np.concatenate([qr, qr[::-1]]),
            y=np.concatenate([np.full_like(qr, Pd), np.full_like(qr, atcV)]),
            fill="toself", fillcolor=COLORS["profit"], line=dict(width=0),
            name="πd", showlegend=False, hoverinfo="skip",
        ), row=1, col=2)

# -- D(p) dotted above kink --
if Qk > 0:
    qd_dp, pd_dp = make_curve(lambda q: a - b * q, 0, Qk)
    fig.add_trace(go.Scatter(
        x=qd_dp, y=pd_dp,
        mode="lines", line=dict(color=COLORS["demand"], width=2, dash="dash"),
        name="D(p)", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- Residual demand: upper segment (Dr) --
qr_up, pr_up = make_curve(lambda q: A_u - B_u * q, 0, Qk)
if len(qr_up) > 1:
    fig.add_trace(go.Scatter(
        x=qr_up, y=pr_up,
        mode="lines", line=dict(color=COLORS["demand"], width=3),
        name="Dr", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- Residual demand: lower segment = D(p)=Dr --
qr_lo, pr_lo = make_curve(lambda q: a - b * q, Qk, MAX_Q)
if len(qr_lo) > 1:
    fig.add_trace(go.Scatter(
        x=qr_lo, y=pr_lo,
        mode="lines", line=dict(color=COLORS["demand"], width=3),
        name="D(p)=Dr", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# Kink dot
kP = model.residual_demand_P(Qk)
if 0 < Qk < MAX_Q and 0 < kP < MAX_P:
    fig.add_trace(go.Scatter(
        x=[Qk], y=[kP], mode="markers",
        marker=dict(size=8, color=COLORS["demand"]),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- MR upper segment --
qm_up, pm_up = make_curve(lambda q: A_u - 2 * B_u * q, 0, Qk)
if len(qm_up) > 1:
    fig.add_trace(go.Scatter(
        x=qm_up, y=pm_up,
        mode="lines", line=dict(color=COLORS["mr"], width=2.5),
        name="MRd", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- MR lower segment --
mrB = eq["mrB"]
qm_lo, pm_lo = np.array([]), np.array([])
if mrB > 0.5:
    qm_lo, pm_lo = make_curve(lambda q: a - 2 * b * q, Qk, MAX_Q)
    if len(qm_lo) > 1:
        fig.add_trace(go.Scatter(
            x=qm_lo, y=pm_lo,
            mode="lines", line=dict(color=COLORS["mr"], width=2.5),
            name="MRd lower", showlegend=False, hoverinfo="skip",
        ), row=1, col=2)

# -- MR vertical gap --
mrT = eq["mrT"]
if Qk > 0 and mrT > mrB and mrB > 0.5:
    fig.add_trace(go.Scatter(
        x=[Qk, Qk], y=[min(mrT, MAX_P), mrB],
        mode="lines", line=dict(color=COLORS["mr"], width=1.5, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- MCd --
qmc, pmc = make_curve(lambda q: model.mc_at(q), 0, MAX_Q)
fig.add_trace(go.Scatter(
    x=qmc, y=pmc,
    mode="lines", line=dict(color=COLORS["mc_dom"], width=3),
    name="MCd", showlegend=False, hoverinfo="skip",
), row=1, col=2)

# -- ACd --
if show_atc:
    qa = np.linspace(1, MAX_Q, 400)
    pa = np.array([model.atc_at(q) for q in qa])
    mask = pa < MAX_P
    fig.add_trace(go.Scatter(
        x=qa[mask], y=pa[mask],
        mode="lines", line=dict(color=COLORS["atc"], width=2.2),
        name="ACd", showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

# -- Equilibrium markers (right) --
if Qd > 0 and 0 < Pd < MAX_P:
    # Vertical dashed to axis
    fig.add_trace(go.Scatter(
        x=[Qd, Qd], y=[0, Pd],
        mode="lines", line=dict(color="black", width=1.5, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=2)
    # Equilibrium point (P*, Qd)
    fig.add_trace(go.Scatter(
        x=[Qd], y=[Pd], mode="markers",
        marker=dict(size=10, color="#333", line=dict(width=2, color="white")),
        showlegend=False,
        hovertemplate=(
            "<b>Dominant Firm Equilibrium</b><br>"
            f"P* = {Pd:.2f}<br>"
            f"Qd = {Qd:.2f}<br>"
            f"Qf = {eq['Qf']:.2f}<br>"
            f"πd = {eq['profitD']:.1f}<extra></extra>"
        ),
    ), row=1, col=2)
    # MR=MC point
    fig.add_trace(go.Scatter(
        x=[Qd], y=[eq["mcQd"]], mode="markers",
        marker=dict(size=8, color="#333", line=dict(width=2, color="white")),
        showlegend=False,
        hovertemplate=(
            "<b>MR = MC</b><br>"
            f"Qd = {Qd:.2f}<br>"
            f"MR = MC = {eq['mcQd']:.2f}<br>"
            f"Segment: {eq['seg']}<extra></extra>"
        ),
    ), row=1, col=2)

# -- Competitive equilibrium --
if show_comp and eq["QdComp"] > 0:
    QdC, PdC = eq["QdComp"], eq["PdComp"]
    fig.add_trace(go.Scatter(
        x=[QdC, QdC], y=[0, PdC],
        mode="lines", line=dict(color="black", width=1.5, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=[QdC], y=[PdC], mode="markers",
        marker=dict(size=8, color="black", line=dict(width=2, color="white")),
        showlegend=False,
        hovertemplate=(
            "<b>Efficient Equilibrium</b><br>"
            f"Pc = {PdC:.2f}<br>"
            f"Q* = {QdC:.2f}<extra></extra>"
        ),
    ), row=1, col=2)


# ═══════════════════════════════════════════════
# LEFT PANEL — Fringe Firm
# ═══════════════════════════════════════════════

# Fringe profit shading
if show_profit and eq["qf"] > 0 and Pd > 0:
    fAtc = model.fringe_firm_ATC(eq["qf"])
    if Pd > fAtc:
        qr = np.linspace(0, eq["qf"], 50)
        fig.add_trace(go.Scatter(
            x=np.concatenate([qr, qr[::-1]]),
            y=np.concatenate([np.full_like(qr, Pd), np.full_like(qr, fAtc)]),
            fill="toself", fillcolor=COLORS["profit"], line=dict(width=0),
            name="πf", showlegend=False, hoverinfo="skip",
        ), row=1, col=1)

# D(p) solid red
qd_l, pd_l = make_curve(lambda q: a - b * q, 0, MAX_Q)
fig.add_trace(go.Scatter(
    x=qd_l, y=pd_l,
    mode="lines", line=dict(color=COLORS["demand"], width=2),
    name="D(p)", showlegend=False, hoverinfo="skip",
), row=1, col=1)

# S(p) aggregate fringe
qs_l, ps_l = make_curve(lambda q: model.fringe_supply_P(q), 0, MAX_Q)
fig.add_trace(go.Scatter(
    x=qs_l, y=ps_l,
    mode="lines", line=dict(color=COLORS["fringe_supply"], width=2.5),
    name="S(p)", showlegend=False, hoverinfo="skip",
), row=1, col=1)

# MCf
qmf, pmf = make_curve(lambda q: model.fringe_firm_MC(q), 0, MAX_Q)
fig.add_trace(go.Scatter(
    x=qmf, y=pmf,
    mode="lines", line=dict(color=COLORS["mc_fringe"], width=3),
    name="MCf", showlegend=False, hoverinfo="skip",
), row=1, col=1)

# ACf
if show_atc:
    qa_f = np.linspace(1, MAX_Q, 400)
    pa_f = np.array([model.fringe_firm_ATC(q) for q in qa_f])
    mask = pa_f < MAX_P
    fig.add_trace(go.Scatter(
        x=qa_f[mask], y=pa_f[mask],
        mode="lines", line=dict(color="#4a148c", width=2.2),
        name="ACf", showlegend=False, hoverinfo="skip",
    ), row=1, col=1)

# S(p) ∩ D(p) intersection
Pc = eq["Pc"]
QcMkt = eq["QcMarket"]
QcFringe = eq["QcFringe"]
if 0 < Pc < MAX_P and 0 < QcMkt < MAX_Q:
    fig.add_trace(go.Scatter(
        x=[QcMkt], y=[Pc], mode="markers",
        marker=dict(size=8, color="#555", line=dict(width=2, color="white")),
        showlegend=False,
        hovertemplate=(
            "<b>S(p) = D(p) Intersection</b><br>"
            f"Pc = {Pc:.2f}<br>"
            f"Q (market) = {QcMkt:.2f}<br>"
            f"Qf (fringe total) = {QcFringe:.2f}<br>"
            "Competitive outcome<extra></extra>"
        ),
    ), row=1, col=1)

# Fringe eq markers
qf = eq["qf"]
if qf > 0 and 0 < Pd <= MAX_P:
    fig.add_trace(go.Scatter(
        x=[qf, qf], y=[0, Pd],
        mode="lines", line=dict(color="black", width=1.5, dash="dash"),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[qf], y=[Pd], mode="markers",
        marker=dict(size=8, color="#333", line=dict(width=2, color="white")),
        showlegend=False,
        hovertemplate=(
            "<b>Fringe Firm</b><br>"
            f"P* = {Pd:.2f}<br>"
            f"qf = {qf:.2f}<br>"
            f"πf = {eq['fringeProfitPerFirm']:.1f}<br>"
            f"{n} firms × {qf:.1f} = {eq['Qf']:.1f}<extra></extra>"
        ),
    ), row=1, col=1)


# ═══════════════════════════════════════════════
# Horizontal price lines across both panels
# ═══════════════════════════════════════════════
price_lines = []
if Qd > 0 and 0 < Pd < MAX_P:
    price_lines.append(dict(p=Pd, label="P*", color="black"))
if 0 < cF < MAX_P:
    price_lines.append(dict(p=cF, label="p̄", color="black"))
if 0 < Pc < MAX_P:
    price_lines.append(dict(p=Pc, label="Pc", color="gray"))

for pl in price_lines:
    for col in [1, 2]:
        fig.add_hline(
            y=pl["p"], row=1, col=col,
            line=dict(color=pl["color"], width=1.5, dash="dash"),
            opacity=0.5,
        )


# ═══════════════════════════════════════════════
# Curve label annotations
# ═══════════════════════════════════════════════

# Right panel labels
def add_label(text, x, y, col, color, xanchor="left", yanchor="middle", xshift=6, yshift=0):
    fig.add_annotation(
        x=x, y=y, text=f"<b>{text}</b>",
        showarrow=False, font=dict(size=13, color=color, family="IBM Plex Sans"),
        xanchor=xanchor, yanchor=yanchor, xshift=xshift, yshift=yshift,
        row=1, col=col,
    )

# Right panel
if len(qr_up) > 1:
    mid_i = len(qr_up) // 2
    add_label("Dr", qr_up[mid_i], pr_up[mid_i], 2, COLORS["demand"], yshift=12)

if len(qr_lo) > 1:
    add_label("D(p)=Dr", qr_lo[-1], max(pr_lo[-1], 2), 2, COLORS["demand"], yshift=-14)

if Qk > 0 and len(qd_dp) > 1:
    mid_i = len(qd_dp) // 3
    add_label("D(p)", qd_dp[mid_i], pd_dp[mid_i], 2, COLORS["demand"], yshift=12, xshift=-8)

# MRd label at end of visible curve
if len(qm_lo) > 1:
    add_label("MRd", qm_lo[-1], max(pm_lo[-1], 2), 2, COLORS["mr"], yshift=-14)
elif len(qm_up) > 1:
    add_label("MRd", qm_up[-1], pm_up[-1], 2, COLORS["mr"], yshift=-8)

add_label("MCd", qmc[-1], min(pmc[-1], MAX_P - 5), 2, COLORS["mc_dom"])

# Left panel
if len(qd_l) > 1:
    add_label("D(p)", qd_l[-1], max(pd_l[-1], 2), 1, COLORS["demand"], yshift=-14)
if len(qs_l) > 1:
    add_label("S(p)", qs_l[-1], min(ps_l[-1], MAX_P - 5), 1, COLORS["fringe_supply"])
add_label("MCf", qmf[-1], min(pmf[-1], MAX_P - 5), 1, COLORS["mc_fringe"])

# Price line labels (on right edge)
for pl in price_lines:
    add_label(pl["label"], MAX_Q, pl["p"], 2, pl["color"], xanchor="left", xshift=4, yshift=0)
    add_label(pl["label"], 0, pl["p"], 1, pl["color"], xanchor="right", xshift=-4, yshift=0)

# Axis quantity labels
if Qd > 0:
    fig.add_annotation(
        x=Qd, y=0, text="<b>Qd</b>", showarrow=False,
        font=dict(size=11, color="#333"), yshift=-18, row=1, col=2,
    )
if qf > 0:
    fig.add_annotation(
        x=qf, y=0, text="<b>qf</b>", showarrow=False,
        font=dict(size=11, color="#333"), yshift=-18, row=1, col=1,
    )


# ═══════════════════════════════════════════════
# Layout
# ═══════════════════════════════════════════════
fig.update_xaxes(range=[0, MAX_Q], title_text="Fringe firm output, q", row=1, col=1)
fig.update_xaxes(range=[0, MAX_Q], title_text="Dominant firm output, Q", row=1, col=2)
fig.update_yaxes(range=[0, MAX_P], title_text="Price", row=1, col=1)
fig.update_yaxes(range=[0, MAX_P], row=1, col=2)

fig.update_layout(
    height=620,
    margin=dict(l=60, r=40, t=40, b=60),
    plot_bgcolor="white",
    paper_bgcolor="#f5f5f5",
    font=dict(family="IBM Plex Sans"),
    hovermode="closest",
)

# Grid lines
for ax in ["xaxis", "xaxis2", "yaxis", "yaxis2"]:
    fig.update_layout(**{
        ax: dict(
            showgrid=True, gridcolor="rgba(0,0,0,0.06)", gridwidth=1,
            zeroline=True, zerolinecolor="#333", zerolinewidth=2,
            dtick=20,
        )
    })

st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
# Readouts
# ──────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("P*", f"{Pd:.1f}" if Qd > 0 else "—")
c2.metric("Qd", f"{Qd:.1f}" if Qd > 0 else "0")
c3.metric("Qf", f"{eq['Qf']:.1f}" if Qd > 0 else "0")
c4.metric("πd", f"{eq['profitD']:.0f}" if Qd > 0 else "0")
c5.metric("CS", f"{eq['CS']:.0f}" if Qd > 0 else "0")
c6.metric("DWL", f"{eq['DWL']:.0f}" if Qd > 0 else "0")
