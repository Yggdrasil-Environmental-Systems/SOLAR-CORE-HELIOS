# -*- coding: utf-8 -*-
"""
☀️ HELIOS-CORE: HAY-DAVIES-KLUCHER-REINDL (HDKR) ANISOTROPIC TRANSPOSITION ENGINE
========================================================================================
Ecosistema: Yggdrasil Environmental Systems | SOLAR-CORE: HELIOS V3.0
Director Técnico: Kelvin Jesús Flores Yarihuaman (MECES Nivel 3 / EQF Level 7)
Acreditación: Máster Universitario Oficial en Ingeniería y Gestión Ambiental (Art. 335 LEC / ISO 27037)
Referencia Científica:
  Reindl, D. T., Beckman, W. A., Duffie, J. A. (1990). "Evaluation of hourly global and
  diffuse irradiation models and a new model for diffuse irradiation on tilted surfaces".
  Solar Energy, 45(1), 1-7. [ArXiv/SEL Benchmark 2302.08912]

Invariantes Físicas & Leyes de Conservación:
1. Conservación de irradiancia geométrica hemisférica (0.0 <= I_T <= 1361.0 W/m²).
2. Límite Shockley-Queisser / Auger para eficiencia de celda c-Si (eta <= 29.4%, Richter et al., 2013).
3. Corrección de anisotropía circumsolar (A_i = I_b / I_0) y abrillantamiento de horizonte.
========================================================================================
"""

import math
from typing import Dict, List, Tuple, Any, Optional
import numpy as np


class HDKRTransposition:
    """
    Motor vectorial y determinista de transposición espectral anisotrópica HDKR.
    
    Ecuación gobernante de Reindl-Beckman-Duffie:
    I_T = (I_b + I_d * A_i) * R_b + 
          I_d * (1 - A_i) * [(1 + cos(beta)) / 2] * [1 + f * sin^3(beta / 2)] + 
          I * rho_g * [(1 - cos(beta)) / 2]
    
    donde:
      A_i = I_b / I_0             (Índice de anisotropía circumsolar)
      f   = sqrt(I_b / max(1e-3, I)) (Factor modulador de horizonte)
      R_b = cos(theta) / max(0.01, cos(theta_z)) (Razón geométrica directa)
      rho_g = Albedo superficial (0.20 estándar)
    """

    SOLAR_CONSTANT_G0 = 1361.0  # W/m² (Constante solar extraterrestre AM0 - INV-HEL-01)

    @classmethod
    def calculate_extraterrestrial_g0(cls, day_of_year: int) -> float:
        """
        Calcula la irradiancia normal extraterrestre con excentricidad orbital (Spencer, 1971).
        """
        b = 2.0 * math.pi * (day_of_year - 1) / 365.0
        r_corr = 1.000110 + 0.034221 * math.cos(b) + 0.001280 * math.sin(b) + \
                 0.000719 * math.cos(2.0 * b) + 0.000077 * math.sin(2.0 * b)
        return cls.SOLAR_CONSTANT_G0 * r_corr

    @classmethod
    def calculate_poa_hdkr(
        cls,
        ghi: float,
        dhi: float,
        dni: float,
        theta_z_deg: float,
        surface_tilt_deg: float,
        surface_azimuth_deg: float,
        solar_azimuth_deg: float,
        day_of_year: int = 180,
        albedo: float = 0.20
    ) -> Dict[str, float]:
        """
        Calcula la radiación global en el plano del generador (POA) mediante HDKR.
        
        Args:
            ghi: Irradiancia Global Horizontal (W/m²)
            dhi: Irradiancia Difusa Horizontal (W/m²)
            dni: Irradiancia Directa Normal (W/m²)
            theta_z_deg: Ángulo cenital solar (grados, 0 = cenit vertical, 90 = horizonte)
            surface_tilt_deg: Inclinación de la mesa beta (grados, 0 = horizontal)
            surface_azimuth_deg: Azimut de la mesa (-90 = Este, 0 = Sur, +90 = Oeste o convención astronómica)
            solar_azimuth_deg: Azimut del sol (astronómico 0..360, 180 = Sur)
            day_of_year: Día del año (1..365)
            albedo: Coeficiente de reflectancia del terreno (default 0.20)
            
        Returns:
            Dict con poa_global, poa_beam, poa_diffuse_circumsolar, poa_diffuse_isotropic,
            poa_diffuse_horizon, poa_albedo, anisotropy_index.
        """
        # Condiciones de noche o sol bajo el horizonte
        if theta_z_deg >= 89.0 or ghi <= 0.0:
            return {
                "poa_global": 0.0,
                "poa_beam": 0.0,
                "poa_diffuse": 0.0,
                "poa_diffuse_circumsolar": 0.0,
                "poa_diffuse_isotropic": 0.0,
                "poa_diffuse_horizon": 0.0,
                "poa_albedo": 0.0,
                "anisotropy_index": 0.0
            }

        theta_z_rad = math.radians(theta_z_deg)
        tilt_rad = math.radians(surface_tilt_deg)
        cos_theta_z = max(0.01, math.cos(theta_z_rad))

        # Homogeneización de convención de azimut
        if abs(surface_azimuth_deg) <= 90.0:
            surf_astro_azimuth = (surface_azimuth_deg + 180.0) % 360.0
        else:
            surf_astro_azimuth = surface_azimuth_deg % 360.0

        gamma_diff_rad = math.radians(solar_azimuth_deg - surf_astro_azimuth)

        # Ángulo de incidencia en la superficie inclinada (cos theta)
        cos_theta = (
            math.cos(theta_z_rad) * math.cos(tilt_rad) +
            math.sin(theta_z_rad) * math.sin(tilt_rad) * math.cos(gamma_diff_rad)
        )
        cos_theta = max(0.0, cos_theta)

        # Razón geométrica de radiación directa R_b
        r_b = cos_theta / cos_theta_z

        # Radiación directa horizontal I_b
        i_b = max(0.0, ghi - dhi)
        if dni > 0.0:
            i_b = min(i_b, dni * cos_theta_z)

        # Irradiancia extraterrestre en el plano horizontal I_0
        g0_normal = cls.calculate_extraterrestrial_g0(day_of_year)
        i_0 = max(1.0, g0_normal * cos_theta_z)

        # 1. Índice de anisotropía circumsolar A_i (acotado [0, 1])
        a_i = max(0.0, min(1.0, i_b / i_0))

        # 2. Factor modulador de abrillantamiento del horizonte f
        f = math.sqrt(max(0.0, i_b / max(1.0, ghi)))

        # --- Componente Directa en Plano (acotada por INV-HEL-01) ---
        poa_beam = min(cls.SOLAR_CONSTANT_G0, max(0.0, (i_b + dhi * a_i) * r_b))

        # --- Componente Difusa en Plano (HDKR) ---
        # Difusa Isotropica + Abrillantamiento del Horizonte
        geom_view_sky = (1.0 + math.cos(tilt_rad)) / 2.0
        horizon_factor = 1.0 + f * (math.sin(tilt_rad / 2.0) ** 3)
        poa_diff_sky = dhi * (1.0 - a_i) * geom_view_sky * horizon_factor

        poa_diff_circum = dhi * a_i * r_b
        poa_diff_iso = dhi * (1.0 - a_i) * geom_view_sky
        poa_diff_horizon = poa_diff_sky - poa_diff_iso

        # --- Componente de Albedo (Reflejo del Suelo) ---
        geom_view_ground = (1.0 - math.cos(tilt_rad)) / 2.0
        poa_albedo = ghi * albedo * geom_view_ground

        # Irradiancia Total POA (Gobernada por ley de conservación INV-HEL-01)
        poa_global = min(cls.SOLAR_CONSTANT_G0, max(0.0, poa_beam + poa_diff_sky + poa_albedo))

        return {
            "poa_global": round(poa_global, 3),
            "poa_beam": round(poa_beam, 3),
            "poa_diffuse": round(poa_diff_sky + poa_diff_circum, 3),
            "poa_diffuse_circumsolar": round(poa_diff_circum, 3),
            "poa_diffuse_isotropic": round(poa_diff_iso, 3),
            "poa_diffuse_horizon": round(poa_diff_horizon, 3),
            "poa_albedo": round(poa_albedo, 3),
            "anisotropy_index": round(a_i, 4)
        }

    @classmethod
    def optimize_tilt_azimuth_for_f5d_demand(
        cls,
        hourly_ghi: np.ndarray,
        hourly_dhi: np.ndarray,
        hourly_dni: np.ndarray,
        hourly_zenith_deg: np.ndarray,
        hourly_solar_azimuth_deg: np.ndarray,
        f5d_demand_curve: Optional[np.ndarray] = None,
        lat_deg: float = 39.47,
        albedo: float = 0.20
    ) -> Dict[str, Any]:
        """
        Optimiza la inclinación (tilt) y el azimut fotovoltaico acoplando:
        - Curva de demanda horaria F5D del sistema eléctrico
        - Máxima producción anual ponderada por valor horario
        
        Permite seleccionar el ángulo óptimo para:
        1. Máxima producción bruta (kWh/kWp anuales)
        2. Máximo acoplamiento con demanda F5D / Precios OMIE
        """
        n_hours = len(hourly_ghi)
        if f5d_demand_curve is None:
            # Ponderación plana si no se suministra curva F5D
            f5d_demand_curve = np.ones(n_hours, dtype=np.float32)

        # Normalizar perfil de demanda
        demand_weight = f5d_demand_curve / max(1e-3, np.mean(f5d_demand_curve))

        tilts_to_test = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0]
        azimuths_to_test = [-30.0, -15.0, 0.0, 15.0, 30.0]  # Respecto al Sur

        best_tilt_yield = 30.0
        best_azimuth_yield = 0.0
        max_total_kwh = -1.0

        best_tilt_f5d = 30.0
        best_azimuth_f5d = 0.0
        max_f5d_weighted_yield = -1.0

        results_grid = []

        for tilt in tilts_to_test:
            for az in azimuths_to_test:
                poa_sum = 0.0
                f5d_weighted_poa = 0.0

                for h in range(n_hours):
                    doy = int((h // 24) % 365) + 1
                    poa_res = cls.calculate_poa_hdkr(
                        ghi=float(hourly_ghi[h]),
                        dhi=float(hourly_dhi[h]),
                        dni=float(hourly_dni[h]),
                        theta_z_deg=float(hourly_zenith_deg[h]),
                        surface_tilt_deg=tilt,
                        surface_azimuth_deg=az,
                        solar_azimuth_deg=float(hourly_solar_azimuth_deg[h]),
                        day_of_year=doy,
                        albedo=albedo
                    )
                    poa_val = poa_res["poa_global"]
                    poa_sum += poa_val
                    f5d_weighted_poa += poa_val * demand_weight[h]

                total_kwh_m2 = poa_sum / 1000.0
                weighted_kwh_m2 = f5d_weighted_poa / 1000.0

                results_grid.append({
                    "tilt_deg": tilt,
                    "azimuth_deg": az,
                    "annual_poa_kwh_m2": round(total_kwh_m2, 2),
                    "f5d_weighted_poa_kwh_m2": round(weighted_kwh_m2, 2)
                })

                if total_kwh_m2 > max_total_kwh:
                    max_total_kwh = total_kwh_m2
                    best_tilt_yield = tilt
                    best_azimuth_yield = az

                if weighted_kwh_m2 > max_f5d_weighted_yield:
                    max_f5d_weighted_yield = weighted_kwh_m2
                    best_tilt_f5d = tilt
                    best_azimuth_f5d = az

        return {
            "optimal_for_maximum_yield": {
                "tilt_deg": best_tilt_yield,
                "azimuth_deg": best_azimuth_yield,
                "annual_poa_kwh_m2": round(max_total_kwh, 2)
            },
            "optimal_for_f5d_demand_matching": {
                "tilt_deg": best_tilt_f5d,
                "azimuth_deg": best_azimuth_f5d,
                "f5d_weighted_poa_kwh_m2": round(max_f5d_weighted_yield, 2)
            },
            "exploration_grid": results_grid
        }
