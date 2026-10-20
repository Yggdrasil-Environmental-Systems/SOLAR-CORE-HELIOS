class ThermalDegradationModel:
    """
    Modelo de Temperatura de Celula y Degradacion Termica & Temporal.
    Formulacion de Faiman (2008) y norma IEC 61215 / IEC 61724.
    """

    def __init__(
        self,
        temp_coeff_pmp_pct_c: float = -0.34,
        annual_degradation_pct: float = 0.40,
        u0: float = 25.0, # Coeficiente Faiman perdidas radiativas constantes W/(m2*K) [INV-HEL-03]
        u1: float = 6.84  # Coeficiente Faiman conveccion forzada por viento W/(m2*K)/(m/s) [INV-HEL-03]
    ):
        self.gamma_pmp = temp_coeff_pmp_pct_c / 100.0
        self.deg_annual = annual_degradation_pct / 100.0
        self.u0 = u0
        self.u1 = u1

    def calculate_cell_temperature(self, poa_w_m2: float, t_amb_c: float, wind_speed_m_s: float = 1.0) -> float:
        """
        Ecuacion de Faiman para temperatura de operacion de la celula:
        T_cell = T_amb + G_poa / (u0 + u1 * v_wind)
        """
        if poa_w_m2 <= 0:
            return t_amb_c
        heat_dissipation = self.u0 + self.u1 * wind_speed_m_s
        delta_t = poa_w_m2 / max(1.0, heat_dissipation)
        return round(t_amb_c + delta_t, 2)

    def calculate_thermal_derating_factor(self, cell_temp_c: float) -> float:
        """Factor de correccion de potencia por temperatura respecto a STC (25 °C)."""
        factor = 1.0 + self.gamma_pmp * (cell_temp_c - 25.0)
        return round(max(0.0, factor), 4)

    def calculate_aged_power(self, nominal_power_kwp: float, year: int) -> float:
        """
        Potencia nominal remanente tras N anos de operacion.
        Ano 1: degradacion de acodamiento inicial (1.0%).
        Anos subsiguientes: 0.40% anual lineal para n-TOPCon.
        """
        if year <= 1:
            degraded_factor = 1.0 - 0.010
        else:
            degraded_factor = 1.0 - 0.010 - (year - 1) * self.deg_annual
        return round(nominal_power_kwp * max(0.50, degraded_factor), 2)
