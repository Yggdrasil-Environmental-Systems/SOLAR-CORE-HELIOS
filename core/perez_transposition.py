import math
from typing import Dict, Tuple

class PerezTransposition:
    """
    Modelo Anisotropico de Transposicion Radiativa de Perez et al. (1990).
    Descompone la radiacion solar incidente en el plano del generador (POA).
    """

    # Coeficientes f1, f2 de Perez segun rangos de claridad atmosferica epsilon
    PEREZ_COEFFS = [
        # (eps_low, eps_high, f11, f12, f13, f21, f22, f23)
        (1.000, 1.065, -0.008, 0.588, -0.062, -0.060, 0.072, -0.022),
        (1.065, 1.230,  0.130, 0.683, -0.151, -0.019, 0.066, -0.029),
        (1.230, 1.500,  0.330, 0.487, -0.221,  0.055, -0.064, -0.026),
        (1.500, 1.950,  0.568, 0.187, -0.295,  0.109, -0.152, -0.014),
        (1.950, 2.800,  0.873, -0.392, -0.362,  0.226, -0.252,  0.001),
        (2.800, 4.500,  1.132, -1.237, -0.412,  0.288, -0.280,  0.060),
        (4.500, 6.200,  1.060, -1.600, -0.359,  0.264, -0.212,  0.156),
        (6.200, 999.0,  0.678, -0.327, -0.250,  0.156, -0.020,  0.264),
    ]

    @classmethod
    def calculate_poa_irradiance(
        cls,
        ghi: float,
        dhi: float,
        dni: float,
        theta_z_deg: float,
        surface_tilt_deg: float,
        surface_azimuth_deg: float,
        solar_azimuth_deg: float,
        albedo: float = 0.20
    ) -> Dict[str, float]:
        """
        Calcula la irradiancia en el plano del colector (Plane of Array - POA).
        ghi: Global Horizontal (W/m2)
        dhi: Diffuse Horizontal (W/m2)
        dni: Direct Normal (W/m2)
        theta_z_deg: Cenit solar (grados)
        surface_tilt_deg: Inclinacion de los modulos beta (grados, ej. 30 deg)
        surface_azimuth_deg: Azimut de la mesa (0 = Sur, 90 = Oeste, -90 = Este)
        """
        if theta_z_deg >= 89.0 or ghi <= 0:
            return {"poa_global": 0.0, "poa_beam": 0.0, "poa_diffuse": 0.0, "poa_albedo": 0.0}

        theta_z_rad = math.radians(theta_z_deg)
        tilt_rad = math.radians(surface_tilt_deg)

        # Homogeneizar convencion de azimut:
        # Si se pasa en convencion europea (-180..180 con 0=Sur, -90=Este, +90=Oeste),
        # se convierte a azimut astronomico (0=Norte, 90=Este, 180=Sur, 270=Oeste).
        # Si ya se pasa en escala astronomica (ej. 180=Sur), se preserva.
        if abs(surface_azimuth_deg) <= 90.0:
            surf_astro_azimuth = (surface_azimuth_deg + 180.0) % 360.0
        else:
            surf_astro_azimuth = surface_azimuth_deg % 360.0

        gamma_diff_rad = math.radians(solar_azimuth_deg - surf_astro_azimuth)

        # Angulo de incidencia sobre la superficie inclinada (cos theta)
        cos_theta = (
            math.cos(theta_z_rad) * math.cos(tilt_rad) +
            math.sin(theta_z_rad) * math.sin(tilt_rad) * math.cos(gamma_diff_rad)
        )
        cos_theta = max(0.0, cos_theta)
        cos_theta_z = max(0.01, math.cos(theta_z_rad))

        # 1. Componente directa (Beam) acotada por constante solar AM0 (INV-HEL-01: 1361.0 W/m2)
        poa_beam = min(1361.0, max(0.0, dni * cos_theta))

        # 2. Componente de albedo (Ground reflected)
        poa_albedo = ghi * albedo * (1.0 - math.cos(tilt_rad)) / 2.0

        # 3. Componente difusa anisotrópica (Perez)
        if dhi <= 0:
            poa_diffuse = 0.0
        else:
            # Parametros de Perez: epsilon y delta
            kappa = 1.041
            theta_z_cube = (theta_z_rad) ** 3
            eps = ((dhi + dni) / dhi + kappa * theta_z_cube) / (1.0 + kappa * theta_z_cube)
            delta = dhi * 1.0 / (cos_theta_z * 1361.0)

            # Buscar coeficientes
            coeffs = cls.PEREZ_COEFFS[-1]
            for c in cls.PEREZ_COEFFS:
                if c[0] <= eps < c[1]:
                    coeffs = c
                    break

            f11, f12, f13, f21, f22, f23 = coeffs[2:]
            f1 = max(0.0, f11 + f12 * delta + f13 * theta_z_rad)
            f2 = f21 + f22 * delta + f23 * theta_z_rad

            a = max(0.0, cos_theta)
            b = max(math.cos(math.radians(85.0)), cos_theta_z)

            diff_iso = dhi * (1.0 - f1) * (1.0 + math.cos(tilt_rad)) / 2.0
            diff_circum = dhi * f1 * (a / b)
            diff_horizon = dhi * f2 * math.sin(tilt_rad)

            poa_diffuse = max(0.0, diff_iso + diff_circum + diff_horizon)

        poa_global = min(1361.0, max(0.0, poa_beam + poa_diffuse + poa_albedo))

        return {
            "poa_global": round(poa_global, 2),
            "poa_beam": round(poa_beam, 2),
            "poa_diffuse": round(poa_diffuse, 2),
            "poa_albedo": round(poa_albedo, 2),
            "cos_incidence": round(cos_theta, 4)
        }
