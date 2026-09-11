import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

st.set_page_config(page_title="Inspección Geométrica de Batería", layout="wide")

st.title("Inspección Geométrica de Batería")
st.markdown("Comparativa entre **Coordenadas Nominales**, **Valores Medidos** y **Esquina Estimada (RL)** respetando el sistema de coordenadas de la imagen.")

# 1. Coordenadas Nominales según orientación de la imagen:
# Eje X: Horizontal hacia la derecha (de 609.31 mm a 2290.48 mm)
# Eje Y: Negativo ARRIBA (~ -583 mm), Positivo ABAJO (~ +558 mm)
nominals = {
    'FL': (609.31, -583.30),   # Superior Izquierda
    'FR': (2290.48, -559.40),  # Superior Derecha
    'RL': (609.31, 535.00),    # Inferior Izquierda (Faltante)
    'RR': (2290.48, 558.90)    # Inferior Derecha
}

# 2. Deltas medidos (mm)
deltas = {
    'FL': (3.342301, 1.745206),
    'FR': (-3.196817, 2.564179),
    'RR': (-3.363002, -5.858942)
}

# 3. Estimación de Delta para RL (traslación/cuerpo rígido)
delta_RL_x = deltas['FL'][0] + deltas['RR'][0] - deltas['FR'][0]
delta_RL_y = deltas['FL'][1] + deltas['RR'][1] - deltas['FR'][1]
deltas['RL'] = (delta_RL_x, delta_RL_y)

# 4. Cálculo de Coordenadas Medidas/Estimadas
measured = {k: (nominals[k][0] + deltas[k][0], nominals[k][1] + deltas[k][1]) for k in nominals}

# Sidebar inputs
st.sidebar.header("Opciones de Visualización")
view_mode = st.sidebar.radio("Vista", ["General (Toda la batería)", "Zoom a Esquinas (2x2)", "Detalle Esquina Individual"])
tolerance = st.sidebar.slider("Tolerancia (±mm)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

selected_corner = None
if view_mode == "Detalle Esquina Individual":
    selected_corner = st.sidebar.selectbox("Selecciona la Esquina", ["FL", "FR", "RL", "RR"])

zoom_margin = st.sidebar.slider("Margen de Zoom (mm)", min_value=2, max_value=20, value=8, step=1)

def apply_coordinate_system(ax):
    # Invertir el eje Y para alinear con la representación CAD/CMM (Y negativo arriba, positivo abajo)
    ax.invert_yaxis()

def plot_corner_detail(ax, k, show_legend=False):
    x_nom, y_nom = nominals[k]
    x_meas, y_meas = measured[k]
    
    # Caja de tolerancia
    rect = patches.Rectangle(
        (x_nom - tolerance, y_nom - tolerance), 
        tolerance * 2, 
        tolerance * 2, 
        linewidth=1.5, 
        edgecolor='gray', 
        facecolor='lightgray', 
        alpha=0.3,
        linestyle='--', 
        label=f'Tolerancia (±{tolerance}mm)' if show_legend else ""
    )
    ax.add_patch(rect)
    
    # Punto nominal
    ax.scatter(x_nom, y_nom, color='blue', s=80, label='Nominal' if show_legend else "", zorder=5)
    
    # Punto medido o estimado
    is_est = (k == 'RL')
    color_m = 'orange' if is_est else 'red'
    marker_m = '^' if is_est else 'o'
    label_m = f"Esquina {'Estimada' if is_est else 'Medida'}"
    
    ax.scatter(x_meas, y_meas, color=color_m, marker=marker_m, s=100, label=label_m if show_legend else "", zorder=6)
    
    # Vector de desviación
    ax.annotate('', xy=(x_meas, y_meas), xytext=(x_nom, y_nom),
                arrowprops=dict(arrowstyle="->", color=color_m, lw=1.5))
    
    # Límites del Zoom
    ax.set_xlim(x_nom - zoom_margin, x_nom + zoom_margin)
    ax.set_ylim(y_nom - zoom_margin, y_nom + zoom_margin)
    
    apply_coordinate_system(ax)
    
    ax.set_title(f"Esquina {k} ({'Estimada' if is_est else 'Medida'}) | ΔX={deltas[k][0]:+.2f}, ΔY={deltas[k][1]:+.2f}", fontsize=9, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal', adjustable='datalim')

col1, col2 = st.columns([2, 1])

with col1:
    if view_mode == "General (Toda la batería)":
        fig, ax = plt.subplots(figsize=(10, 6))
        order = ['FL', 'FR', 'RR', 'RL', 'FL']

        x_nom = [nominals[k][0] for k in order]
        y_nom = [nominals[k][1] for k in order]
        ax.plot(x_nom, y_nom, 'b--', label='Batería Nominal', linewidth=1.5)
        ax.scatter([nominals[k][0] for k in nominals], [nominals[k][1] for k in nominals], color='blue', zorder=5)

        for k, (x, y) in nominals.items():
            rect = patches.Rectangle(
                (x - tolerance, y - tolerance), 
                tolerance * 2, 
                tolerance * 2, 
                linewidth=1.2, 
                edgecolor='gray', 
                facecolor='none', 
                linestyle=':', 
                label=f'Tolerancia (±{tolerance}mm)' if k == 'FL' else ""
            )
            ax.add_patch(rect)
            y_offset = -25 if nominals[k][1] < 0 else 25
            ax.text(x, y + y_offset, f"{k} Nom", fontsize=8, ha='center', color='blue')

        measured_keys = ['FL', 'FR', 'RR']
        x_meas = [measured[k][0] for k in measured_keys]
        y_meas = [measured[k][1] for k in measured_keys]
        ax.scatter(x_meas, y_meas, color='red', s=60, label='Esquinas Medidas', zorder=6)
        ax.scatter(measured['RL'][0], measured['RL'][1], color='orange', marker='^', s=80, label='Esquina Estimada (RL)', zorder=6)

        x_meas_full = [measured[k][0] for k in order]
        y_meas_full = [measured[k][1] for k in order]
        ax.plot(x_meas_full, y_meas_full, 'r-', alpha=0.7, label='Geometría Medida/Estimada', linewidth=1.5)

        apply_coordinate_system(ax)

        ax.set_title('Ploteo General Batería (Sistema de Coordenadas CAD)')
        ax.set_xlabel('X (mm) →')
        ax.set_ylabel('← Y (mm) [Negativo Arriba / Positivo Abajo]')
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='lower right', fontsize=8)
        ax.set_aspect('equal', adjustable='datalim')

        st.pyplot(fig)

    elif view_mode == "Zoom a Esquinas (2x2)":
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        # Layout coincidente con la posición espacial de la batería
        corners_grid = [['FL', 'FR'], ['RL', 'RR']]
        for i in range(2):
            for j in range(2):
                k = corners_grid[i][j]
                plot_corner_detail(axes[i, j], k, show_legend=(i==0 and j==0))
        plt.tight_layout()
        st.pyplot(fig)

    elif view_mode == "Detalle Esquina Individual":
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_corner_detail(ax, selected_corner, show_legend=True)
        ax.set_xlabel('X (mm) →')
        ax.set_ylabel('Y (mm)')
        st.pyplot(fig)

with col2:
    st.subheader("Resumen de Coordenadas")
    table_data = []
    for k in ['FL', 'FR', 'RL', 'RR']:
        is_est = "Estimado" if k == 'RL' else "Medido"
        table_data.append({
            "Esquina": k,
            "Estado": is_est,
            "Nom X": nominals[k][0],
            "Nom Y": nominals[k][1],
            "Delta X": round(deltas[k][0], 3),
            "Delta Y": round(deltas[k][1], 3),
            "Actual X": round(measured[k][0], 3),
            "Actual Y": round(measured[k][1], 3),
        })
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
