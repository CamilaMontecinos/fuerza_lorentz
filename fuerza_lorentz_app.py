import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
st.title("Trayectoria de un protón en un campo magnético uniforme")

# Sidebar para controles
st.sidebar.header("Controles")

# Sliders en sidebar
B = st.sidebar.slider(
    'B (T)', 0.005, 0.01, B_initial, 0.0005, format="%.3f"
)

velocity = st.sidebar.slider(
    'Velocidad (m/s)', 5000, 22000, velocity_initial, 1000
)

# Botón para campo nulo
field_off = st.sidebar.checkbox("B = 0")

# Botones
play_button = st.sidebar.button("Play")
reset_button = st.sidebar.button("Reiniciar")

# Función de simulación (EXACTAMENTE igual a la original)
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

# Estado de la simulación
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = None

# Manejo de botones
if play_button:
    with st.spinner("Calculando trayectoria..."):
        posiciones_x, posiciones_y, times = run_simulation(B, velocity, field_off)
        st.session_state.simulation_data = (posiciones_x, posiciones_y)
        st.session_state.simulation_run = True

if reset_button:
    st.session_state.simulation_run = False
    st.session_state.simulation_data = None
    st.rerun()

# Crear el gráfico
fig, ax = plt.subplots(figsize=(6, 4))

ax.set_aspect('equal', 'box')
# ax.set_title('Trayectoria de un protón en un campo magnético uniforme')
ax.set_xlabel('Posición X')
ax.set_ylabel('Posición Y')
ax.grid(True)
ax.set_facecolor('#f0f0f0')

# ESCALA FIJA
ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
ax.set_ylim(-Y_LIM, 0.01)

# Línea divisoria
ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--')

# Puntos de campo magnético (a la derecha)
dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
dots_y = np.linspace(-Y_LIM + 0.005, -0.005, 6)
dots_grid_x, dots_grid_y = np.meshgrid(dots_x, dots_y)

# Estilo de puntos según campo
if field_off:
    ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='gray', s=50, alpha=0.25)
else:
    ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='black', s=50, alpha=1.0)

# Mostrar simulación o estado inicial
if st.session_state.simulation_run and st.session_state.simulation_data:
    posiciones_x, posiciones_y = st.session_state.simulation_data
    
    # Trazar solo la trayectoria (línea azul)
    ax.plot(posiciones_x, posiciones_y, 'b-', lw=2)
    
    # Información en el gráfico (solo campo y velocidad como antes)
    if field_off:
        campo_text = "SIN campo (B=0)"
    else:
        campo_text = f"B = {B:.3f} T"
    
    info_text = f"{campo_text}\nVelocidad = {velocity:,} m/s"
    ax.text(0.02, 0.95, info_text, transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
else:
    # Estado inicial - solo posición inicial
    ax.plot(initial_pos_x, 0.0, 'ro', markersize=8)
    ax.text(0.02, 0.95, 'Presiona Play para iniciar', transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

# Mostrar el gráfico
st.pyplot(fig)

# Créditos
st.markdown("<p style='text-align: center; color: gray;'>© Domenico Sapone, Camila Montecinos</p>", 
            unsafe_allow_html=True)


