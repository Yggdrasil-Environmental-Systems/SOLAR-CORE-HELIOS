from typing import List, Dict, Any

class MultiMPPTEngine:
    """
    Motor de Simulacion de Topologia Multi-MPPT en Inversores de String Industriales SOFAR,
    Perdidas por Clipping, Saturacion de Nudo de Red MT (SCR) y Blindaje PID.
    Normas de referencia:
    - Directiva (UE) 2023/2413 (RED III)
    - Real Decreto 244/2019 de Autoconsumo & Procedimientos de Operacion REE (P.O. 12.2 / 12.3)
    - IEC 62804 (Test de Degradacion por Potencial Inducido - PID)
    """

    def __init__(
        self,
        num_mppt_trackers: int = 4,
        inverter_euro_efficiency: float = 0.984,
        dc_ac_ratio: float = 1.11,  # 500 kWp DC / 450 kVA AC en Fuentejara
        thd_current_pct: float = 2.2
    ):
        self.num_mppt = num_mppt_trackers
        self.inverter_eff = inverter_euro_efficiency
        self.dc_ac_ratio = dc_ac_ratio
        self.thd = thd_current_pct

    def process_string_power(
        self,
        dc_power_total_kw: float,
        shading_distribution_pct: List[float] = None
    ) -> Dict[str, float]:
        """
        Calcula la potencia AC inyectada considerando desajuste (mismatch) entre canales MPPT
        y recorte de pico (clipping loss).
        """
        if shading_distribution_pct is None:
            shading_distribution_pct = [1.0] * self.num_mppt

        power_per_mppt_ideal = dc_power_total_kw / self.num_mppt
        mppt_harvested_dc = []

        for factor in shading_distribution_pct:
            mppt_harvested_dc.append(power_per_mppt_ideal * factor)

        total_dc_harvested = sum(mppt_harvested_dc)

        # Inversor max AC clipping (450 kVA nominal en Fuentejara)
        inverter_rated_ac_kw = dc_power_total_kw / self.dc_ac_ratio
        raw_ac_power = total_dc_harvested * self.inverter_eff

        clipped_ac_power = min(inverter_rated_ac_kw, raw_ac_power)
        clipping_loss_kw = max(0.0, raw_ac_power - inverter_rated_ac_kw)
        clipping_pct = (clipping_loss_kw / max(1.0, raw_ac_power)) * 100.0

        # Mismatch mitigado respecto a inversor central
        min_factor = min(shading_distribution_pct)
        central_inverter_dc = dc_power_total_kw * min_factor
        mismatch_saved_kw = max(0.0, total_dc_harvested - central_inverter_dc)

        return {
            "dc_power_input_kw": round(dc_power_total_kw, 2),
            "dc_power_harvested_kw": round(total_dc_harvested, 2),
            "ac_power_output_kw": round(clipped_ac_power, 2),
            "inverter_rated_ac_kw": round(inverter_rated_ac_kw, 2),
            "clipping_loss_kw": round(clipping_loss_kw, 2),
            "clipping_loss_pct": round(clipping_pct, 2),
            "mismatch_mitigated_kw": round(mismatch_saved_kw, 2),
            "inverter_efficiency": self.inverter_eff,
            "thd_current_pct": self.thd
        }

    @staticmethod
    def evaluate_grid_connection_scr(
        short_circuit_capacity_mva: float = 1.75,
        plant_evacuation_power_mw: float = 0.50,
        grid_voltage_kv: float = 20.0
    ) -> Dict[str, Any]:
        """
        Calcula el Short-Circuit Ratio (SCR) en el nudo de Media Tension.
        SCR = S_cc (MVA) / P_nom (MW).
        - SCR < 2.0: Restriccion de saturacion de nudo debil de red (Directiva RED III).
        - SCR >= 2.0: Nudo estable para evacuacion garantizada.
        """
        scr = short_circuit_capacity_mva / max(0.01, plant_evacuation_power_mw)
        is_weak_grid = scr < 2.0

        return {
            "short_circuit_capacity_mva": short_circuit_capacity_mva,
            "evacuation_power_mw": plant_evacuation_power_mw,
            "grid_voltage_kv": grid_voltage_kv,
            "scr_ratio": round(scr, 2),
            "is_weak_grid": is_weak_grid,
            "grid_status": "NUDO_DEBIL_RESTRICCION_SATURACION" if is_weak_grid else "NUDO_ESTABLE_CONEXION_ROBUSTA",
            "regulatory_compliance": (
                "Alerta RED III: Nudo MT debil (SCR < 2.0). Requiere control dinamico de factor de potencia P-Q y compensacion reactiva."
                if is_weak_grid else
                "Conforme: Capacidad de cortocircuito suficiente (SCR >= 2.0) para inyeccion plena en barra MT."
            ),
            "recommended_inverter_mode": "Control de Tension Volt-VAr Dinamico (Q(U))" if is_weak_grid else "Cos(phi) = 1.0 Estandar"
        }

    @staticmethod
    def evaluate_pid_and_thermal_iv(
        cell_technology: str = "n-TOPCon",
        system_voltage_v: float = 1500.0,
        cell_temperature_c: float = 55.0,
        v_mp_stc: float = 42.5,
        i_mp_stc: float = 12.94
    ) -> Dict[str, Any]:
        """
        Calcula la degradacion por Potencial Inducido (PID) segun IEC 62804 y
        la correccion de curvas I-V por temperatura extrema de celda.
        """
        is_n_type = "TOPCon" in cell_technology or "HJT" in cell_technology or "tipo N" in cell_technology.lower()

        # Coeficientes termicos para TOPCon (gamma_Pmp = -0.34%/C, beta_Voc = -0.28%/C, alpha_Isc = +0.045%/C)
        delta_t = cell_temperature_c - 25.0
        beta_v = -0.0028
        alpha_i = +0.00045

        v_mp_corrected = v_mp_stc * (1.0 + beta_v * delta_t)
        i_mp_corrected = i_mp_stc * (1.0 + alpha_i * delta_t)
        p_mp_corrected = v_mp_corrected * i_mp_corrected

        # Perdida PID segun tecnologia
        if is_n_type:
            pid_loss_pct = 0.15  # Inmunidad intrinseca n-type
            pid_status = "BLINDADO_INMUNIDAD_N_TYPE"
            pid_notes = "Silicio tipo N dopado con Fosforo sin polarizacion perjudicial. Blindado segun IEC 62804."
        else:
            pid_loss_pct = 2.80  # p-PERC tipico
            pid_status = "RIESGO_PID_ELEVADO"
            pid_notes = "Silicio p-PERC vulnerable a fugas de electrones a 1500V. Exige cajas anti-PID nocturnas."

        return {
            "cell_technology": cell_technology,
            "system_voltage_v": system_voltage_v,
            "cell_temperature_c": round(cell_temperature_c, 1),
            "v_mp_corrected_v": round(v_mp_corrected, 2),
            "i_mp_corrected_a": round(i_mp_corrected, 2),
            "p_mp_corrected_w": round(p_mp_corrected, 2),
            "pid_loss_pct": round(pid_loss_pct, 2),
            "pid_status": pid_status,
            "pid_assessment": pid_notes
        }
