import streamlit as st
import pandas as pd
try:
    from components.ui_components import render_kpi_card_html
except (ImportError, ModuleNotFoundError):
    from app.components.ui_components import render_kpi_card_html
from core.eia_buffer_checker import EIABufferChecker
try:
    from core.rdl23_permitting_milestones import RDL23PermittingMilestones
    from core.grid_easement_and_nodal_capacity import HighVoltageEasementAndNodalEngine
except (ImportError, ModuleNotFoundError):
    RDL23PermittingMilestones = None
    HighVoltageEasementAndNodalEngine = None

def render_view(site_config: dict):
    st.markdown("## 🌿 3. Evaluación de Impacto Ambiental (EIA), RED III & Zonificación Territorial")
    st.markdown(
        "*Verificación preventiva de condicionantes según Directiva (UE) 2023/2413 (RED III), Ley 21/2013, Dominio Público Hidráulico (DPH), "
        "Red Natura 2000, Servidumbres AESA (RD 384/2023) y Matriz de Riesgo de Avales (RDL 23/2020).*"
    )

    kwp = float(site_config.get("peak_power_kwp", 500.0))

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        d_natura = st.number_input("Distancia a Red Natura 2000 (km)", 0.0, 20.0, 2.8, step=0.1, key="v3_num_natura")
    with col_in2:
        d_cauce = st.number_input("Distancia a Cauce / Rambla DPH (m)", 0.0, 500.0, 115.0, step=5.0, key="v3_num_cauce")
    with col_in3:
        d_via = st.number_input("Distancia a Vía Pecuaria (m)", 0.0, 200.0, 25.0, step=1.0, key="v3_num_via")

    col_in4, col_in5, col_in6 = st.columns(3)
    with col_in4:
        slope = st.slider("Pendiente Media del Terreno (%)", 0.0, 15.0, 3.2, step=0.1, key="v3_slider_slope")
    with col_in5:
        fence_gap = st.slider("Luz Inferior del Cerramiento Cinegético (cm)", 5.0, 30.0, 18.0, step=1.0, key="v3_slider_fence_gap")
    with col_in6:
        d_corredor = st.slider("Distancia a Corredor Ecológico (km)", 0.0, 10.0, 3.5, step=0.1, key="v3_slider_corredor")

    # Auditoria integral con RED III
    audit = EIABufferChecker.audit_territorial_constraints(
        distance_natura_2000_km=d_natura,
        distance_cauce_dph_m=d_cauce,
        distance_via_pecuaria_m=d_via,
        average_slope_pct=slope,
        fence_mesh_bottom_clearance_cm=fence_gap,
        distance_corredores_ecologicos_km=d_corredor
    )

    # BANNER 0: Pre-filtro Vinculante SIG (Directiva RED III & Ley 21/2013)
    pre = audit["pre_screening_sig"]
    pre_status_clean = str(pre['status']).replace("_", " ")
    if pre["is_site_compatible"]:
        st.success(f"🗺️ **CAPA SIG VINCULANTE (PRE-PEREZ):** {pre_status_clean} — {pre['justificacion']}")
    else:
        st.error(f"🚫 **CAPA SIG VINCULANTE (PRE-PEREZ):** {pre_status_clean} — {pre['justificacion']}")

    st.markdown("### 📋 Resultados del Chequeo Normativo")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(render_kpi_card_html(
            "Red Natura 2000",
            f"{d_natura:.1f} km",
            audit['red_natura_2000']['motivo'],
            audit['red_natura_2000']['status'],
            audit['red_natura_2000']['status'] == "APTO"
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card_html(
            "Dominio Público Hidráulico",
            f"{d_cauce:.0f} m al cauce",
            f"Servidumbre 5m: {audit['dph_cauces']['zona_servidumbre_5m']}",
            audit['dph_cauces']['status'],
            audit['dph_cauces']['status'] == "CONFORME"
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card_html(
            "Vías Pecuarias",
            f"{d_via:.0f} m de buffer",
            audit['vias_pecuarias']['motivo'],
            audit['vias_pecuarias']['status'],
            audit['vias_pecuarias']['status'] == "INDEMNE"
        ), unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(render_kpi_card_html(
            "Pendiente Topográfica",
            f"{slope:.1f}%",
            audit['pendiente_suelo']['motivo'],
            audit['pendiente_suelo']['status'],
            audit['pendiente_suelo']['status'] == "OPTIMO"
        ), unsafe_allow_html=True)
    with col5:
        st.markdown(render_kpi_card_html(
            "Cerramiento de Fauna",
            f"{fence_gap:.0f} cm de vano inferior",
            audit['cerramiento_fauna']['motivo'],
            audit['cerramiento_fauna']['status'],
            audit['cerramiento_fauna']['status'] == "PERMEABLE"
        ), unsafe_allow_html=True)
    with col6:
        red_iii = audit["directiva_red_iii"]
        st.markdown(render_kpi_card_html(
            "Directiva (UE) RED III",
            f"Plazo: {red_iii['plazo_maximo_meses']} Meses",
            red_iii['motivo'],
            red_iii['status'],
            red_iii['tramitacion_abreviada']
        ), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ✈️ Servidumbres Aeronáuticas AESA & Deslumbramiento Glint/Glare (RD 384/2023)")
    st.caption("Verificación de radioayudas CNS (VOR/DME/ILS), superficies limitadoras (SLO) y reflexión solar hacia conos de aproximación:")

    col_ae1, col_ae2 = st.columns(2)
    with col_ae1:
        d_aero = st.slider("Distancia al Aeródromo / Pista (km)", 2.0, 30.0, 14.5, step=0.5, key="v3_slider_daero")
        d_vor = st.slider("Distancia a Radioayuda VOR/DME (m)", 500, 10000, 6200, step=100, key="v3_slider_dvor")
        has_arc = st.checkbox("Módulos con Vidrio Antirreflectante (Capa ARC)", value=True, key="v3_chk_arc")

    with col_ae2:
        from core.aeronautical_servitudes_glare import AeronauticalServitudesGlare
        aesa_audit = AeronauticalServitudesGlare.audit_aeronautical_servitudes(
            distance_aerodrome_km=d_aero,
            distance_vor_dme_m=float(d_vor),
            distance_radar_m=8100.0,
            max_structure_height_agl_m=3.2,
            distance_to_runway_m=d_aero * 1000.0,
            tilt_deg=float(site_config.get("tilt_deg", 30.0)),
            azimuth_deg=0.0
        )
        glare = aesa_audit["glint_and_glare"]
        glare_verdict_es = {
            "NO_GLARE_SAFE": "SIN AFECCIÓN OCULAR (ZONA VERDE)",
            "GREEN_GLARE_LOW_POTENTIAL": "DESTELLO LEVE ADMISIBLE (ZONA VERDE)",
            "YELLOW_GLARE_POTENTIAL_AFTERIMAGE": "RIESGO DE POST-IMAGEN (ZONA AMARILLA)",
            "RED_GLARE_RETINAL_BURN_RISK": "AFECCION RETINIANA CRITICA (ZONA ROJA)"
        }.get(glare["hazard_verdict"], str(glare["hazard_verdict"]).replace("_", " "))
        st.markdown(render_kpi_card_html(
            "Autorización AESA (RD 384/2023)",
            aesa_audit["global_aesa_authorization"],
            f"Radioayudas: {aesa_audit['radioayudas_cns']['cns_status']} (VOR: {d_vor} m)",
            aesa_audit["global_aesa_authorization"],
            aesa_audit["is_authorized_by_aesa"]
        ), unsafe_allow_html=True)
        st.markdown(render_kpi_card_html(
            "Deslumbramiento (Glint & Glare)",
            glare_verdict_es,
            f"Reflectividad Fresnel: {glare['fresnel_reflectivity_pct']}% | {glare['retinal_hazard_description']}",
            glare["glare_hazard_category"],
            glare["aesa_safe_flight_compliant"]
        ), unsafe_allow_html=True)

    # =========================================================================
    # SERVIDUMBRES DE ALTA TENSIÓN (RD 1955/2000) & CAPACIDAD NODAL (P.O. 12.2 REE)
    # =========================================================================
    st.markdown("---")
    st.markdown("### ⚡ Servidumbres de Líneas de Alta Tensión (400 kV / 220 kV) & Capacidad Nodal (P.O. 12.2 REE)")
    st.caption("Verificación de franjas de servidumbre aérea (RD 1955/2000 Arts. 158-162), radio de afección a apoyos (ITC-LAT 07), zonas CEM y sobretensión nodal $\\Delta V$:")

    if not site_config.get("is_enterprise", True) or HighVoltageEasementAndNodalEngine is None or RDL23PermittingMilestones is None:
        st.info("🔒 **Módulos Enterprise (Servidumbres AT RD 223/2008 & Avales RDL 23/2020):** La auditoría de electroductos de alta tensión, sobretensión nodal P.O. 12.2 y la matriz de caducidad de avales bancarios (40 000 €/MW) pertenecen a la **💼 Edición Enterprise**. Conmuta en el panel lateral para activarlos.")
        at_compliant = True
    else:
        col_at1, col_at2, col_at3 = st.columns(3)
        with col_at1:
            v_line = st.selectbox("Tensión de Línea Próxima (kV)", [400, 220, 132, 66], index=0, key="v3_sb_line_kv")
            d_axis = st.slider("Distancia al Eje de la Línea (m)", 5.0, 100.0, 35.0, step=1.0, key="v3_slider_dist_axis")
        with col_at2:
            d_tower = st.slider("Distancia a Cimentación de Apoyo / Torre (m)", 2.0, 100.0, 25.0, step=1.0, key="v3_slider_dist_tower")
            d_inv_cem = st.slider("Distancia de Inversores / CT a Línea (m)", 5.0, 100.0, 40.0, step=1.0, key="v3_slider_dist_inv")
        with col_at3:
            s_cc_mva = st.number_input("Potencia Cortocircuito del Nudo (MVA)", 500.0, 25000.0, 4500.0, step=250.0, key="v3_num_scc")
            v_init_pu = st.slider("Tensión Previa en Nudo de Red (p.u.)", 0.95, 1.08, 1.02, step=0.005, key="v3_slider_v_init")

        at_audit = HighVoltageEasementAndNodalEngine.audit_line_easement(
            line_voltage_kv=float(v_line),
            distance_to_axis_m=float(d_axis),
            distance_to_nearest_tower_m=float(d_tower),
            distance_inverters_to_line_m=float(d_inv_cem),
            pv_modules_under_line=False
        )
        at_compliant = at_audit["is_compliant"]

        evac_mw = kwp / 1000.0
        nodal_res = HighVoltageEasementAndNodalEngine.calculate_nodal_overvoltage_and_reactive_support(
            evacuation_voltage_kv=float(v_line),
            pv_evacuated_power_mw=evac_mw,
            grid_short_circuit_mva=float(s_cc_mva),
            initial_grid_voltage_pu=float(v_init_pu),
            power_factor=1.0
        )

        col_kpi_at1, col_kpi_at2, col_kpi_at3, col_kpi_at4 = st.columns(4)
        with col_kpi_at1:
            st.markdown(render_kpi_card_html(
                f"Servidumbre {v_line} kV",
                f"Eje: {d_axis:.1f} m",
                f"Semianchura Legal: {at_audit['corridor_half_width_m']:.0f} m (Franja {at_audit['corridor_total_width_m']:.0f} m)",
                at_audit["status"],
                at_audit["is_compliant"]
            ), unsafe_allow_html=True)
        with col_kpi_at2:
            tower_ok = d_tower >= at_audit["tower_clearance_radius_m"]
            st.markdown(render_kpi_card_html(
                "Cimentación de Apoyo",
                f"{d_tower:.1f} m al apoyo",
                f"Mínimo Exigido ITC-LAT 07: {at_audit['tower_clearance_radius_m']:.0f} m",
                "INDEMNE" if tower_ok else "AFECCION_APOYO",
                tower_ok
            ), unsafe_allow_html=True)
        with col_kpi_at3:
            cem_ok = d_inv_cem >= at_audit["inverter_cem_buffer_m"]
            st.markdown(render_kpi_card_html(
                "Inmunidad CEM Inversores",
                f"{d_inv_cem:.1f} m al CT",
                f"Buffer Recomendado: {at_audit['inverter_cem_buffer_m']:.0f} m",
                "INMUNE" if cem_ok else "ADVERTENCIA_CEM",
                cem_ok
            ), unsafe_allow_html=True)
        with col_kpi_at4:
            v_final = nodal_res["projected_voltage_pu"]
            v_safe = not nodal_res["overvoltage_trip_risk"]
            st.markdown(render_kpi_card_html(
                "Tensión Proyectada Nodal",
                f"{v_final:.3f} p.u. ({nodal_res['projected_voltage_kv']:.1f} kV)",
                f"Delta V: +{nodal_res['delta_v_pct']:.2f}% | Límite PO 12.2: 1,10 p.u.",
                nodal_res["status"],
                v_safe
            ), unsafe_allow_html=True)

        if nodal_res["reactive_support_needed_mvar"] > 0:
            st.warning(
                f"⚡ **CONTROL DE TENSIÓN ACTIVO (P.O. 12.2):** Para mitigar sobretensión nodal (> 1,05 p.u.), los inversores "
                f"deben absorber **{nodal_res['reactive_support_needed_mvar']:.2f} MVAr** de reactiva inductiva, "
                f"operando a un factor de potencia objetivo de **cos φ = {nodal_res['recommended_inverter_cos_phi']}**."
            )
        else:
            st.success(f"✅ **CAPACIDAD NODAL CONFORME:** Inyección de {evac_mw:.2f} MW en nudo {v_line} kV (Scc = {s_cc_mva:.0f} MVA) no genera disparos por sobretensión permanente. Cumple P.O. 12.2.")

        # =========================================================================
        # MÓDULO ENTERPRISE: GESTOR DE HITOS RDL 23/2020 Y RIESGO DE AVALES
        # =========================================================================
        st.markdown("---")
        st.markdown("### ⏱️ Calendario de Hitos RDL 23/2020 & Matriz de Riesgo de Avales (40 000 €/MW)")
        st.caption("Control pericial de plazos administrativos perentorios y protección del aval depositado según RD 1183/2020:")

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            elapsed = st.slider("Meses Transcurridos desde Concesión de Acceso", 1.0, 72.0, 18.0, step=1.0, key="v3_slider_elapsed_m")
        with col_h2:
            milestone_choices = {
                "H1_SOLICITUD_AAP": "H1: Solicitud de AAP Realizada",
                "H2_OBTENCION_DIA": "H2: DIA Favorable Obtenida",
                "H3_OBTENCION_AAP": "H3: AAP Concedida",
                "H4_OBTENCION_AAC": "H4: AAC Concedida",
                "H5_AUTORIZACION_COD": "H5: Puesta en Servicio (COD)"
            }
            completed_m = st.selectbox(
                "Último Hito Culminado con Éxito:",
                list(milestone_choices.keys()),
                format_func=lambda k: milestone_choices[k],
                index=0,
                key="v3_sb_milestone_completed"
            )
        with col_h3:
            rdl8_ext = st.checkbox("Acogido a Prórroga Extraordinaria (RDL 8/2023)", value=True, key="v3_chk_rdl8")

        hitos_res = RDL23PermittingMilestones.calculate_bank_guarantee_and_milestones(
            peak_power_kw=kwp,
            elapsed_months=elapsed,
            completed_milestone_id=completed_m,
            has_extended_deadline_rdl8_2023=rdl8_ext
        )

        col_av1, col_av2, col_av3, col_av4 = st.columns(4)
        with col_av1:
            st.markdown(render_kpi_card_html("Aval Bancario Depositado", f"{hitos_res['bank_guarantee_total_eur']:,.0f} €", f"{RDL23PermittingMilestones.AVAL_RATE_EUR_PER_KW:.0f} €/kW ({hitos_res['installed_capacity_mw']} MW)", "Garantía RD 1183", True), unsafe_allow_html=True)
        with col_av2:
            st.markdown(render_kpi_card_html("Meses en Tramitación", f"{hitos_res['elapsed_months']:.0f} Meses", f"Prórroga RDL 8/2023: {'SÍ' if rdl8_ext else 'NO'}", "Cronograma", True), unsafe_allow_html=True)
        with col_av3:
            is_safe = hitos_res['global_risk_level'] == "VERDE_PLAZO_SEGURO"
            st.markdown(render_kpi_card_html("Semáforo de Caducidad", hitos_res['global_risk_level'], f"Hito Crítico: {hitos_res['critical_milestone'] or 'Ninguno'}", hitos_res['global_risk_level'], is_safe), unsafe_allow_html=True)
        with col_av4:
            st.markdown(render_kpi_card_html("Riesgo de Ejecución Aval", "0.0 €" if is_safe else f"{hitos_res['bank_guarantee_total_eur']:,.0f} €", "Blindaje Jurídico Art. 28", "Seguridad Jurídica", is_safe), unsafe_allow_html=True)

        st.markdown("#### 📜 Tabla de Hitos Administrativos Obligatorios (RDL 23/2020)")
        df_hitos = pd.DataFrame([
            {
                "Hito Administrativo": m["name"],
                "Límite Legal (Mes)": f"Mes {m['legal_month_limit']}",
                "Margen Restante": f"{m['months_remaining']} Meses ({m['days_remaining']} Días)",
                "Estado de Tramitación": str(m["status"]).replace("_", " "),
                "Semáforo": str(m["risk_color"]).replace("_", " ")
            }
            for m in hitos_res["milestones"]
        ])
        st.table(df_hitos.set_index("Hito Administrativo"))

        st.info(f"⚖️ **Protocolo de Defensa Jurídica del Aval:** {hitos_res['legal_defense_protocol']}")

    st.markdown("---")
    clasificacion_clean = str(audit['directiva_red_iii']['clasificacion']).replace("_", " ")
    if audit['dictamen_global']['cero_alegaciones_proyectadas'] and aesa_audit['is_authorized_by_aesa'] and at_compliant:
        st.success(f"🌟 **DICTAMEN TERRITORIAL, AERONÁUTICO & ELÉCTRICO GLOBAL:** La parcela cumple íntegramente los condicionantes de la **Ley 21/2013**, **RD 384/2023 (AESA)**, **RD 1955/2000 (Servidumbres AT)** y clasifica como **{clasificacion_clean}** bajo la **Directiva (UE) 2023/2413 (RED III)**. Proyección: **CERO ALEGACIONES AMBIENTALES & TRAMITACIÓN ABREVIADA PRIORITARIA**.")
    else:
        st.warning("⚠️ **ATENCIÓN:** Existen condicionantes territoriales, aeronáuticos o de servidumbre eléctrica que requieren medidas correctoras antes de presentar el Documento Ambiental Inicial ante el órgano sustantivo.")
