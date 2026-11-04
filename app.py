import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# MESTI JADI ARAHAN PERTAMA STREAMLIT
st.set_page_config(
    page_title="Ideal Brayton Cycle Simulator", 
    page_layout="wide"
)

# Seterusnya barulah tajuk dan lain-lain
st.title("🔥 Ideal Brayton Cycle Interactive Simulator (KJM442)")
st.markdown(
    "Adjust the parameters below to observe real-time changes in performance metrics, thermal efficiency, back work ratio, and the $P-V$ and $T-s$ diagrams."
)

# --- SIDEBAR INPUTS ---
st.sidebar.header("Cycle Operating Parameters")
p1 = st.sidebar.slider(
    "Initial Pressure, P1 (kPa)", min_value=50.0, max_value=200.0, value=100.0, step=5.0
)
t1 = st.sidebar.slider(
    "Initial Temperature, T1 (K)", min_value=250.0, max_value=400.0, value=300.0, step=5.0
)
rp = st.sidebar.slider(
    "Pressure Ratio (r_p = P2/P1)", min_value=2.0, max_value=30.0, value=10.0, step=0.5
)
t3 = st.sidebar.slider(
    "Max Turbine Inlet Temp, T3 (K)", min_value=800.0, max_value=1800.0, value=1200.0, step=10.0
)
k = st.sidebar.slider(
    "Specific Heat Ratio (k for air)", min_value=1.2, max_value=1.67, value=1.4, step=0.01
)
cp = 1.005  # kJ/kg.K constant specific heat for air

# --- THERMODYNAMIC CALCULATIONS ---
# State 1
P1 = p1
T1 = t1

# State 2: Isentropic Compression (P2 = rp * P1)
P2 = rp * P1
T2 = T1 * (rp ** ((k - 1) / k))

# State 3: Constant Pressure Heat Addition (P3 = P2, T3 is given)
P3 = P2
T3 = t3

# State 4: Isentropic Expansion (P4 = P1)
P4 = P1
T4 = T3 * ((P4 / P3) ** ((k - 1) / k))

# Work and Heat metrics (per unit mass)
w_comp = cp * (T2 - T1)  # Compressor work input[cite: 12]
w_turb = cp * (T3 - T4)  # Turbine work output[cite: 12]
w_net = w_turb - w_comp  # Net work output
q_in = cp * (T3 - T2)  # Heat input[cite: 12]
q_out = cp * (T4 - T1)  # Heat rejection[cite: 12]

# Performance Metrics
eta_th = w_net / q_in  # Thermal Efficiency[cite: 13]
# Alternatively using temperature ratio formula[cite: 14]:
# eta_th = 1 - (1 / (rp ** ((k - 1) / k)))

bwr = w_comp / w_turb  # Back Work Ratio[cite: 14, 15]

# --- DISPLAY METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Thermal Efficiency (η_th)", f"{eta_th * 100:.2f} %")
col2.metric("Back Work Ratio (BWR)", f"{bwr:.4f} ({bwr * 100:.1f}%)")
col3.metric("Net Work Output (w_net)", f"{w_net:.2f} kJ/kg")
col4.metric(
    "Compressor Exit Temp (T2)", f"{T2:.2f} K", f"T4: {T4:.2f} K"
)

st.markdown("---")

# --- PLOTTING GRAPHS ($P-V$ and $T-s$) ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# 1. P-V Diagram Calculations & Plotting
# Process 1-2: Isentropic (P * v^k = constant -> P = C / v^k)
# We can simulate specific volumes v for plotting curves
v1 = (287 * T1) / (P1 * 1000)  # Ideal gas law estimation for scaling
v2 = v1 / (rp ** (1 / k))
v_comp = np.linspace(v2, v1, 100)
p_comp = P1 * (v1 / v_comp) ** k

v3 = (287 * T3) / (P3 * 1000)
# Process 3-4: Isentropic
v4 = v3 * (rp ** (1 / k))
v_turb = np.linspace(v3, v4, 100)
p_turb = P3 * (v3 / v_turb) ** k

# Plot P-V
ax1.plot(
    [v1, v2], [P1, P2], "g--", alpha=0.6
)  # straight guide or use curve below
ax1.plot(v_comp, p_comp, "r-", lw=2, label="1-2: Isentropic Compression")
ax1.plot(
    [v2, v3], [P2, P3], "b-", lw=2, label="2-3: Constant Pressure Heat Add"
)
ax1.plot(v_turb, p_turb, "m-", lw=2, label="3-4: Isentropic Expansion")
ax1.plot(
    [v4, v1], [P4, P1], "k-", lw=2, label="4-1: Constant Pressure Heat Reject"
)

# Scatter points for states
ax1.scatter([v1, v2, v3, v4], [P1, P2, P3, P4], color="black")
ax1.text(v1, P1 * 0.9, " 1", fontsize=12, fontweight="bold")
ax1.text(v2, P2 * 1.02, " 2", fontsize=12, fontweight="bold")
ax1.text(v3, P3 * 1.02, " 3", fontsize=12, fontweight="bold")
ax1.text(v4, P4 * 1.1, " 4", fontsize=12, fontweight="bold")

ax1.set_title("P-V Diagram (Brayton Cycle)", fontsize=14)
ax1.set_xlabel("Specific Volume (m^3/kg)", fontsize=12)
ax1.set_ylabel("Pressure (kPa)", fontsize=12)
ax1.grid(True, linestyle=":", alpha=0.7)
ax1.legend(loc="upper right")

# 2. T-s Diagram Calculations & Plotting
# Entropy changes relative to state 1 (s1 = 0 as baseline)
s1 = 0
s2 = s1  # Isentropic
s3 = s2 + cp * np.log(T3 / T2)
s4 = s3  # Isentropic

s_vals_12 = np.linspace(s1, s2, 50)
t_vals_12 = np.linspace(T1, T2, 50)

s_vals_23 = np.linspace(s2, s3, 50)
t_vals_23 = T2 * np.exp((s_vals_23 - s2) / cp)  # Constant pressure line approximation

s_vals_34 = np.linspace(s3, s4, 50)
t_vals_34 = np.linspace(T3, T4, 50)

s_vals_41 = np.linspace(s4, s1, 50)
t_vals_41 = T4 * np.exp((s_vals_41 - s4) / cp)

# Plot T-s
ax2.plot(s_vals_12, t_vals_12, "r-", lw=2, label="1-2: Isentropic Compression")
ax2.plot(s_vals_23, t_vals_23, "b-", lw=2, label="2-3: Constant Pressure (P2)")
ax2.plot(s_vals_34, t_vals_34, "m-", lw=2, label="3-4: Isentropic Expansion")
ax2.plot(s_vals_41, t_vals_41, "k-", lw=2, label="4-1: Constant Pressure (P1)")

# Scatter points for states
ax2.scatter([s1, s2, s3, s4], [T1, T2, T3, T4], color="black")
ax2.text(s1 - 0.05, T1, "1", fontsize=12, fontweight="bold")
ax2.text(s2 - 0.05, T2, "2", fontsize=12, fontweight="bold")
ax2.text(s3 + 0.02, T3, "3", fontsize=12, fontweight="bold")
ax2.text(s4 + 0.02, T4, "4", fontsize=12, fontweight="bold")

ax2.set_title("T-s Diagram (Brayton Cycle)", fontsize=14)
ax2.set_xlabel("Specific Entropy s (kJ/kg·K)", fontsize=12)
ax2.set_ylabel("Temperature T (K)", fontsize=12)
ax2.grid(True, linestyle=":", alpha=0.7)
ax2.legend(loc="upper left")

# Render plots in Streamlit
st.pyplot(fig)