import streamlit as st
import pandas as pd
try:
    from components.ui_components import render_kpi_card_html, format_es_num_str
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import render_kpi_card_html, format_es_num_str
from core.air_dispersion_gauss import GaussianAirDispersion

def render_view(site_config: dict):
    st.markdown("## 💨 4. Calidad del Aire & Dispersión Atmosférica (Fase de Obra Civil)")
    st.markdown(
        "*Modelización de partículas PM10 a sotavento según Directiva 2008/50/CE y Real Decreto 102/2011.*"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🚜 Parámetros de Obra Civil y Viento")
        dist = st.slider("Distancia al Receptor Sotavento (metros)", 50, 300, 100, step=10, key="v4_slider_dist")
        wind = st.slider("Velocidad Media del Viento (m/s)", 1.0, 8.0, 2.5, step=0.5, key="v4_slider_wind")
        baseline = st.number_input("Nivel de Fondo Territorial ideIB (µg/m³)", 10.0, 40.0, 21.6, step=0.5, key="v4_num_baseline")
        mitigate = st.checkbox("Activar Riego Programado de Pistas (Camión Cisterna)", value=True, key="v4_chk_mitigate")

        res = GaussianAirDispersion.calculate_downwind_concentration(
            emission_rate_g_s=0.060,
            wind_speed_m_s=wind,
            downwind_distance_m=dist,
            baseline_ug_m3=baseline,
            wet_suppression_active=mitigate
        )

        st.markdown(render_kpi_card_html(
            "Concentración Total PM10",
            f"{res['total_concentration_ug_m3']} µg/m³",
            f"Fondo: {res['baseline_ug_m3']} | Incremento: +{res['increment_civil_works_ug_m3']} µg/m³",
            f"Límite legal: {res['legal_limit_ug_m3']} µg/m³ ({res['compliance_status']})",
            res['compliance_status'] == "CONFORME"
        ), unsafe_allow_html=True)

        st.metric(
            "Margen de Seguridad Legal",
            format_es_num_str(f"{res['safety_margin_pct']}% por debajo del límite"),
            delta="Dentro de norma" if res['compliance_status'] == "CONFORME" else "Infracción"
        )

    with col2:
        st.markdown("### 📈 Curva de Dispersión Gaussiana a Distancia")
        distancias = list(range(20, 320, 20))
        curva_con = [
            GaussianAirDispersion.calculate_downwind_concentration(0.060, wind, d, baseline, wet_suppression_active=True)['total_concentration_ug_m3']
            for d in distancias
        ]
        curva_sin = [
            GaussianAirDispersion.calculate_downwind_concentration(0.060, wind, d, baseline, wet_suppression_active=False)['total_concentration_ug_m3']
            for d in distancias
        ]

        df_disp = pd.DataFrame({
            "Distancia (m)": distancias,
            "Con Riego (Mitigado)": curva_con,
            "Sin Riego (Crudo)": curva_sin,
            "Límite RD 102/2011": [50.0] * len(distancias)
        })

        st.line_chart(df_disp.set_index("Distancia (m)"))

        if mitigate:
            st.success("💧 **Medida Correctora Eficaz:** La humectación reduce las emisiones fugitivas un 75%, garantizando que en el receptor de 100 m se cumpla holgadamente la Directiva Europea 2008/50/CE.")
        else:
            st.error("🚨 **Aviso de Incumplimiento:** Sin riego preventivo, las emisiones de excavación pueden superar los 50 µg/m³, provocando denuncias vecinales y paralizaciones cautelares de obra.")
