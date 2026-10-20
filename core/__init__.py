"""
SOLAR-CORE: HELIOS - Open-Core Physics, Optics & EIA Algorithms
YGGDRASIL Environmental Systems
"""

from .solar_geometry import SolarGeometry
from .perez_transposition import PerezTransposition
from .thermal_degradation import ThermalDegradationModel
from .multi_mppt_engine import MultiMPPTEngine
from .air_dispersion_gauss import GaussianAirDispersion
from .eia_buffer_checker import EIABufferChecker
from .financial_dcf_engine import FinancialDCFEngine
from .hdkr_transposition import HDKRTransposition
from .official_telemetry_service import OfficialTelemetryService

try:
    from .grid_easement_and_nodal_capacity import HighVoltageEasementAndNodalEngine
except (ImportError, ModuleNotFoundError):
    HighVoltageEasementAndNodalEngine = None

__all__ = [
    "SolarGeometry",
    "PerezTransposition",
    "HDKRTransposition",
    "HighVoltageEasementAndNodalEngine",
    "OfficialTelemetryService",
    "ThermalDegradationModel",
    "MultiMPPTEngine",
    "GaussianAirDispersion",
    "EIABufferChecker",
    "FinancialDCFEngine",
]
