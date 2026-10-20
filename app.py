# -*- coding: utf-8 -*-
"""
SOLAR-CORE: HELIOS · OPEN-CORE PUBLIC EDITION
=============================================
Ecosistema: Yggdrasil Environmental Systems
Director Técnico & Autor: Kelvin Jesús Flores Yarihuaman (MECES Nivel 3 · EQF Level 7)
Habilitación Pericial: Art. 335 Ley de Enjuiciamiento Civil (LEC) · ISO/IEC 27037
Licencia: Creative Commons Attribution-NonCommercial 4.0 (CC-BY-NC 4.0) / MIT Open-Core

Marco Regulatorio Auditado (116 Normas en compliance/regulatory_dna.json):
- Ley 21/2013, de Evaluación Ambiental & Directiva (UE) 2023/2413 (RED III)
- Real Decreto 384/2023 & RD 369/2023 (Servidumbres Aeronáuticas AESA · Glint & Glare SGHAT)
- Real Decreto 102/2011 & Directiva 2008/50/CE (Calidad del Aire · Dispersión PM10 en Obra)
- Reglamento (UE) 2024/1689 (EU AI Act Art. 14 HITL · DSS Nivel 2 ISO 23247)
"""

import sys
import math
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT_DIR = Path(__file__).resolve().parent
if (ROOT_DIR / "core").exists():
    PROJECT_ROOT = ROOT_DIR
else:
    PROJECT_ROOT = ROOT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
APP_SUBDIR = PROJECT_ROOT / "app"
if APP_SUBDIR.exists() and str(APP_SUBDIR) not in sys.path:
    sys.path.insert(0, str(APP_SUBDIR))

try:
    import freyja_ui
except Exception:
    try:
        from components import freyja_ui
    except Exception:
        try:
            from app.components import freyja_ui
        except Exception:
            freyja_ui = None

try:
    from components.ui_components import load_catalog_sites, render_kpi_card_html
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import load_catalog_sites, render_kpi_card_html
from core.official_telemetry_service import OfficialTelemetryService
from core.multi_mppt_engine import MultiMPPTEngine
from core.eia_buffer_checker import EIABufferChecker
from core.aeronautical_servitudes_glare import AeronauticalServitudesGlare
from core.air_dispersion_gauss import GaussianAirDispersion
from core.financial_dcf_engine import FinancialDCFEngine
from neural_lab.models import HeliosSurrogateInference
from physics.sentinel_sidecar import PhysicsSentinelSidecar

st.set_page_config(
    page_title="HELIOS | Open-Core DSS Solar Fotovoltaica, TOPCon & EIA · Ley 21/2013",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if freyja_ui and hasattr(freyja_ui, "render_ecosystem_topbar"):
    freyja_ui.render_ecosystem_topbar("helios")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@600;700;800&display=swap');

    .stApp {
        background-color: #070B12;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    .c2-header {
        background: linear-gradient(135deg, rgba(11,18,31,0.96) 0%, rgba(120,83,13,0.22) 100%);
        border: 1px solid rgba(255, 214, 10, 0.35);
        border-left: 4px solid #FFD60A;
        border-radius: 12px;
        padding: 20px 26px;
        margin-bottom: 18px;
    }
    .helios-card {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 0.76rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 1.45rem; color: #F8FAFC; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin: 4px 0; }
    .kpi-subtext { font-size: 0.72rem; color: #64748B; }
    .badge-compliant { background: rgba(16,185,129,0.15); border: 1px solid #10B981; color: #34D399; padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; }
    .badge-alert { background: rgba(239,68,68,0.15); border: 1px solid #EF4444; color: #F87171; padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Sidebar Táctico Open-Core
with st.sidebar:
    icon_path = PROJECT_ROOT / "assets" / "app_icon.png"
    if icon_path.exists():
        st.image(str(icon_path), width=90)

    st.markdown("### ☀️ HELIOS")
    st.markdown("<div style='font-size: 0.85rem; color: #FFD60A; font-weight: 700; letter-spacing: 0.5px;'>SISTEMA DE SOPORTE A LA DECISIÓN (DSS)</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.78rem; color: #94A3B8; margin-top: 2px;'>Gemelo Fotovoltaico Paramétrico, TOPCon & EIA · Ley 21/2013</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.75rem; color: #64748B; margin-top: 2px;'>Yggdrasil Environmental Systems · Madrid</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style="background: rgba(120, 83, 13, 0.25); border: 1.5px solid rgba(255, 214, 10, 0.45); border-radius: 8px; padding: 12px 14px; margin-bottom: 14px;">
        <div style="font-size: 0.70rem; color: #FFD60A; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; font-family: 'JetBrains Mono', monospace;">MODO DE OPERACIÓN</div>
        <div style="font-size: 0.95rem; color: #F8FAFC; font-weight: 800; margin-top: 3px;">🔓 OPEN-CORE EDICIÓN PÚBLICA</div>
        <div style="font-size: 0.74rem; color: #94A3B8; margin-top: 4px; line-height: 1.35;">Transformer PINN (11,41M params) · Perez (1990) & Faiman (2008) · Telemetría PVGIS JRC</div>
    </div>
    """, unsafe_allow_html=True)

    sites = load_catalog_sites()
    site_names = [s["display_name"] for s in sites] + ["🌐 Simulador Paramétrico Personalizado (Multi-MW + Telemetría PVGIS)"]
    selected_option = st.selectbox("Seleccionar Escenario de Proyecto:", site_names, index=0, key="hf_sb_site")

    if "Simulador Paramétrico" in selected_option or "Cono Paramétrico" in selected_option:
        c_lat = st.number_input("Latitud (°N)", 36.0, 44.0, 40.24, step=0.05)
        c_lon = st.number_input("Longitud (°W/E)", -9.0, 4.0, -3.56, step=0.05)
        c_kwp = st.number_input("Potencia Pico (kWp)", 10.0, 500000.0, 4950.0, step=50.0)
        c_tilt = st.slider("Inclinación β (grados)", 10, 45, 32)
        c_ppa = st.number_input("Precio PPA (€/MWh)", 30.0, 100.0, 54.0, step=1.0)
        active_site = {
            "site_id": "PROYECTO-PARAMETRICO-ES",
            "display_name": f"Proyecto Fotovoltaico Personalizado ({c_kwp:,.0f} kWp | {c_lat:.2f}°N, {c_lon:.2f}°E)".replace(',', ' ').replace('.', ','),
            "region": "Simulación Paramétrica Nacional (España)",
            "lat": c_lat, "lon": c_lon, "peak_power_kwp": c_kwp, "tilt_deg": c_tilt,
            "azimuth_deg": 0.0, "ghi_kwh_m2": 1760.0, "specific_yield_kwh_kwp": 1690.0,
            "pr": 0.835, "capex_wp": 0.68, "opex_kwp_year": 8.8, "ppa_price_eur_mwh": c_ppa,
            "is_enterprise": False
        }
    else:
        active_site = dict(next((s for s in sites if s["display_name"] == selected_option), sites[0]))
        active_site["is_enterprise"] = False

    st.markdown("#### 📍 Ficha Técnica del Emplazamiento")
    st.markdown(
        f"• **ID:** `{active_site['site_id']}`<br>"
        f"• **Ámbito:** {active_site.get('region', 'España')}<br>"
        f"• **Coordenadas:** `{active_site['lat']:.2f}°N, {active_site['lon']:.2f}°E`".replace('.', ',') + "<br>"
        f"• **Potencia Pico:** `{active_site['peak_power_kwp']:,.0f} kWp` ({active_site['peak_power_kwp']/1000.0:.2f} MWp)".replace(',', ' ').replace('.', ','),
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("""
    👑 **Director Técnico Titular:**<br>
    **Kelvin Jesús Flores Yarihuaman**<br>
    _Máster Universitario en Ing. y Gestión Ambiental_<br>
    _MECES Nivel 3 · EQF Level 7_<br>
    _Art. 335 LEC / ISO 27037_<br>
    <div style="margin-top: 10px; display: flex; flex-direction: column; gap: 6px;">
        <a href="https://www.linkedin.com/in/kelvinflores-ingenieria" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #00D2FF; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; background: rgba(0, 210, 255, 0.08); border: 1px solid rgba(0, 210, 255, 0.3); padding: 5px 8px; border-radius: 6px;">
            <span>💼</span> <span>LinkedIn: Kelvin Flores</span>
        </a>
        <a href="https://www.linkedin.com/company/yggdrasil-environmental-systems" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #00F5A0; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; background: rgba(0, 245, 160, 0.08); border: 1px solid rgba(0, 245, 160, 0.3); padding: 5px 8px; border-radius: 6px;">
            <span>🏢</span> <span>LinkedIn: Yggdrasil Systems</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="c2-header">
    <div style="font-size: 0.78rem; font-family: monospace; color: #FFD60A; letter-spacing: 0.14em; font-weight: 700;">
        SOLAR-CORE: HELIOS · GEMELO FOTOVOLTAICO PARAMÉTRICO & MOTOR AMBIENTAL (EDICIÓN OPEN-CORE)
    </div>
    <h1 style="margin: 4px 0 6px 0; font-size: 2.05rem; font-weight: 800; color: #FFFFFF;">
        ☀️ HELIOS · {active_site['display_name']}
    </h1>
    <div style="color: #94A3B8; font-size: 0.92rem;">
        Gemelo Fotovoltaico Paramétrico (ISO 23247 Nivel 2), simulación n-TOPCon, evaluación ambiental preventiva (Ley 21/2013 & RED III) y red neuronal informada por la física (PINN).
    </div>
</div>
""", unsafe_allow_html=True)

try:
    from views import view_1_cockpit_generacion_pvgis as v1
    from views import view_2_inversores_mppt_topcon as v2
    from views import view_3_evaluacion_ambiental_eia as v3
    from views import view_4_dispersion_aire_pm10 as v4
    from views import view_5_project_finance_roi as v5
    from views import view_6_neural_lab_inference as v6
except (ImportError, ModuleNotFoundError):
    from app.views import view_1_cockpit_generacion_pvgis as v1
    from app.views import view_2_inversores_mppt_topcon as v2
    from app.views import view_3_evaluacion_ambiental_eia as v3
    from app.views import view_4_dispersion_aire_pm10 as v4
    from app.views import view_5_project_finance_roi as v5
    from app.views import view_6_neural_lab_inference as v6

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "☀️ 1. Generación Solar & PR (PVGIS)",
    "⚡ 2. Inversores Multi-MPPT & TOPCon",
    "🌿 3. Evaluación Ambiental EIA (Ley 21/2013)",
    "💨 4. Dispersión Atmosférica (PM10 Obra)",
    "💰 5. Project Finance DCF (25 Años)",
    "🧠 6. Modelo PINN & Validación Física"
])

with tab1:
    v1.render_view(active_site)
with tab2:
    v2.render_view(active_site)
with tab3:
    v3.render_view(active_site)
with tab4:
    v4.render_view(active_site)
with tab5:
    v5.render_view(active_site)
with tab6:
    v6.render_view(active_site)

st.markdown("---")
if freyja_ui and hasattr(freyja_ui, "render_legal_shield"):
    freyja_ui.render_legal_shield(
        core_id="helios",
        doc_ref="HELIOS-SOLAR-EIA-MECES3-2026-v1",
        cert_hash="SHA256:b453a51957d12263c918548ade3cdff244a404c3b344d39ef06777716227357f"
    )
if freyja_ui and hasattr(freyja_ui, "render_scientific_dna_shield"):
    freyja_ui.render_scientific_dna_shield(core_id="helios")
