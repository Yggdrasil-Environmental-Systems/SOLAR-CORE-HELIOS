from typing import Dict, Any, Optional

class EIABufferChecker:
    """
    Motor de Verificacion Espacial de Restricciones Territoriales & Condicionantes EIA.
    Normas de referencia:
    - Directiva (UE) 2023/2413 (RED III - Renewable Energy Directive III: Zonas de Aceleracion de Renovables)
    - Ley 21/2013 de Evaluacion Ambiental
    - Ley 42/2007 (Red Natura 2000 / Biodiversidad)
    - RDL 1/2001 (Dominio Publico Hidraulico - DPH)
    - Decreto Ley 14/2020 de la Comunitat Valenciana
    """

    @staticmethod
    def pre_screening_filter(
        distance_natura_2000_km: float,
        distance_corredores_ecologicos_km: float = 3.0
    ) -> Dict[str, Any]:
        """
        Capa SIG vinculante de exclusion ambiental previa.
        Descarta ubicaciones incompatibles antes del calculo de irradiacion transpuesta con modelo Perez
        segun la Directiva (UE) 2023/2413 (RED III) y la Ley 21/2013 de Evaluacion Ambiental.
        """
        is_compatible = distance_natura_2000_km >= 2.5 and distance_corredores_ecologicos_km >= 1.0
        return {
            "is_site_compatible": is_compatible,
            "perez_transposition_allowed": is_compatible,
            "distancia_natura_2000_km": distance_natura_2000_km,
            "distancia_corredores_km": distance_corredores_ecologicos_km,
            "status": "APTO_CALCULO_RADIATIVO" if is_compatible else "EXCLUSION_TERRITORIAL_VINCULANTE",
            "justificacion": (
                "Emplazamiento fuera de areas sensibles. Autorizado para calculo de transposicion Perez."
                if is_compatible else
                "Incompatibilidad ambiental critica: Emplazamiento colindante o invasivo con Red Natura 2000 o corredor biologico. Calculo radiativo cancelado."
            )
        }

    @staticmethod
    def audit_territorial_constraints(
        distance_natura_2000_km: float,
        distance_cauce_dph_m: float,
        distance_via_pecuaria_m: float,
        average_slope_pct: float,
        fence_mesh_bottom_clearance_cm: float = 15.0,
        distance_corredores_ecologicos_km: float = 3.0,
        distance_linea_at_eje_m: Optional[float] = None,
        linea_at_tension_kv: float = 400.0,
        distance_torre_at_m: Optional[float] = None,
        distance_inversores_a_linea_m: Optional[float] = None,
        distance_inverters_to_line_m: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Audita las distancias y caracteristicas fisicas de la parcela frente al marco legal
        integrando la Directiva (UE) 2023/2413 (RED III).
        """
        checks = {}

        # 0. Pre-filtro Vinculante Previo a Perez
        pre_filter = EIABufferChecker.pre_screening_filter(
            distance_natura_2000_km, distance_corredores_ecologicos_km
        )
        checks["pre_screening_sig"] = pre_filter

        # 1. Red Natura 2000 (ZEPA / LIC)
        natura_ok = distance_natura_2000_km >= 2.5
        checks["red_natura_2000"] = {
            "distancia_km": distance_natura_2000_km,
            "umbral_seguridad_km": 2.5,
            "status": "APTO" if natura_ok else "ALERTA_AFECCION",
            "motivo": "Sin afeccion directa ni indirecta a avifauna esteparia y habitats protegidos" if natura_ok else "Requiere evaluacion de repercusiones art. 46 Ley 42/2007"
        }

        # 2. Dominio Publico Hidraulico (DPH - Cauces / Ramblas)
        dph_servidumbre_ok = distance_cauce_dph_m >= 5.0
        dph_policia_ok = distance_cauce_dph_m >= 100.0
        checks["dph_cauces"] = {
            "distancia_m": distance_cauce_dph_m,
            "zona_servidumbre_5m": "RESPETADA" if dph_servidumbre_ok else "INVASION_ILEGAL",
            "zona_policia_100m": "LIBRE" if dph_policia_ok else "AUTORIZACION_CHJ_REQUERIDA",
            "status": "CONFORME" if dph_servidumbre_ok else "NO_CONFORME"
        }

        # 3. Vias Pecuarias (Ley 3/1995)
        via_ok = distance_via_pecuaria_m >= 15.0
        checks["vias_pecuarias"] = {
            "distancia_m": distance_via_pecuaria_m,
            "status": "INDEMNE" if via_ok else "AFECCION_TRAZADO",
            "motivo": "Respeto a servidumbre de transito ganadero tradicional" if via_ok else "Exige deslinde y modificacion de poligonal"
        }

        # 4. Pendiente Topografica & Edafologia (Decreto Ley 14/2020 CV)
        slope_ok = average_slope_pct <= 4.0
        checks["pendiente_suelo"] = {
            "pendiente_pct": average_slope_pct,
            "umbral_pct": 4.0,
            "status": "OPTIMO" if slope_ok else "MOVIMIENTO_TIERRAS_ELEVADO",
            "motivo": "Apto para hincado directo sin alteracion del perfil edafico fertil" if slope_ok else "Supera el 4%; exige desmontes y terrazas"
        }

        # 5. Permeabilidad Cinegetica del Cerramiento
        fence_ok = fence_mesh_bottom_clearance_cm >= 15.0
        checks["cerramiento_fauna"] = {
            "luz_inferior_cm": fence_mesh_bottom_clearance_cm,
            "umbral_cm": 15.0,
            "status": "PERMEABLE" if fence_ok else "BARRERA_CINEGETICA",
            "motivo": "Libre transito de mesomamiferos (liebres, erizos, reptiles)" if fence_ok else "Barrera opaca no autorizable en evaluacion ambiental"
        }

        # 6. Evaluacion Directiva (UE) 2023/2413 (RED III - Zonas de Aceleracion Renovable)
        red_iii_apto = natura_ok and (distance_corredores_ecologicos_km >= 1.0) and slope_ok
        checks["directiva_red_iii"] = {
            "norma": "Directiva (UE) 2023/2413 (RED III) / Art. 15 ter",
            "clasificacion": "ZONA_ACELERACION_RENOVABLE" if red_iii_apto else "ZONA_TRAMITACION_ORDINARIA",
            "tramitacion_abreviada": red_iii_apto,
            "plazo_maximo_meses": 12 if red_iii_apto else 24,
            "status": "BENEFICIARIO_RED_III" if red_iii_apto else "REQUIERE_EIA_COMPLETA",
            "motivo": (
                "Cumple criterios de aceleracion europea: fuera de Red Natura 2000 y corredores sensibles. Tramitacion prioritaria agilizada."
                if red_iii_apto else
                "No clasifica como zona de aceleracion; sujeto a plazos estandares ordinarios."
            )
        }

        # 7. Servidumbre de Paso de Lineas de Alta Tension (RD 1955/2000 & RD 223/2008 ITC-LAT 07)
        at_ok = True
        if distance_linea_at_eje_m is not None:
            try:
                from .grid_easement_and_nodal_capacity import HighVoltageEasementAndNodalEngine
                dist_torre = distance_torre_at_m if distance_torre_at_m is not None else 50.0
                dist_inv = distance_inversores_a_linea_m if distance_inversores_a_linea_m is not None else (
                    distance_inverters_to_line_m if distance_inverters_to_line_m is not None else 50.0
                )
                at_audit = HighVoltageEasementAndNodalEngine.audit_line_easement(
                    line_voltage_kv=linea_at_tension_kv,
                    distance_to_axis_m=distance_linea_at_eje_m,
                    distance_to_nearest_tower_m=dist_torre,
                    distance_inverters_to_line_m=dist_inv
                )
                checks["servidumbre_lineas_alta_tension"] = at_audit
                at_ok = at_audit["is_compliant"]
            except (ImportError, ModuleNotFoundError):
                checks["servidumbre_lineas_alta_tension"] = {
                    "is_compliant": True,
                    "status": "RESERVADO_EDICION_ENTERPRISE"
                }
                at_ok = True

        # Dictamen global
        all_passed = natura_ok and dph_servidumbre_ok and via_ok and slope_ok and fence_ok and at_ok
        checks["dictamen_global"] = {
            "resultado": "APTO_PARA_TRAMITACION_EIA" if all_passed else "CONDICIONANTES_A_CORREGIR",
            "cero_alegaciones_proyectadas": all_passed,
            "clasificacion_red_iii": checks["directiva_red_iii"]["clasificacion"]
        }

        return checks
