# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 20:54:45 2025

@author: camil
"""

# app.py — Simulación en Streamlit
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ====== Constantes físicas ======
q_proton = 1.602e-19
m_proton = 1.672e-27

# ====== Parámetros base ======
B_INITIAL = 0.005        # Dentro del rango 0.005 .. 0.01
VEL_INITIAL = 15000.0    # m/s
dt = 1e-8
n_steps = 5000
field_start_pos_x = 0.0
initial_pos_x = -0.02

# Escala fija del gráfico
X_LIM_LEFT = -0.05
X_LIM_RIGHT = 0.05
Y_LIM = 0.1

# ====== Estado (session_state) ======
if "pos_x" not in st.session_state:
    st.session_state.pos_x = np.array([])
    st.session_state.pos_y = np.array([])
    st.session_state.times = np.array([])
if "B" not in st.session_state:
    st.session_state.B = B_INITIAL
if "velocity" not in st.session_state:
    st.session_state.velocity = VEL_INITIAL
if "field_off" not in st.session_state:
    st.session_state.field_off = False
if "frame" not in st.session_state:
    st.session_state.frame = 0

# ====== Simulación ======
def run_simulation(b_mag: float, v_mag: float, field_off: bool):
    """Devuelve (x, y, t) para la trayectoria con parámetros dados."""
    q = q_proton
    m = m_proton

    if field_off:
        b_mag = 0.0

    pos = np.array([initial_pos_x, 0.0], dtype=float)
    vel = np.array([v_mag, 0.0], dtype=float)

    xs = [pos[0]]
    ys = [pos[1]]
    ts = [0.0]

    for step in range(1, n_steps):
        current_time = step * dt
        # Campo activo solo si x >= 0 y no está apagado globalmente
        if field_off:
            current_B = 0.0
        else:
            current_B = b_mag if pos[0] >= field_start_pos_x else 0.0

        # Fuerza de Lorentz (B || +z): (q*vy*B, -q*vx*B)
        Fx = q * vel[1] * current_B
        Fy = -q * vel[0] * current_B

        ax = Fx / m
        ay = Fy / m

        # Integración explícita simple
        vel[0] += ax * dt
        vel[1] += ay * dt
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt

        xs.append(pos[0])
        ys.append(pos[1])
        ts.append(current_time)

        # Corte de seguridad si se va muy lejos
        if (abs(pos[0]) > 2 * abs(X_LIM_RIGHT) or abs(pos[1]) > 2 * abs(Y_LIM)):
            break

    return np.array(xs), np.array(ys), np.array(ts)

# ====== UI ======
st.title("Trayectoria de un protón en un campo magnético uniforme (Streamlit)")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    B_ui = st.slider("|B| [T]", min_value=0.005, max_value=0.01,
                     value=float(st.session_state.B),
                     step=0.0005, format="%.4f",
                     help="Magnitud del campo en la región x ≥ 0")
with col2:
    velocity_ui = st.slider("v0 [m/s]", min_value=5000, max_value=22000,
                            value=int(st.session_state.velocity), step=500)
with col3:
    st.markdown("**Campo nulo**")
    field_zero_clicked = st.button("B = 0 (apagar campo)")

colA, colB, colC = st.columns([1, 1, 1])
with colA:
    if st.button("Calcular / Actualizar"):
        # Mover sliders reactiva el campo
        st.session_state.field_off = False
        st.session_state.B = float(B_ui)
        st.session_state.velocity = float(velocity_ui)
        x, y, t = run_simulation(st.session_state.B, st.session_state.velocity, st.session_state.field_off)
        st.session_state.pos_x, st.session_state.pos_y, st.session_state.times = x, y, t
        st.session_state.frame = 0
with colB:
    play_clicked = st.button("Reproducir")
with colC:
    if st.button("Reiniciar"):
        st.session_state.pos_x = np.array([])
        st.session_state.pos_y = np.array([])
        st.session_state.times = np.array([])
        st.session_state.frame = 0
        st.session_state.B = B_INITIAL
        st.session_state.velocity = VEL_INITIAL
        st.session_state.field_off = False

# Botón campo nulo (no recalcula automáticamente para que se note el estado)
if field_zero_clicked:
    st.session_state.field_off = True
    st.session_state.B = 0.0
    # No recalc aquí; que el usuario presione "Calcular / Actualizar" para ver la nueva trayectoria.

# Scrubber de frame (si ya hay trayectoria)
if st.session_state.pos_x.size > 0:
    st.session_state.frame = st.slider(
        "Frame", 0, int(st.session_state.pos_x.size - 1),
        value=int(st.session_state.frame), step=1
    )

# ====== Gráfico ======
def plot_frame(frame_idx: int):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal', 'box')
    ax.set_title('Trayectoria de un protón en un campo magnético uniforme')
    ax.set_xlabel('Posición X [m]')
    ax.set_ylabel('Posición Y [m]')
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')

    # Escala fija
    ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
    ax.set_ylim(-Y_LIM, 0.01)

    # Línea divisoria x=0
    ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--')

    # Puntos de la zona con B (lado derecho)
    dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
    dots_y = np.linspace(-Y_LIM + 0.005, Y_LIM - 0.005, 6)
    XX, YY = np.meshgrid(dots_x, dots_y)
    col = 'gray' if (st.session_state.field_off or st.session_state.B <= 0) else 'black'
    alpha = 0.25 if (st.session_state.field_off or st.session_state.B <= 0) else 1.0
    ax.scatter(XX, YY, marker='.', color=col, alpha=alpha, s=50)

    # Trayectoria y punto
    if st.session_state.pos_x.size > 0:
        x = st.session_state.pos_x
        y = st.session_state.pos_y
        f = max(0, min(frame_idx, x.size - 1))
        ax.plot(x[:f+1], y[:f+1], 'b-', lw=2)
        ax.plot([x[f]], [y[f]], 'ro', ms=7)

        # Texto de zona
        if st.session_state.field_off or st.session_state.B <= 0:
            zona = "SIN campo (B=0)"
        else:
            zona = "CON campo" if x[f] >= 0 else "SIN campo"
        ax.text(0.02, 0.95,
                f"Zona: {zona}\n|B|={(0.0 if st.session_state.field_off else st.session_state.B):.4f} T\nv0={st.session_state.velocity:.0f} m/s",
                transform=ax.transAxes, fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    else:
        ax.text(0.5, 0.5, "Presiona 'Calcular / Actualizar' para generar la trayectoria",
                ha='center', va='center', fontsize=11)

    fig.tight_layout()
    return fig

placeholder = st.empty()

# Mostrar cuadro actual
fig = plot_frame(st.session_state.frame)
placeholder.pyplot(fig)

# Reproducir (animación simple en el servidor; bloquea hasta terminar)
if play_clicked and st.session_state.pos_x.size > 0:
    for f in range(st.session_state.frame, st.session_state.pos_x.size):
        fig = plot_frame(f)
        placeholder.pyplot(fig)
        st.session_state.frame = f
        time.sleep(0.02)  # ~50 fps
    # Al terminar, deja el último cuadro mostrado

st.caption("© Domenico Sapone, Camila Montecinos")
