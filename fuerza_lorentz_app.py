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
    format="%.3f"
)

velocity = st.sidebar.slider(
    "Velocidad Inicial (m/s)",
    min_value=5000,
    max_value=22000,
    value=velocity_initial,
    step=1000
)

# Botón simple para campo nulo
field_off = st.sidebar.checkbox("Campo magnético apagado (B = 0)", value=False)

# Botones de control
col1, col2 = st.sidebar.columns(2)
with col1:
    play_button = st.button("▶️ Ejecutar Simulación", use_container_width=True)
with col2:
    reset_button = st.button("🔄 Reiniciar", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("""
**Instrucciones:**
1. Ajusta los parámetros
2. Presiona **Ejecutar Simulación**
3. Usa el checkbox para apagar el campo
""")

# Función de simulación (la misma que tenías originalmente)
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

# Función para crear el gráfico (SIN animación)
def create_plot(posiciones_x, posiciones_y, field_off_flag, B_value, velocity_value):
    """Crea el gráfico de la trayectoria"""
    fig, ax = plt.subplots(figsize=(12, 8))  # Tamaño más grande
    
    ax.set_aspect('equal', 'box')
    ax.set_title('Trayectoria de un protón en un campo magnético uniforme', fontsize=14)
    ax.set_xlabel('Posición X (m)')
    ax.set_ylabel('Posición Y (m)')
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')
    
    # ESCALA FIJA
    ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
    ax.set_ylim(-Y_LIM, 0.01)
    
    # Línea divisoria
    ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--')
    
    # Puntos de campo magnético (a la derecha) - solo si el campo no está apagado
    if not field_off_flag:
        dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
        dots_y = np.linspace(-Y_LIM + 0.005, -0.005, 6)  # Ajustado para Y negativo
        dots_grid_x, dots_grid_y = np.meshgrid(dots_x, dots_y)
        ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='black', s=50)
    
    # Trazar la trayectoria completa
    ax.plot(posiciones_x, posiciones_y, 'b-', lw=2, label='Trayectoria')
    ax.plot(posiciones_x[0], posiciones_y[0], 'go', markersize=8, label='Inicio')
    ax.plot(posiciones_x[-1], posiciones_y[-1], 'ro', markersize=8, label='Final')
    
    # Información en el gráfico
    campo_status = "B = 0 T" if field_off_flag else f"B = {B_value:.3f} T"
    info_text = f"{campo_status}\nVelocidad = {velocity_value:,} m/s"
    ax.text(0.02, 0.95, info_text, transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax.legend()
    
    return fig

# Estado de la simulación
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = None

# Manejo de botones
if play_button:
    with st.spinner("Calculando trayectoria..."):
        posiciones_x, posiciones_y, times = run_simulation(B, velocity, field_off)
        st.session_state.simulation_data = (posiciones_x, posiciones_y, B, velocity, field_off)
        st.session_state.simulation_run = True

if reset_button:
    st.session_state.simulation_run = False
    st.session_state.simulation_data = None
    st.rerun()

# Mostrar simulación o mensaje inicial
if st.session_state.simulation_run and st.session_state.simulation_data:
    posiciones_x, posiciones_y, B_val, vel_val, field_off_val = st.session_state.simulation_data
    
    # Mostrar el gráfico
    fig = create_plot(posiciones_x, posiciones_y, field_off_val, B_val, vel_val)
    st.pyplot(fig)
    
    # Información adicional debajo del gráfico
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Campo Magnético B", f"{B_val if not field_off_val else 0:.3f} T")
    
    with col2:
        st.metric("Velocidad", f"{vel_val:,} m/s")
    
    with col3:
        st.metric("Longitud de Trayectoria", f"{len(posiciones_x)} puntos")
        
else:
    # Pantalla inicial con gráfico vacío
    st.markdown("### 👆 Configura los parámetros y presiona **Ejecutar Simulación**")
    
    # Gráfico inicial estático
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal', 'box')
    ax.set_title('Trayectoria de un protón en un campo magnético uniforme', fontsize=14)
    ax.set_xlabel('Posición X (m)')
    ax.set_ylabel('Posición Y (m)')
    ax.grid(True)
    ax.set_facecolor('#f0f0f0')
    
    # ESCALA FIJA
    ax.set_xlim(X_LIM_LEFT, X_LIM_RIGHT)
    ax.set_ylim(-Y_LIM, 0.01)
    
    # Línea divisoria
    ax.axvline(x=field_start_pos_x, color='red', linewidth=3, linestyle='--')
    
    # Puntos de campo magnético iniciales
    if not field_off:
        dots_x = np.linspace(0.005, X_LIM_RIGHT - 0.005, 6)
        dots_y = np.linspace(-Y_LIM + 0.005, -0.005, 6)
        dots_grid_x, dots_grid_y = np.meshgrid(dots_x, dots_y)
        ax.scatter(dots_grid_x, dots_grid_y, marker='.', color='black', s=50)
    
    # Posición inicial
    ax.plot(initial_pos_x, 0.0, 'go', markersize=8, label='Posición inicial')
    ax.legend()
    
    st.pyplot(fig)

# Créditos
st.markdown("---")
st.caption("© Domenico Sapone, Camila Montecinos")

