import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

st.set_page_config(page_title="Inspección Geométrica de Batería", layout="wide")

st.title("Inspección Geométrica de Batería")
st.markdown("Comparativa entre **Coordenadas Nominales**, **Valores Medidos** y **Esquina Estimada (RL)**.")

# 1. Coordenadas Nominales
nominals = {
    'FL': (609.31, -583.30),
    'FR': (2290.48, -559.40),
    'RR': (2290.48, 558.90),
    'RL': (609.31, 535.00)
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

# Barra lateral para ajustar tolerancia interactiva
st.sidebar.header("Parámetros de Tolerancia")
tolerance = st.sidebar.slider("Zona de Tolerancia (±mm)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

col1, col2 = st.columns([2, 1])

with col1:
    fig, ax = plt.subplots(figsize=(10, 6))

    order = ['FL', 'FR', 'RR', 'RL', 'FL']

    # Contorno Nominal
    x_nom = [nominals[k][0] for k in order]
    y_nom = [nominals[k][1] for k in order]
    ax.plot(x_nom, y_nom, 'b--', label='Batería Nominal', linewidth=1.5)
    ax.scatter([nominals[k][0] for k in nominals], [nominals[k][1] for k in nominals], color='blue', zorder=5)

    # Zonas de Tolerancia (Cuadrados punteados)
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
        ax.text(x, y - 15, f"{k} Nom", fontsize=8, ha='center', color='blue')

    # Esquinas Medidas Reales
    measured_keys = ['FL', 'FR', 'RR']
    x_meas = [measured[k][0] for k in measured_keys]
    y_meas = [measured[k][1] for k in measured_keys]
    ax.scatter(x_meas, y_meas, color='red', s=60, label='Esquinas Medidas (FL, FR, RR)', zorder=6)

    # Esquina Estimada
    ax.scatter(measured['RL'][0], measured['RL'][1], color='orange', marker='^', s=80, label='Esquina Estimada (RL)', zorder=6)

    # Contorno Medido + Estimado
    x_meas_full = [measured[k][0] for k in order]
    y_meas_full = [measured[k][1] for k in order]
    ax.plot(x_meas_full, y_meas_full, 'r-', alpha=0.7, label='Geometría Medida/Estimada', linewidth=1.5)

    ax.set_title('Ploteo Geométrico: Nominal vs Medido')
    ax.set_xlabel('Coordenada X (mm)')
    ax.set_ylabel('Coordenada Y (mm)')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_aspect('equal', adjustable='datalim')

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
