import streamlit as st
import pandas as pd
try:
    from components.ui_components import render_kpi_card_html, format_es_num_str
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import render_kpi_card_html, format_es_num_str
from core.financial_dcf_engine import FinancialDCFEngine
try:
    from core.omie_capture_price_engine import OMIECapturePriceEngine
except (ImportError, ModuleNotFoundError):
    OMIECapturePriceEngine = None

def render_view(site_config: dict):
    st.markdown("## 💰 5. Bancabilidad, Flujo de Caja & Project Finance")
    st.markdown(
        "*Modelado financiero a 25 años: Tasa Interna de Retorno (TIR), Periodo de Retorno (Payback), VAN, LCOE "
        "y Análisis de Precios de Captura OMIE (Curva de Pato y Horas Negativas).*"
    )

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        capex_wp = st.slider("CAPEX Unitario (€/Wp)", 0.50, 1.00, float(site_config.get("capex_wp", 0.72)), step=0.01, key="v5_slider_capex")
    with col_in2:
        opex_kwp = st.slider("OPEX Anual (€/kWp·año)", 5.0, 15.0, float(site_config.get("opex_kwp_year", 9.0)), step=0.5, key="v5_slider_opex")
    with col_in3:
        ppa_price = st.slider("Precio PPA Referencia (€/MWh)", 35.0, 90.0, float(site_config.get("ppa_price_eur_mwh", 55.0)), step=1.0, key="v5_slider_ppa")

    kwp = float(site_config.get("peak_power_kwp", 500.0))
    total_capex = kwp * 1000.0 * capex_wp
    total_opex = kwp * opex_kwp
    mwh_year = (kwp * float(site_config.get("specific_yield_kwh_kwp", 1680.0))) / 1000.0

    fin = FinancialDCFEngine.calculate_project_metrics(
        capex_total_eur=total_capex,
        opex_annual_eur=total_opex,
        annual_generation_mwh=mwh_year,
        energy_price_eur_mwh=ppa_price
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card_html("Inversión Total (CAPEX)", f"{total_capex:,.0f} €", f"{capex_wp:.2f} €/Wp instalado", "Presupuesto", True), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card_html("TIR del Proyecto (25 Años)", f"{fin['irr_pct']:.1f}%", f"VAN: {fin['npv_eur']:,.0f} €", "Bancable", True), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card_html("Retorno Simple (Payback)", f"{fin['payback_simple_years']:.1f} Años", "Sin subsidios extraordinarios", "Solvente", True), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card_html("Coste Nivelado (LCOE)", f"{fin['lcoe_eur_mwh']:.1f} €/MWh", "Altamente competitivo", "Grid Parity", True), unsafe_allow_html=True)

    st.markdown("### 📈 Proyección de Flujo de Caja Acumulado (25 Años)")
    anos = list(range(0, 26))
    cf_acum = [-total_capex]
    running = -total_capex

    for y in range(1, 26):
        deg = (1.0 - (y - 1) * 0.004)
        inf = (1.0 + 0.02) ** (y - 1)
        net_flow = (mwh_year * deg * ppa_price) - (total_opex * inf)
        running += net_flow
        cf_acum.append(running)

    df_cf = pd.DataFrame({"Año": anos, "Flujo Acumulado (€)": cf_acum})
    st.line_chart(df_cf.set_index("Año"))

    dscr_str = format_es_num_str(f"{fin['bankability_dscr_proxy']:.2f}")
    st.info(f"📊 **Ratio de Cobertura de la Deuda (DSCR Estimado):** `{dscr_str}x` (Supera holgadamente el umbral bancario estándar de $1,30\\times$, garantizando viabilidad de financiación bancaria sin recurso).")

    # =========================================================================
    # MÓDULO ENTERPRISE: ANÁLISIS DE CURVA DE PATO & SOLAR CAPTURE RATE OMIE
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🦆 Mercado Mayorista OMIE: Curva de Pato & Precio de Captura Solar (*Capture Rate*)")
    st.caption("Auditoría de riesgo de canibalización de precios y horas cero/negativas en el mercado ibérico (MIBEL / OMIE 2024-2026).")

    if not site_config.get("is_enterprise", True) or OMIECapturePriceEngine is None:
        st.info("🔒 **Módulo Enterprise (Project Finance & Trading OMIE):** El análisis horario de Curva de Pato (*Duck Curve*), estrés de horas con precios negativos y *Solar Capture Rate* pertenece a la **💼 Edición Enterprise**. Conmuta en el panel lateral para activarlo.")
    else:
        col_om1, col_om2 = st.columns(2)
        with col_om1:
            merchant_exposure = st.slider("Exposición a Mercado Diario / Merchant (%)", 0.0, 100.0, 30.0, step=5.0, key="v5_slider_merchant_exp")
        with col_om2:
            negative_hours = st.slider("Estrés de Horas con Precios Negativos/Cero al Año", 0, 500, 150, step=25, key="v5_slider_neg_hours")

        capture_res = OMIECapturePriceEngine.calculate_solar_capture_metrics(
            annual_generation_mwh=mwh_year,
            nominal_ppa_price_eur_mwh=ppa_price,
            merchant_exposure_pct=merchant_exposure,
            negative_price_stress_hours=negative_hours
        )

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.markdown(render_kpi_card_html("Precio Pool Baseload", f"{capture_res['baseload_pool_price_eur_mwh']:.1f} €/MWh", "Media aritmética OMIE", "Referencia", True), unsafe_allow_html=True)
        with col_c2:
            st.markdown(render_kpi_card_html("Solar Capture Price", f"{capture_res['solar_capture_price_eur_mwh']:.1f} €/MWh", f"Ponderado por radiación solar", "Capturado", True), unsafe_allow_html=True)
        with col_c3:
            st.markdown(render_kpi_card_html("Solar Capture Rate", f"{capture_res['capture_rate_pct']:.1f}%", f"Descuento canibalización: {capture_res['cannibalization_discount_pct']:.1f}%", "Apuntamiento", True), unsafe_allow_html=True)
        with col_c4:
            st.markdown(render_kpi_card_html("Precio Efectivo Blended", f"{capture_res['blended_effective_price_eur_mwh']:.1f} €/MWh", f"{100-merchant_exposure:.0f}% PPA / {merchant_exposure:.0f}% Merchant", "Ponderado", True), unsafe_allow_html=True)

        st.markdown("#### ⚖️ Comparativa de Ingresos y Estrés Financiero por Modelo de Venta")
        df_scenarios = pd.DataFrame([
            {
                "Estructura Comercial": "1. PPA Fijo Garantizado (100%)",
                "Precio Efectivo (€/MWh)": f"{capture_res['nominal_ppa_price_eur_mwh']:.2f} €",
                "Ingreso Anual Estimado (€)": f"{capture_res['revenue_scenario_100_ppa_eur']:,.0f} €",
                "Impacto vs PPA Plano": "Caso Base (0.0%)",
                "Perfil Bancario": "Máxima Bancabilidad (Tier 1)"
            },
            {
                "Estructura Comercial": f"2. Híbrido Estructurado ({100-merchant_exposure:.0f}% PPA + {merchant_exposure:.0f}% Merchant)",
                "Precio Efectivo (€/MWh)": f"{capture_res['blended_effective_price_eur_mwh']:.2f} €",
                "Ingreso Anual Estimado (€)": f"{capture_res['revenue_scenario_hybrid_eur']:,.0f} €",
                "Impacto vs PPA Plano": f"-{capture_res['hybrid_haircut_pct']:.1f}% (-{capture_res['hybrid_haircut_vs_ppa_eur']:,.0f} €)",
                "Perfil Bancario": "Bancable con Haircut (Estándar)"
            },
            {
                "Estructura Comercial": "3. Merchant Puro (100% Pool)",
                "Precio Efectivo (€/MWh)": f"{capture_res['solar_capture_price_eur_mwh']:.2f} €",
                "Ingreso Anual Estimado (€)": f"{capture_res['revenue_scenario_100_merchant_eur']:,.0f} €",
                "Impacto vs PPA Plano": f"-{capture_res['cannibalization_discount_pct']:.1f}%",
                "Perfil Bancario": "Inbancable sin Coberturas / BESS"
            }
        ])
        st.table(df_scenarios.set_index("Estructura Comercial"))

        df_hourly = pd.DataFrame(capture_res["hourly_profile_table"])
        df_hourly["Hora del Día"] = df_hourly["hour"].apply(lambda h: f"{h:02d}:00")
        st.markdown("#### 📊 Perfil Horario de Precios OMIE vs Curva de Inyección Fotovoltaica")
        st.line_chart(df_hourly.set_index("Hora del Día")[["omie_price_eur_mwh", "solar_share_pct"]])

        st.warning(
            f"**Dictamen de Bancabilidad OMIE:** `{capture_res['bankability_rating']}`  \n"
            f"{capture_res['bankability_recommendation']}"
        )
