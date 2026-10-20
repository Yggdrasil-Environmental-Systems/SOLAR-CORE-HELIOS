import streamlit as st
import pandas as pd
try:
    from components.ui_components import render_kpi_card_html, format_es_num_str
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import render_kpi_card_html, format_es_num_str
from core.solar_geometry import SolarGeometry
from core.perez_transposition import PerezTransposition
from core.official_telemetry_service import OfficialTelemetryService

def render_view(site_config: dict):
    st.markdown("## ☀️ 1. Generación Fotovoltaica, Transposición Perez & PR")
    st.markdown(
        "*Modelado de radiación de la Comisión Europea (PVGIS-SARAH2), ángulo óptimo sobre plano inclinado y balance de planta.*"
    )

    lat = float(site_config.get("lat", 39.47))
    lon = float(site_config.get("lon", -0.40))
    kwp = float(site_config.get("peak_power_kwp", 500.0))

    # Control de Asimilación Telemática Oficial (ISO 23247 / Ticket 043)
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        live_telemetry = st.toggle(
            "🟢 Asimilación Telemática en Vivo (PVGIS JRC & REE)",
            value=True,
            help="Asimila en tiempo real satélites SARAH-2 de la Comisión Europea y datos del mercado eléctrico REE según ISO 23247 / Ticket 043.",
            key="v1_toggle_live_telemetry"
        )
    with col_t2:
        st.caption(format_es_num_str(f"📍 Coordenadas: `{lat:.4f}°N, {lon:.4f}°W` | Potencia: `{kwp:,.0f} kWp`"))

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    with col_ctrl1:
        tilt = st.slider("Inclinación de Módulos (β en grados)", 15, 45, int(site_config.get("tilt_deg", 30)), key="v1_slider_tilt")
    with col_ctrl2:
        azimuth = st.selectbox("Orientación (Azimut)", [0, -15, 15, -30, 30], index=0, format_func=lambda x: f"{x}° (Sur Puro)" if x == 0 else f"{x}°", key="v1_sb_azimuth")
    with col_ctrl3:
        pr_user = st.slider("Performance Ratio (PR %)", 75.0, 88.0, float(site_config.get("pr", 0.815) * 100), step=0.1, key="v1_slider_pr")

    # Ingestión telemática oficial (Digital Shadow Nivel 2)
    telemetry = OfficialTelemetryService.get_combined_telemetry(
        lat=lat,
        lon=lon,
        peak_power_kw=kwp,
        tilt_deg=float(tilt),
        azimuth_deg=float(azimuth),
        use_live=live_telemetry
    )
    pvgis = telemetry["pvgis"]
    ree = telemetry["ree"]

    # Banner de Estado Telemático
    if pvgis["is_live"]:
        st.success(
            f"🛰️ **TELEMETRÍA EN VIVO CONECTADA (NIVEL 2 INGRESS / ISO 23247):** "
            f"Asimilando datos oficiales satelitales SARAH-2 de la **Comisión Europea (JRC)** y mercado de **Red Eléctrica de España (REE)**. "
            f"Latencia: `{pvgis['latency_ms']:.0f} ms` | Estado: **ONLINE**"
        )
    else:
        st.info(
            f"🛡️ **MODO SEGURO AIR-GAP ({pvgis['status']}):** {pvgis['source']} — {pvgis['nota']}"
        )

    # Métricas y KPIs
    poa_annual = pvgis["annual_poa_kwh_m2"]
    annual_generation_mwh = pvgis["annual_generation_mwh"]
    spec_yield = pvgis["specific_yield_kwh_kwp"]
    avoided_co2_tons = telemetry["avoided_co2_tons"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card_html(
            "Potencia de Pico",
            f"{kwp:,.0f} kWp",
            "Campo generador DC",
            "TOPCon",
            True
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card_html(
            "Irradiación en Plano (POA)",
            f"{poa_annual:,.0f} kWh/m²",
            f"Fuente: {pvgis['source'][:20]}",
            f"β = {tilt}°",
            True
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card_html(
            "Generación Anual Neta",
            f"{annual_generation_mwh:,.1f} MWh",
            f"Yield: {spec_yield:,.0f} kWh/kWp",
            f"PR: {pr_user:.1f}%",
            True
        ), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card_html(
            "Emisiones Evitadas",
            f"{avoided_co2_tons:,.1f} tCO₂e",
            f"Factor Mix: {ree['mix_emission_factor_kg_kwh']:.3f} kg/kWh",
            "Descarbonización",
            True
        ), unsafe_allow_html=True)

    # Mini-panel de mercado eléctrico oficial REE / OMIE
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="Precio Pool Spot Oficial (REE)",
            value=format_es_num_str(f"{ree['market_pool_price_avg_eur_mwh']:.2f} €/MWh"),
            delta=format_es_num_str(f"Rango: {ree.get('market_pool_price_min_eur_mwh', 0):.1f} - {ree.get('market_pool_price_max_eur_mwh', 0):.1f} €")
        )
    with col_m2:
        st.metric(
            label="Ingreso Bruto Anual Estimado",
            value=format_es_num_str(f"{telemetry['estimated_annual_revenue_eur']:,.0f} €"),
            delta="Captura solar en mercado diario"
        )
    with col_m3:
        st.metric(
            label="Horas Precio Cero / Negativo",
            value=f"{ree.get('zero_or_negative_price_hours', 0)} h/día",
            delta="Riesgo Canibalización (Curva Pato)"
        )

    st.markdown("### 📊 Perfil de Generación Mensual Auditado")
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    gen_mes = pvgis["monthly_generation_mwh"]

    df_mes = pd.DataFrame({"Mes": meses, "Generación (MWh)": [round(g, 1) for g in gen_mes]})
    st.bar_chart(df_mes.set_index("Mes"))

    with st.expander("🔬 Desglose de Pérdidas del Performance Ratio (PR 81,5%)"):
        st.markdown(r"""
        * **Pérdidas Térmicas por Temperatura de Célula ($-8,2\%$):** Coeficiente de temperatura $\gamma_{P_{\text{mp}}} = -0,34\%/^\circ\text{C}$ para tecnología n-TOPCon.
        * **Pérdidas Ópticas por Reflexión de Fresnel ($-2,1\%$):** Reflexión angular en vidrio frontal antirreflectante.
        * **Pérdidas por Ensuciamiento y Polvo ($-2,8\%$):** Compensado con protocolo de limpieza semestral programada en OPEX.
        * **Pérdidas Óhmicas de Cableado DC/AC ($-1,2\%$):** Caída de tensión dimensionada a plena carga $\Delta V \le 1,2\%$.
        * **Pérdidas del Inversor SOFAR ($-1,8\%$):** Rendimiento ponderado europeo $\eta_{\text{euro}} \ge 98,4\%$.
        * **Pérdidas de Transformador a MT ($-1,1\%$):** Centro de transformación elevador $0,4 / 20\text{ kV}$.
        * **Disponibilidad & Mismatch Mitigado ($-1,3\%$):** Seguidores multi-MPPT independientes.
        """)
