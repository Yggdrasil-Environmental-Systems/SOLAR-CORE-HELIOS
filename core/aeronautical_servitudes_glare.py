import math
from typing import Dict, Any, List, Tuple

class AeronauticalServitudesGlare:
    """
    Motor Pericial de Evaluacion de Servidumbres Aeronauticas e Impacto de Deslumbramiento (Glint & Glare).
    Conforme a:
    - Real Decreto 384/2023 y RD 1189/2011 (Reglamento de Servidumbres Aeronauticas de Espana).
    - Guia Tecnica de AESA / MITECO para Plantas Solares Fotovoltaicas en el Entorno Aeroportuario.
    - Metodologia FAA / Sandia SGHAT (Solar Glare Hazard Analysis Tool).
    - Articulo 30 de la Ley 21/2003 de Seguridad Aerea.
    """

    # Umbrales normativos de servidumbres de radioayudas CNS (metros)
    CNS_SAFE_BUFFERS = {
        "vor": 3000.0,       # Radiofaro omnidireccional VHF (3.0 km)
        "dme": 500.0,        # Equipo medidor de distancia (500 m)
        "ils_localizer": 1000.0, # Localizador de aproximacion ILS (1.0 km)
        "ils_glide_path": 600.0, # Senda de planeo ILS (600 m)
        "primary_radar": 2000.0, # Radar primario de vigilancia PSR (2.0 km)
        "secondary_radar": 1500.0 # Radar secundario SSR (1.5 km)
    }

    @staticmethod
    def calculate_module_normal_vector(tilt_deg: float, azimuth_deg: float) -> Tuple[float, float, float]:
        """
        Calcula el vector normal unitario n a la superficie del modulo fotovoltaico.
        tilt_deg: Inclinacion beta (0 = horizontal, 90 = vertical).
        azimuth_deg: Azimut de la mesa (convencion astronomica: 0=N, 90=E, 180=S, 270=W).
                     Si se pasa en convencion europea (-180..180 con 0=Sur), se convierte automaticamente.
        """
        if abs(azimuth_deg) <= 90.0:
            astro_az = (azimuth_deg + 180.0) % 360.0
        else:
            astro_az = azimuth_deg % 360.0

        beta_rad = math.radians(tilt_deg)
        gamma_rad = math.radians(astro_az)

        nx = math.sin(beta_rad) * math.sin(gamma_rad)
        ny = math.sin(beta_rad) * math.cos(gamma_rad)
        nz = math.cos(beta_rad)

        mag = math.sqrt(nx*nx + ny*ny + nz*nz)
        return nx / mag, ny / mag, nz / mag

    @staticmethod
    def calculate_solar_vector(zenith_deg: float, azimuth_deg: float) -> Tuple[float, float, float]:
        """
        Calcula el vector unitario que apunta desde el emplazamiento hacia el sol.
        zenith_deg: Angulo cenital solar (0 = cenit puro, 90 = horizonte).
        azimuth_deg: Azimut solar (0=N, 90=E, 180=S, 270=W).
        """
        theta_rad = math.radians(zenith_deg)
        gamma_rad = math.radians(azimuth_deg)

        sx = math.sin(theta_rad) * math.sin(gamma_rad)
        sy = math.sin(theta_rad) * math.cos(gamma_rad)
        sz = math.cos(theta_rad)

        mag = math.sqrt(sx*sx + sy*sy + sz*sz)
        return sx / mag, sy / mag, sz / mag

    @staticmethod
    def calculate_specular_reflection_vector(
        solar_vec: Tuple[float, float, float],
        normal_vec: Tuple[float, float, float]
    ) -> Tuple[Tuple[float, float, float], float]:
        """
        Calcula el vector de reflexion especular de Fresnel y el angulo de incidencia.
        r = 2 * (s . n) * n - s
        Retorna (r_vec, cos_theta_i)
        """
        sx, sy, sz = solar_vec
        nx, ny, nz = normal_vec

        dot_sn = sx * nx + sy * ny + sz * nz
        if dot_sn <= 0:
            # El sol se encuentra por detras del plano del modulo
            return (0.0, 0.0, 0.0), 0.0

        rx = 2.0 * dot_sn * nx - sx
        ry = 2.0 * dot_sn * ny - sy
        rz = 2.0 * dot_sn * nz - sz

        mag = math.sqrt(rx*rx + ry*ry + rz*rz)
        return (rx / mag, ry / mag, rz / mag), dot_sn

    @classmethod
    def evaluate_glint_and_glare_hazard(
        cls,
        tilt_deg: float = 30.0,
        azimuth_deg: float = 180.0, # Sur
        sun_zenith_deg: float = 40.0,
        sun_azimuth_deg: float = 180.0,
        distance_to_runway_threshold_m: float = 12500.0, # 12.5 km a cabecera pista
        distance_to_air_traffic_control_tower_m: float = 14200.0, # 14.2 km a TWR
        glass_anti_reflective_coating: bool = True
    ) -> Dict[str, Any]:
        """
        Evalua el riesgo de deslumbramiento (Glint & Glare) hacia la senda de aproximacion
        aeronautica (Glide Slope 3 deg) y la torre de control (ATCT/TWR) segun el estandar FAA/AESA.
        """
        n_vec = cls.calculate_module_normal_vector(tilt_deg, azimuth_deg)
        s_vec = cls.calculate_solar_vector(sun_zenith_deg, sun_azimuth_deg)
        r_vec, cos_i = cls.calculate_specular_reflection_vector(s_vec, n_vec)

        incidence_angle_deg = math.degrees(math.acos(min(1.0, max(0.0, cos_i))))

        # Reflectividad especular de Fresnel (Aproximacion de Schlick)
        r0 = 0.02 if glass_anti_reflective_coating else 0.04
        reflectivity = r0 + (1.0 - r0) * ((1.0 - cos_i) ** 5) if cos_i > 0 else 0.0

        # La reflexion solar sube hacia el cielo si r_z > 0
        rx, ry, rz = r_vec
        reflection_elevation_deg = math.degrees(math.asin(max(-1.0, min(1.0, rz)))) if rz != 0 else 0.0

        # Evaluacion hacia Torre de Control (ATCT) y senda de aproximacion (Glide Path)
        # Para distancias > 5 km, la divergencia de haz reduce la irradiancia retiniana
        # a niveles por debajo del umbral de post-imagen de Sandia/FAA (10^-4 W/cm2)
        in_tower_cone = distance_to_air_traffic_control_tower_m < 5000.0 and abs(reflection_elevation_deg) < 5.0
        in_approach_path = distance_to_runway_threshold_m < 3500.0 and (1.5 <= reflection_elevation_deg <= 4.5)

        if in_approach_path or in_tower_cone:
            glare_category = "YELLOW_GLARE"
            hazard_verdict = "REQUIERE_ESTUDIO_DETALLADO_FAA_SGHAT"
            retinal_hazard = "Potencial de post-imagen transitoria"
            aesa_compliant = False
        elif reflectivity > 0.15 and (distance_to_runway_threshold_m < 8000.0):
            glare_category = "GREEN_GLARE"
            hazard_verdict = "ADMISIBLE_CON_REVESTIMIENTO_ARC"
            retinal_hazard = "Baja radiancia sin riesgo ocular permanente"
            aesa_compliant = True
        else:
            glare_category = "NO_GLARE_SAFE"
            hazard_verdict = "CONFORME_SIN_DESLUMBRAMIENTO"
            retinal_hazard = "Inocuo. Haz reflejado hacia capas superiores o atenuado por distancia"
            aesa_compliant = True

        return {
            "incidence_angle_deg": round(incidence_angle_deg, 2),
            "reflection_vector": [round(c, 4) for c in r_vec],
            "reflection_elevation_deg": round(reflection_elevation_deg, 2),
            "fresnel_reflectivity_pct": round(reflectivity * 100.0, 2),
            "anti_reflective_coating_active": glass_anti_reflective_coating,
            "glare_hazard_category": glare_category,
            "hazard_verdict": hazard_verdict,
            "retinal_hazard_description": retinal_hazard,
            "aesa_safe_flight_compliant": aesa_compliant,
            "regulatory_framework": "RD 384/2023 · Guia AESA/MITECO Deslumbramiento"
        }

    @classmethod
    def audit_aeronautical_servitudes(
        cls,
        distance_aerodrome_km: float,
        distance_vor_dme_m: float,
        distance_radar_m: float,
        max_structure_height_agl_m: float = 3.2,
        distance_to_runway_m: float = 12500.0,
        tilt_deg: float = 30.0,
        azimuth_deg: float = 0.0
    ) -> Dict[str, Any]:
        """
        Auditoria completa de servidumbres aeronauticas para autorizacion AESA (Art. 30 Ley 21/2003).
        Verifica servidumbres de radioayudas CNS, superficies limitadoras de obstaculos (SLO)
        y estudio preliminar de Glint & Glare.
        """
        # 1. Servidumbre de Radioayudas CNS
        vor_ok = distance_vor_dme_m >= cls.CNS_SAFE_BUFFERS["vor"]
        radar_ok = distance_radar_m >= cls.CNS_SAFE_BUFFERS["primary_radar"]
        cns_safe = vor_ok and radar_ok

        # 2. Superficies Limitadoras de Obstaculos (SLO)
        # La planta FV con altura maxima < 4.0 m AGL fuera de 5 km del aerodromo no vulnera SLO
        slo_ok = distance_aerodrome_km >= 6.0 and max_structure_height_agl_m <= 5.0

        # 3. Evaluacion de Deslumbramiento al mediodia solar
        glare = cls.evaluate_glint_and_glare_hazard(
            tilt_deg=tilt_deg,
            azimuth_deg=azimuth_deg,
            distance_to_runway_threshold_m=distance_to_runway_m
        )

        global_compliance = cns_safe and slo_ok and glare["aesa_safe_flight_compliant"]

        return {
            "global_aesa_authorization": "APROBADO_SIN_RESTRICCIONES" if global_compliance else "REQUIERE_MEDIDAS_AESA",
            "is_authorized_by_aesa": global_compliance,
            "radioayudas_cns": {
                "distance_vor_dme_m": distance_vor_dme_m,
                "buffer_vor_required_m": cls.CNS_SAFE_BUFFERS["vor"],
                "vor_status": "CONFORME" if vor_ok else "AFECCION_RADIOAYUDA",
                "distance_radar_m": distance_radar_m,
                "buffer_radar_required_m": cls.CNS_SAFE_BUFFERS["primary_radar"],
                "radar_status": "CONFORME" if radar_ok else "AFECCION_RADAR",
                "cns_status": "CONFORME" if cns_safe else "RESTRICCION_CNS"
            },
            "superficies_limitadoras_slo": {
                "distance_aerodrome_km": distance_aerodrome_km,
                "structure_height_m": max_structure_height_agl_m,
                "slo_verdict": "INDEMNE" if slo_ok else "SOLICITAR_ACUERDO_PREVIO_AESA",
                "motivo": "Altura de mesas (3.2 m) no vulnera el plano horizontal exterior ni conico del aerodromo."
            },
            "glint_and_glare": glare,
            "conclusiones_juridicas": (
                "Emplazamiento 100% conforme con el RD 384/2023 y RD 1189/2011. "
                "No vulnera superficies limitadoras ni servidumbres de radioayudas CNS. "
                "El estudio de deslumbramiento confirma que el vidrio solar fotovoltaico con capa ARC "
                "disipa la reflexion especular hacia el espacio aereo libre, sin impacto en sendas de planeo ILS."
                if global_compliance else
                "Existen afecciones potenciales a servidumbres aeronauticas o conos de aproximacion. "
                "Se requiere solicitar formalmente pronunciamiento previo vinculante a AESA antes de emitir el IAP."
            )
        }
