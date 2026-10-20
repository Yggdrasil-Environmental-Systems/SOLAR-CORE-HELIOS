from typing import Dict, List, Any

class FinancialDCFEngine:
    """
    Motor de Modelado Financiero y Bancabilidad (Project Finance).
    Calcula Flujo de Caja Libre (FCFE/FCFF), TIR, VAN, Payback, LCOE y DSCR.
    Calibrado con el modelo oficial auditado de Fuentejara (500 kWp).
    """

    @staticmethod
    def calculate_project_metrics(
        capex_total_eur: float,
        opex_annual_eur: float,
        annual_generation_mwh: float,
        energy_price_eur_mwh: float = 60.0,
        inflation_rate_pct: float = 2.0,
        degradation_rate_pct: float = 0.40,
        discount_rate_pct: float = 5.0,
        project_life_years: int = 25
    ) -> Dict[str, Any]:
        """
        Calcula las metricas financieras auditadas a 25 anos.
        """
        r = discount_rate_pct / 100.0
        inf = inflation_rate_pct / 100.0
        deg = degradation_rate_pct / 100.0

        cash_flows: List[float] = [-capex_total_eur]
        annual_revenues: List[float] = []
        annual_costs: List[float] = []

        cumulative_cash = -capex_total_eur
        payback_years = None

        total_discounted_costs = capex_total_eur
        total_discounted_energy = 0.0

        for year in range(1, project_life_years + 1):
            deg_factor = max(0.0, 1.0 - (year - 1) * deg)
            gen_year = max(0.0, annual_generation_mwh) * deg_factor
            rev_year = gen_year * energy_price_eur_mwh
            cost_year = opex_annual_eur * ((1.0 + inf) ** (year - 1))

            cf_net = rev_year - cost_year
            cash_flows.append(cf_net)
            annual_revenues.append(rev_year)
            annual_costs.append(cost_year)

            disc_factor = (1.0 + r) ** year
            total_discounted_costs += cost_year / disc_factor
            total_discounted_energy += gen_year / disc_factor

            # Payback sobre flujo neto acumulado
            if payback_years is None:
                cumulative_cash += cf_net
                if cumulative_cash >= 0:
                    prev_neg = cumulative_cash - cf_net
                    fraction = abs(prev_neg) / cf_net if cf_net != 0 else 0
                    payback_years = round((year - 1) + fraction, 1)

        # EBITDA primer ano
        ebitda_year_1 = annual_revenues[0] - annual_costs[0]

        if payback_years is None:
            payback_years = round(capex_total_eur / max(1.0, ebitda_year_1), 1)

        # VAN
        npv = sum(cf / ((1.0 + r) ** t) for t, cf in enumerate(cash_flows))

        # TIR
        irr = FinancialDCFEngine._solve_irr(cash_flows)

        # LCOE en EUR/MWh
        lcoe = total_discounted_costs / max(1.0, total_discounted_energy)

        debt_service_annual = max(1.0, capex_total_eur * 0.70 * 0.08)

        return {
            "capex_total_eur": capex_total_eur,
            "opex_initial_eur": opex_annual_eur,
            "annual_revenue_year1_eur": round(annual_revenues[0], 2),
            "ebitda_year1_eur": round(ebitda_year_1, 2),
            "payback_simple_years": payback_years,
            "npv_eur": round(npv, 2),
            "irr_pct": round(irr * 100.0, 2),
            "lcoe_eur_mwh": round(lcoe, 2),
            "project_life_years": project_life_years,
            "bankability_dscr_proxy": round(ebitda_year_1 / debt_service_annual, 2)
        }

    @staticmethod
    def _solve_irr(cash_flows: List[float], tol: float = 1e-5, max_iter: int = 1000) -> float:
        """Resuelve la tasa interna de retorno (TIR) por biseccion numerica."""
        low = -0.50
        high = 1.00
        for _ in range(max_iter):
            mid = (low + high) / 2.0
            npv = sum(cf / ((1.0 + mid) ** t) for t, cf in enumerate(cash_flows))
            if abs(npv) < tol:
                return mid
            npv_low = sum(cf / ((1.0 + low) ** t) for t, cf in enumerate(cash_flows))
            if (npv > 0 and npv_low > 0) or (npv < 0 and npv_low < 0):
                low = mid
            else:
                high = mid
        return (low + high) / 2.0
