import math
from typing import Tuple, Dict

class SolarGeometry:
    """
    Motor analitico de trigonometria esferica solar y posicionamiento astronomico.
    Ecuaciones exactas de Duffie & Beckman y Cooper (1969).
    """

    @staticmethod
    def solar_declination_deg(day_of_year: int) -> float:
        """Calcula la declinacion solar en grados (Cooper, 1969)."""
        angle_rad = math.radians((360.0 / 365.0) * (284 + day_of_year))
        return 23.45 * math.sin(angle_rad)

    @staticmethod
    def equation_of_time_min(day_of_year: int) -> float:
        """Ecuacion del tiempo en minutos (Spencer, 1971)."""
        b = math.radians((360.0 / 365.0) * (day_of_year - 81))
        eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
        return eot

    @staticmethod
    def hour_angle_deg(solar_hour: float) -> float:
        """Angulo horario omega en grados (15 grados por hora, 0 a mediodia solar)."""
        return 15.0 * (solar_hour - 12.0)

    @staticmethod
    def solar_zenith_azimuth(lat_deg: float, day_of_year: int, solar_hour: float) -> Tuple[float, float]:
        """
        Calcula el angulo cenital theta_z y el azimut solar gamma_s en grados.
        lat_deg: Latitud en grados decimales (positiva al Norte).
        """
        phi = math.radians(lat_deg)
        delta = math.radians(SolarGeometry.solar_declination_deg(day_of_year))
        omega = math.radians(SolarGeometry.hour_angle_deg(solar_hour))

        # Coseno del cenit
        cos_theta_z = math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.cos(omega)
        cos_theta_z = max(-1.0, min(1.0, cos_theta_z))
        theta_z_rad = math.acos(cos_theta_z)
        theta_z_deg = math.degrees(theta_z_rad)

        if theta_z_deg >= 90.0:
            return 90.0, 0.0

        # Azimut solar
        sin_theta_z = math.sin(theta_z_rad)
        if sin_theta_z > 1e-5:
            cos_gamma = (math.sin(delta) * math.cos(phi) - math.cos(delta) * math.sin(phi) * math.cos(omega)) / sin_theta_z
            cos_gamma = max(-1.0, min(1.0, cos_gamma))
            gamma_s_deg = math.degrees(math.acos(cos_gamma))
            if omega > 0:
                gamma_s_deg = 360.0 - gamma_s_deg
        else:
            gamma_s_deg = 0.0

        return theta_z_deg, gamma_s_deg

    @staticmethod
    def extraterrestrial_irradiance(day_of_year: int) -> float:
        """Constante solar ajustada por excentricidad orbital (W/m2)."""
        g_sc = 1367.0
        angle = math.radians(360.0 * day_of_year / 365.0)
        return g_sc * (1.0 + 0.033 * math.cos(angle))
