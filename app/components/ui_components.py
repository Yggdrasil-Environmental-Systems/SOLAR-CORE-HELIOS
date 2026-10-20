# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path
from typing import Dict, Any, List


def format_es_num_str(text: str) -> str:
    """
    Formatea cadenas numéricas siguiendo el estándar español / SI (UNE 82100 / RAE):
    - Separador de miles: espacio (' ')
    - Separador decimal: coma (',')
    Preserva numeración normativa como P.O. 12.2, PO 12.2, P.O. 3.2, P.O. 7.2, Art. 335.2.
    """
    s = str(text)
    protected = {}

    def _protect(m):
        key = f"__PROT{len(protected)}__"
        protected[key] = m.group(0)
        return key

    s = re.sub(
        r"(?:P\.?O\.?\s*\d+\.\d+|Art\.\s*\d+\.\d+|D\d+\.\d+|v\d+\.\d+(?:\.\d+)?|ISO\s*\d+-\d+|IEC\s*\d+-\d+)",
        _protect,
        s,
    )

    # Números con coma de miles de Python y punto decimal opcional: ej. 360,000.50 o 1,720 o 4,950
    def _repl_py_thousands(m):
        int_part = m.group(1).replace(",", " ")
        dec_part = m.group(2)
        return f"{int_part},{dec_part}" if dec_part is not None else int_part

    s = re.sub(r"\b(\d{1,3}(?:,\d{3})+)(?:\.(\d+))?\b", _repl_py_thousands, s)

    # Números con punto de miles español (exactamente 3 dígitos tras punto antes de unidad)
    s = re.sub(r"\b(\d{1,3})\.(\d{3})\b(?=\s*(?:€|MW|kW|kWp|módulos|tCO|MWh|kWh|m\b))", r"\1 \2", s)

    # Números de 4 a 6 dígitos seguidos de unidad física (ej. 6200 m -> 6 200 m, 4500 MVA -> 4 500 MVA)
    def _repl_plain_thousands(m):
        num = m.group(1)
        unit = m.group(2)
        formatted = f"{int(num):,}".replace(",", " ")
        return f"{formatted}{unit}"

    s = re.sub(
        r"\b(\d{4,6})(\s*(?:m\b|km\b|W/m²|kW\b|kWp\b|MW\b|MWp\b|MVA\b|kVA\b|kWh|MWh|€|params))",
        _repl_plain_thousands,
        s,
    )

    # Decimales con punto -> coma decimal (ej. 58.73 -> 58,73; 0.35 -> 0,35)
    s = re.sub(r"(\d+)\.(\d+)", r"\1,\2", s)

    for k, v in protected.items():
        s = s.replace(k, v)
    return s


def load_catalog_sites() -> List[Dict[str, Any]]:
    """
    Carga el catálogo oficial de escenarios de simulación fotovoltaica.
    Garantiza que por defecto aparezca el escenario de referencia auditado (Fuentejara 500 kWp).
    Permite cargar automáticamente futuros emplazamientos añadidos a configs/sites/*.json.
    """
    root_dir = Path(__file__).resolve().parent.parent.parent
    catalog_path = root_dir / "data" / "missions" / "catalog_missions.json"
    sites = []
    if catalog_path.exists():
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            sites = list(data.get("active_sites", []))

    sites_dir = root_dir / "configs" / "sites"
    if sites_dir.exists():
        for site_file in sorted(sites_dir.glob("*.json")):
            try:
                with open(site_file, "r", encoding="utf-8") as sf:
                    sites.append(json.load(sf))
            except Exception:
                pass

    return sites


def render_kpi_card_html(title: str, value: str, subtext: str = "", badge_text: str = "", is_compliant: bool = True) -> str:
    """Renderiza tarjeta KPI con diseño corporativo HELIOS y formato numérico español (coma decimal y espacio de miles)."""
    clean_title = format_es_num_str(str(title).replace("_", " "))
    clean_value = format_es_num_str(str(value).replace("_", " "))
    clean_subtext = format_es_num_str(str(subtext).replace("_", " "))
    clean_badge = format_es_num_str(str(badge_text).replace("_", " "))
    badge_html = ""
    if clean_badge:
        badge_class = "badge-compliant" if is_compliant else "badge-alert"
        badge_html = f'<span class="{badge_class}">{clean_badge}</span>'

    return f"""
    <div class="helios-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="kpi-title">{clean_title}</div>
            {badge_html}
        </div>
        <div class="kpi-value">{clean_value}</div>
        <div class="kpi-subtext">{clean_subtext}</div>
    </div>
    """
