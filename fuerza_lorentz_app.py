# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 20:54:45 2025

@author: camil
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import io
import base64
from IPython.display import HTML

# Configuración de la página
st.set_page_config(page_title="Simulación Campo Magnético", layout="wide")

# Constantes físicas
q_proton = 1.602e-19
m_proton = 1.672e-27

# Parámetros iniciales
B_initial = 0.005
velocity_initial = 15000
dt = 1e-8
n_steps = 5000
field_start_pos_x = 0.0
initial_pos_x = -0.02

# ESCALA FIJA
X_LIM_LEFT = -0.05
X_LIM_RIGHT = 0.05
Y_LIM = 0.1

# Título principal
st.title("Simulación de Trayectoria de un Protón en Campo Magnético")
st.markdown("---")

# Sidebar para controles
st.sidebar.header("🎛️ Controles de Simulación")

# Sliders en sidebar
B = st.sidebar.slider(
    "Intensidad del Campo Magnético B (T)",
    min_value=0.005,
    max_value=0.01,
    value=B_initial,
    step=0.0005,
    format="%.3f",
    help="Controla la intensidad del campo magnético"
)

velocity = st.sidebar.slider(
    "Velocidad Inicial (m/s)",
    min_value=5000,
    max_value=22000,
    value=velocity_initial,
    step=1000,
    help="Velocidad inicial del protón"
)

# Botones en sidebar
col1, col2, col3 = st.sidebar.columns(3)

with col1:
    play_button = st.button("▶️ Play", use_container_width=True)

with col2:
    reset_button = st.button("🔄 Reiniciar", use_container_width=True)

with col3:
    field_off = st.toggle("B = 0", value=False, help="Apagar el campo magnético")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Información")
st.sidebar.info("""
**Instrucciones:**
1. Ajusta los parámetros con los sliders
2. Presiona **Play** para iniciar
3. Usa **B=0** para campo nulo
4. **Reiniciar** para volver al inicio
""")

# Función de simulación
def run_simulation(b_mag, v_mag, field_off_flag):
    """Ejecuta la simulación con los parámetros dados"""
    q = q_proton
    m = m_proton

    # Si el botón de campo nulo está activo, forzamos B=0
    if field_off_flag:
        b_mag = 0.0
    
    pos = np.array([initial_pos_x, 0.0])
    vel = np.array([v_mag, 0.0])
    
    posiciones_x = [pos[0]]
    posiciones_y = [pos[1]]
    times = [0.0]
    
    for step in range(1, n_steps):
        current_time = step * dt
        
        # Campo activo solo si x >= 0 y si no está apagado globalmente
        current_B = b_mag if (not field_off_flag and pos[0] >= field_start_pos_x) else 0.0
        
        # Fuerza de Lorentz (B || +z): F = q (v × B) -> (q*vy*B, -q*vx*B)
        fuerza_x = q * vel[1] * current_B
        fuerza_y = -q * vel[0] * current_B
        
        # Aceleración
        aceleracion_x = fuerza_x / m
        aceleracion_y = fuerza_y / m
        
        # Integración explícita simple
        vel[0] += aceleracion_x * dt
        vel[1] += aceleracion_y * dt
        
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt
        
        posiciones_x.append(pos[0])
        posiciones_y.append(pos[1])
        times.append(current_time)
        
        # Corte de seguridad si se va muy lejos
        if (abs(pos[0]) > 2 * abs(X_LIM_RIGHT) or 
            abs(pos[1]) > 2 * abs(Y_LIM)):
            break
        
    return posiciones_x, posiciones_y, times

# Función para crear la animación
def create_animation(posiciones_x, posiciones_y, field_off_flag):
    """Crea y muestra la animación"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.set_aspect('equal', 'box')
    ax.set_title('Trayectoria de un protón en un campo magnético uniforme')
    ax.set_xlabel('Posición X (m)')
    ax.set_ylabel('Posición Y (m)')
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')
    
    # ESCALA FIJA
    ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
    ax.set_ylim(-Y_LIM, 0.01)
    
    # Línea divisoria
    ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--', 
               label='Límite del campo')
    
    # Puntos de campo magnético (a la derecha) - solo si el campo no está apagado
    if not field_off_flag:
        dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
        dots_y = np.linspace(-Y_LIM + 0.005, Y_LIM - 0.005, 6)
        dots_grid_x, dots_grid_y = np.meshgrid(dots_x, dots_y)
        ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='black', s=50, 
                  label='Campo magnético')
    else:
        # Mostrar área sombreada cuando el campo está apagado
        ax.axvspan(field_start_pos_x, X_LIM_RIGHT, alpha=0.2, color='gray', 
                  label='Campo apagado')
    
    # Elementos de la animación
    line, = ax.plot([], [], 'b-', lw=2, label='Trayectoria')
    punto, = ax.plot([], [], 'ro', markersize=8, label='Protón')
    
    # Información del estado
    info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Leyenda
    ax.legend(loc='upper right')
    
    def init():
        line.set_data([], [])
        punto.set_data([initial_pos_x], [0.0])
        campo_status = "SIN campo (B=0)" if field_off_flag else "Presiona Play para iniciar"
        info_text.set_text(campo_status)
        return line, punto, info_text
    
    def update(frame):
        line.set_data(posiciones_x[:frame+1], posiciones_y[:frame+1])
        punto.set_data([posiciones_x[frame]], [posiciones_y[frame]])
        
        # Información de zona
        if field_off_flag:
            campo = "SIN campo (B=0)"
        else:
            campo = "CON campo" if posiciones_x[frame] >= field_start_pos_x else "SIN campo"
        
        info = f'Zona: {campo}\nFrame: {frame}/{len(posiciones_x)-1}'
        info_text.set_text(info)
        
        return line, punto, info_text
    
    # Crear animación
    ani = FuncAnimation(fig, update, frames=len(posiciones_x),
                       init_func=init, blit=True, interval=20, repeat=False)
    
    # Mostrar en Streamlit
    st.pyplot(fig)
    
    # Información adicional
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("Campo Magnético B", f"{B if not field_off else 0:.3f} T")
    
    with col_info2:
        st.metric("Velocidad", f"{velocity:,} m/s")
    
    with col_info3:
        st.metric("Partículas", "Protón (q⁺)")
    
    # Créditos
    st.markdown("---")
    st.caption("© Domenico Sapone, Camila Montecinos")

# Estado de la simulación
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = None
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False

# Manejo de botones
if play_button:
    with st.spinner("Calculando trayectoria..."):
        posiciones_x, posiciones_y, times = run_simulation(B, velocity, field_off)
        st.session_state.simulation_data = (posiciones_x, posiciones_y)
        st.session_state.simulation_run = True
        st.success("¡Simulación completada!")

if reset_button:
    st.session_state.simulation_data = None
    st.session_state.simulation_run = False
    st.rerun()

# Mostrar simulación o mensaje inicial
if st.session_state.simulation_run and st.session_state.simulation_data:
    posiciones_x, posiciones_y = st.session_state.simulation_data
    create_animation(posiciones_x, posiciones_y, field_off)
else:
    # Pantalla inicial
    st.markdown("### 👆 Configura los parámetros y presiona **Play** para iniciar la simulación")
    
    # Mostrar gráfico estático inicial
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal', 'box')
    ax.set_title('Trayectoria de un protón en un campo magnético uniforme')
    ax.set_xlabel('Posición X (m)')
    ax.set_ylabel('Posición Y (m)')
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')
    
    # ESCALA FIJA
    ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
    ax.set_ylim(-Y_LIM, 0.01)
    
    # Línea divisoria
    ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--')
    
    # Puntos de campo magnético
    if not field_off:
        dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
        dots_y = np.linspace(-Y_LIM + 0.005, Y_LIM - 0.005, 6)
        dots_grid_x, dots_grid_y = np.meshgrid(dots_x, dots_y)
        ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='black', s=50)
    else:
        ax.axvspan(field_start_pos_x, X_LIM_RIGHT, alpha=0.2, color='gray')
    
    # Posición inicial
    ax.plot(initial_pos_x, 0.0, 'ro', markersize=8, label='Posición inicial')
    ax.legend()
    
    st.pyplot(fig)
    
    # Información de parámetros actuales
    st.info(f"""
    **Parámetros actuales:**
    - Campo magnético: **{B if not field_off else 0:.3f} T**
    - Velocidad inicial: **{velocity:,} m/s**
    - Tipo de partícula: **Protón**
    """)

# Información adicional
with st.expander("📚 Información Física"):
    st.markdown("""
    **Física detrás de la simulación:**
    
    - **Fuerza de Lorentz**: F = q(v × B)
    - **Carga del protón**: q = 1.602 × 10⁻¹⁹ C
    - **Masa del protón**: m = 1.672 × 10⁻²⁷ kg
    
    **Comportamiento esperado:**
    - **Campo activo**: Trayectoria circular (movimiento helicoidal proyectado)
    - **Campo nulo**: Trayectoria rectilínea
    - **Campo parcial**: Transición entre movimiento rectilíneo y circular
    """)

