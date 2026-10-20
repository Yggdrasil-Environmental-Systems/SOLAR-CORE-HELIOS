import streamlit as st
try:
    from components.ui_components import render_kpi_card_html, format_es_num_str
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import render_kpi_card_html, format_es_num_str
from core.multi_mppt_engine import MultiMPPTEngine
try:
    from core.grid_curtailment_engine import GridCurtailmentEngine
except (ImportError, ModuleNotFoundError):
    GridCurtailmentEngine = None

def render_view(site_config: dict):
    st.markdown("## ⚡ 2. Electrónica de Potencia Multi-MPPT, Red MT (SCR) & Células n-TOPCon")
    st.markdown(
        "*Mitigación de desajuste de strings, recorte por clipping, saturación de nudo MT (SCR < 2,0), "
        "restricciones técnicas de red (Curtailment P.O. 3.2 REE) y blindaje PID (Directiva RED III / RD 244/2019).*"
    )

    kwp = float(site_config.get("peak_power_kwp", 500.0))
    p_evac_mw = kwp / 1000.0
    mwh_year = (kwp * float(site_config.get("specific_yield_kwh_kwp", 1680.0))) / 1000.0

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎛️ Sombreado Parcial, Multi-MPPT & Pérdidas por Clipping")
        st.caption("Simulación de sombreado orográfico / suciedad diferencial sobre 4 canales MPPT:")
        s1 = st.slider("Irradiancia MPPT 1 (%)", 60, 100, 100, key="v2_slider_s1") / 100.0
        s2 = st.slider("Irradiancia MPPT 2 (%)", 60, 100, 95, key="v2_slider_s2") / 100.0
        s3 = st.slider("Irradiancia MPPT 3 (%)", 60, 100, 80, key="v2_slider_s3") / 100.0
        s4 = st.slider("Irradiancia MPPT 4 (%)", 60, 100, 100, key="v2_slider_s4") / 100.0

        engine = MultiMPPTEngine(num_mppt_trackers=4, inverter_euro_efficiency=0.984, dc_ac_ratio=1.11)
        res = engine.process_string_power(kwp, [s1, s2, s3, s4])

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Potencia DC Cosechada", format_es_num_str(f"{res['dc_power_harvested_kw']} kW"), delta=format_es_num_str(f"{res['mismatch_mitigated_kw']} kW salvados vs. Central"))
            st.metric("Potencia AC Inyectada", format_es_num_str(f"{res['ac_power_output_kw']} kW"), delta=format_es_num_str(f"Capacidad Inversor: {res['inverter_rated_ac_kw']} kVA"))
        with col_m2:
            st.metric("Pérdidas por Clipping", format_es_num_str(f"{res['clipping_loss_kw']} kW"), delta=format_es_num_str(f"{res['clipping_loss_pct']}% de recorte") if res['clipping_loss_kw'] > 0 else "0,0% (Sin Recorte)")
            st.metric("THD Corriente AC", format_es_num_str(f"{res['thd_current_pct']}%"), delta="Cumple UNE-EN 50549 < 2,5%")

        if res['clipping_loss_kw'] > 0:
            st.info(f"ℹ️ **Recorte por Clipping Detectado ({res['clipping_loss_kw']} kW):** La potencia DC sobrepasa el límite del inversor AC ({res['inverter_rated_ac_kw']} kVA). Normal en horas punta estivales; optimizado para LCOE mínimo.")
        else:
            st.caption("✔️ No hay saturación de inversor en las condiciones actuales.")

    with col2:
        st.markdown("### 🔌 Capacidad de Nudo de Red (SCR) & Saturación MT")
        st.caption("Verificación de nudo débil conforme a P.O. 12.2 REE y Directiva (UE) 2023/2413:")

        default_scc = max(1.85, round(p_evac_mw * 2.5, 2))
        max_scc = max(15.0, round(p_evac_mw * 6.0, 1))
        s_cc = st.slider("Potencia de Cortocircuito en Nudo MT (MVA)", 0.5, max_scc, default_scc, step=0.05, key=f"v2_slider_scc_{site_config.get('site_id', 'DEF')}")
        grid_eval = MultiMPPTEngine.evaluate_grid_connection_scr(
            short_circuit_capacity_mva=s_cc,
            plant_evacuation_power_mw=p_evac_mw
        )

        scr_val = grid_eval['scr_ratio']
        if grid_eval['is_weak_grid']:
            st.error(f"⚠️ **Alerta Regulatoria REE (P.O. 12.2): Nudo Débil (SCR = {scr_val} < 2,0)**")
            st.warning(f"**Restricción de Red:** {grid_eval['regulatory_compliance']}")
            st.caption(f"**Modo de Inversor Exigido:** `{grid_eval['recommended_inverter_mode']}`")
        else:
            st.success(f"✅ **Nudo Robusto y Estable (SCR = {scr_val} ≥ 2,0)**")
            st.caption(format_es_num_str(f"Evacuación de {p_evac_mw:.2f} MW plenamente admisible sin riesgo de sobretensión ni disparos de frecuencia."))

        st.markdown("---")
        st.markdown("### 🛡️ Degradación por Potencial Inducido (PID) & Curvas I-V")
        pid_eval = MultiMPPTEngine.evaluate_pid_and_thermal_iv(
            cell_technology="n-TOPCon Bifacial",
            cell_temperature_c=55.0
        )
        st.markdown(fr"""
        * **Tecnología de Célula:** `n-TOPCon Tipo N` (Inmunidad Intrínseca al PID)
        * **Pérdida por PID estimada:** `{pid_eval['pid_loss_pct']}%` (Frente a $>2,8\%$ en p-PERC convencional)
        * **Punto de Máxima Potencia Corregido (55 °C):** $V_{{mp}} = {pid_eval['v_mp_corrected_v']}\ \text{{V}}$ | $I_{{mp}} = {pid_eval['i_mp_corrected_a']}\ \text{{A}}$ | $P_{{mp}} = {pid_eval['p_mp_corrected_w']}\ \text{{W}}$
        * **Dictamen IEC 62804:** `{pid_eval['pid_assessment']}`
        """)

    # =========================================================================
    # MÓDULO ENTERPRISE: RESTRICCIONES TÉCNICAS REE & CURTAILMENT (P.O. 3.2)
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🛑 Restricciones Técnicas en Tiempo Real de REE (Curtailment P.O. 3.2)")
    st.caption("Auditoría pericial de vertidos forzosos por saturación de capacidad en la subestación de evacuación (P50 vs P90 bancario):")

    if not site_config.get("is_enterprise", True) or GridCurtailmentEngine is None:
        st.info("🔒 **Módulo Enterprise (Utility-Scale & IPP):** La auditoría avanzada de Curtailment Nodal REE (P.O. 3.2) y penalización bancaria P50/P90 está reservada al régimen **💼 Enterprise**. Conmuta en el panel lateral para activarla.")
    else:
        default_sub_cap = max(2.50, round(p_evac_mw * 2.2, 2))
        default_conn_ren = max(2.20, round(p_evac_mw * 1.9, 2))
        col_cur1, col_cur2, col_cur3 = st.columns(3)
        with col_cur1:
            sub_cap = st.slider("Capacidad Firme Subestación MT/AT (MVA)", 1.0, max(25.0, round(p_evac_mw * 5.0, 1)), default_sub_cap, step=0.25, key=f"v2_slider_sub_cap_{site_config.get('site_id', 'DEF')}")
        with col_cur2:
            conn_renewables = st.slider("Potencia Renovable Conectada en Nudo (MW)", 0.5, max(30.0, round(p_evac_mw * 6.0, 1)), default_conn_ren, step=0.1, key=f"v2_slider_conn_ren_{site_config.get('site_id', 'DEF')}")
        with col_cur3:
            stress_idx = st.selectbox(
                "Tensión Regional de Red (Zona Eléctrica)",
                [1.0, 1.2, 1.4],
                index=1 if "Madrid" in site_config.get("region", "") else 0,
                format_func=lambda x: "Levante / Comunitat Valenciana (1.0x)" if x == 1.0 else ("Castilla-La Mancha / Madrid Zona D3 (1.2x)" if x == 1.2 else "Aragón / Extremadura / Valle Ebro (1.4x)"),
                key="v2_sb_stress_idx"
            )

        curt_res = GridCurtailmentEngine.evaluate_node_curtailment(
            plant_peak_power_mw=p_evac_mw,
            annual_expected_generation_mwh=mwh_year,
            energy_price_eur_mwh=float(site_config.get("ppa_price_eur_mwh", 55.0)),
            substation_capacity_mva=sub_cap,
            node_connected_renewable_mw=conn_renewables,
            region_grid_stress_index=stress_idx
        )

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.markdown(render_kpi_card_html("Saturación de Subestación", f"{curt_res['node_saturation_pct']:.1f}%", f"{conn_renewables:.1f} MW / {sub_cap:.1f} MVA", "Capacidad Nudo", True), unsafe_allow_html=True)
        with col_k2:
            st.markdown(render_kpi_card_html("Vertido Estimado (P50)", f"{curt_res['p50_curtailment_pct']:.1f}%", f"{curt_res['p50_energy_loss_mwh']} MWh/año ({curt_res['p50_revenue_loss_eur']:,.0f} €)", "Escenario Central", True), unsafe_allow_html=True)
        with col_k3:
            st.markdown(render_kpi_card_html("Vertido Estresado (P90)", f"{curt_res['p90_curtailment_pct']:.1f}%", f"{curt_res['p90_energy_loss_mwh']} MWh/año ({curt_res['p90_revenue_loss_eur']:,.0f} €)", "Caso Bancario", True), unsafe_allow_html=True)
        with col_k4:
            st.markdown(render_kpi_card_html("Inyección Neta (P50)", f"{curt_res['p50_net_injected_mwh']:,.0f} MWh", f"Generación Bruta: {mwh_year:,.0f} MWh", curt_res['curtailment_risk_level'], True), unsafe_allow_html=True)

        st.info(f"📋 **Recomendación Técnica REE:** {curt_res['technical_recommendation']}")

    st.markdown("---")
    st.markdown("### 🔬 Matriz de Comparación: n-TOPCon vs. Tándem Perovskita / p-PERC")
    st.markdown(r"""
    | Parámetro Clave | n-TOPCon (HELIOS) | p-PERC Tradicional | Tándem Perovskita |
    |---|---|---|---|
    | **Resistencia a PID (IEC 62804)** | **Inmune (< 0,2%)** | Vulnerable (2,5% - 5%) | Degenerativo (> 8%) |
    | **Coeficiente de Temperatura ($\gamma$)**| **$-0,34\%/^\circ\text{C}$** | $-0,38\%/^\circ\text{C}$ | $-0,28\%/^\circ\text{C}$ (Inestable) |
    | **Degradación Primer Año (LID)** | **$< 1,0\%$** | $2,0\% - 2,5\%$ | $> 5,0\%$ |
    | **Bancabilidad Financiera** | **100% Bancable (Estándar IEC 61215 / 61730)** | Estándar en declive | No bancable |
    """)
