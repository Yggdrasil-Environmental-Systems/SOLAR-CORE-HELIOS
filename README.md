---
title: SOLAR-CORE HELIOS V3.0
emoji: ☀️
colorFrom: yellow
colorTo: orange
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: true
license: gpl-3.0
---

# SOLAR-CORE: HELIOS™ | Environmental Cyber-Physical Photovoltaic Engineering & Permitting Platform

> ### ⚖️ REGLA NÚMERO 0 DE TODO EL SISTEMA (AXIOMA SUPREMO DE EXISTENCIA):
> *"Jamás le vamos a poder ganar a la naturaleza, ni a la biología humana; quien no entienda esto, jamás podrá vivir."*  
> — **Kelvin Jesús Flores Yarihuamán**, Fundador y Director Técnico de Yggdrasil Environmental Systems.  
>  
> *Este es el cimiento **ontológico, biofísico y etológico** de todo el ecosistema: la tecnología, los satélites, la termodinámica computacional y la inteligencia artificial no existen para doblegar a la biosfera ni violentar los límites fisiológicos y etológicos del ser humano, sino para comprender sus leyes inmutables, alinearse con ellas y salvaguardar la resiliencia y soberanía de la vida.*
>  
> **Directiva Vinculante:** [`ORDEN_EJECUTIVA_REGLA_CERO_AXIOMA_SUPREMO.md`](./ORDEN_EJECUTIVA_REGLA_CERO_AXIOMA_SUPREMO.md)

---

### Ley 21/2013 Environmental Permitting • Directiva (UE) 2023/2413 (RED III) • RD 102/2011 & Directiva (UE) 2024/2881 Air Dispersion • JRC PVGIS v5.2 Anisotropic Perez (1990) & HDKR Transposition • Faiman (2008) Cell Thermal Model • Multi-MPPT N-TOPCon • BESS Revenue Stacking & Deep RL (TD3) • Physics-Informed Neural Network (PINN)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12-00d2ff.svg?style=flat-square&logo=python)](https://python.org)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23506041-0076ff.svg?style=flat-square)](https://doi.org/10.5281/zenodo.23506041)
[![GitHub Repo](https://img.shields.io/badge/GitHub-SOLAR--CORE--HELIOS-181717.svg?style=flat-square&logo=github)](https://github.com/Yggdrasil-Environmental-Systems/SOLAR-CORE-HELIOS)
[![Streamlit C6ISR](https://img.shields.io/badge/Console-Streamlit%20C6ISR%206--Tabs-ffd60a.svg?style=flat-square&logo=streamlit)](https://yggdrasil-solar-core-helios-kjfy.streamlit.app/)
[![PyTorch Neural Lab](https://img.shields.io/badge/AI%20Engine-PyTorch%20Transformer%20PINN-ee4c2c.svg?style=flat-square&logo=pytorch)](https://pytorch.org)
[![Permitting Standard](https://img.shields.io/badge/Permitting-Ley%2021%2F2013%20%7C%20RED%20III-30d158.svg?style=flat-square)](https://www.boe.es)
[![Solar Standard](https://img.shields.io/badge/Solar%20Physics-Perez%20(1990)%20%7C%20Faiman%20(2008)-ff9f0a.svg?style=flat-square)](https://joint-research-centre.ec.europa.eu/pvgis-photovoltaic-geographical-information-system_en)
[![EU AI Act](https://img.shields.io/badge/Compliance-EU%20AI%20Act%20(2024%2F1689%20Art.%2014)-a855f7.svg?style=flat-square)](https://digital-strategy.ec.europa.eu)
[![ISO 27037](https://img.shields.io/badge/Forensics-ISO%2FIEC%2027037%20SHA--256-ffd600.svg?style=flat-square)](https://www.iso.org)

---

## 🏛️ Acreditación & Identidad Pericial

> **Director Técnico Titular & Lead Systems Architect:**  
> **Kelvin Jesús Flores Yarihuaman**  
> *Máster Universitario Oficial en Ingeniería y Gestión Ambiental*  
> **Cualificación Académica y Profesional:** **MECES Nivel 3 · EQF Level 7** (Nivel Máster Oficial Europeo)  
> *Habilitación Pericial Judicial:* Art. 335 Ley de Enjuiciamiento Civil (LEC) / Cadena de Custodia Digital ISO/IEC 27037  
> **Entidad Colaboradora Protocolizada:** ENTIDAD COLABORADORA DE INGENIERÍA `[EXP-PARTNER-EPC-VAL01]`  
> **Ecosistema:** Yggdrasil Environmental Systems · Madrid / Valencia, España  
> 
> 💼 **LinkedIn Personal:** [linkedin.com/in/kelvinflores-ingenieria](https://www.linkedin.com/in/kelvinflores-ingenieria)  
> 🏢 **LinkedIn Corporativo:** [linkedin.com/company/yggdrasil-environmental-systems](https://www.linkedin.com/company/yggdrasil-environmental-systems)

---

## ☀️ Resumen Ejecutivo y Realidad del Mercado Fotovoltaico

España lidera la transición fotovoltaica europea, pero el despliegue de generación distribuida y plantas *Utility-Scale* se enfrenta a tres cuellos de botella críticos (**Permitting, Red y Canibalización Mayorista**):
1. **El Cuello de Botella de Permitting Ambiental y Territorial:** La tramitación de Declaraciones de Impacto Ambiental (DIA) bajo la **Ley 21/2013**, la zonificación de aceleración renovable (**Directiva UE 2023/2413 RED III**), las servidumbres de líneas de Alta Tensión (**RD 223/2008 / RD 1955/2000**) y la reflectancia especular aeronáutica (**Glint & Glare AESA RD 369/2023**).
2. **Calidad del Aire en Fase de Obra Civil:** El control determinista de la dispersión de material particulado respirable ($PM_{10}$) durante explanación y zanjeo bajo el **Real Decreto 102/2011** y la **Directiva (UE) 2024/2881**.
3. **Curva de Pato OMIE, Precios Cero/Negativos y Curtailment de Red (REE P.O. 3.2):** Los modelos financieros estáticos sobreestiman ingresos al ignorar la canibalización solar en horas centrales, haciendo indispensable el modelado dinámico de precios de captura y la hibridación con baterías LFP (**BESS Revenue Stacking**).

---

## 🎯 Los 3 Demostradores Operativos Integrados

`SOLAR-CORE: HELIOS` articula tres niveles de simulación complementarios desde su selector de emplazamientos:

1. **Caso 1 — Proyecto Real Anonimizado (`FUENTEJARA-PV` · Valencia, Zona Climática B3):**
   * Planta fotovoltaica de **500 kWp** sobre suelo industrial/periurbano en Valencia ($39.47^\circ\text{N}$, $GHI = 1\,720\text{ kWh/m}^2\text{/año}$), con módulos **N-TOPCon 575 Wp**, inversores multi-MPPT de 185 kW y evaluación ambiental real anonimizada bajo protocolo de confidencialidad NDA.
2. **Caso 2 — Gemelo Paramétrico Utility-Scale (`JARAMA-SUR-MAD` · Madrid, Zona Climática D3 CTE):**
   * Planta *Utility-Scale* de **4,95 MWp** en la meseta continental de Madrid ($40.28^\circ\text{N}$, $GHI = 1\,985\text{ kWh/m}^2\text{/año}$), equipada con módulos **N-TOPCon Bifaciales 700 Wp**, seguidores solares 1P y evaluación de corredor de evacuación de **400 kV** y servidumbres aeronáuticas **AESA**.
3. **Caso 3 — Cono Paramétrico Libre Multi-MW (`🌐 Cono Paramétrico Libre + API PVGIS v5.2`):**
   * Simulador abierto ($0,1\text{ a }250\text{ MWp}$) conectado en tiempo real a la **API Oficial JRC PVGIS v5.2 (Comisión Europea)** para cualquier coordenada Lat/Lon de Europa y la Península Ibérica, con degradación garantizada si no existe conectividad externa.

---

## 🏛️ Arquitectura C6ISR de 6 Salas Horizontales

El Cockpit Ejecutivo presenta **6 pestañas horizontales simultáneas** con conmutador bimodal **Open-Core vs. Enterprise**:

| Sala / Pestaña | Motor Científico Open-Core (Público / Zenodo) | Extensión Enterprise Suite (Consultoría IPP / EPC) |
| :--- | :--- | :--- |
| **1. ☀️ Generación Solar & PVGIS** | Transposición anisotrópica de **Perez (1990)** y **HDKR (5 componentes)**, ángulo de incidencia (AOI), modelo térmico de célula de **Faiman (2008)**, telemetría oficial **JRC PVGIS v5.2** y auditoría de PR (**IEC 61724-1**). | Series TMY multi-año completas y calibración piranométrica en planta. |
| **2. ⚡ Inversores, Red & AESA** | Eficiencia de conversión, pérdidas por temperatura en silicio **N-TOPCon Bifacial**, inmunidad **PID (IEC 62804)**, ratio de cortocircuito de red (**SCR**) y reflectancia especular aeronáutica **Glint & Glare 3D (AESA RD 369/2023)**. | Corredor de seguridad de líneas AT **220/400 kV (RD 223/2008, campos CEM)** y estabilidad nodal de tensión con compensación reactiva **STATCOM / P.O. 12.2 REE**. |
| **3. 🌿 Permitting EIA & RED III** | Zonificación ambiental preventiva (**Ley 21/2013**), buffers a **Red Natura 2000**, Dominio Público Hidráulico (**RDL 1/2001**), Vías Pecuarias (**Ley 3/1995**), calificación **RED III (Directiva UE 2023/2413)** y bóveda de **116 normativas oficiales (ISO, IEC, BOE, DOUE)**. | **Generador de Dictamen Pericial EIA (Art. 335 LEC)** con anonimización criptográfica (`AnonymizerProtocol`) y **Monitor de Hitos y Avales RDL 23/2020 (40 €/kW)**. |
| **4. 💨 Dispersión PM10 (Obra)** | Modelo gaussiano de penacho de **Pasquill-Gifford** para movimiento de tierras y obra civil (**RD 102/2011** y **Directiva UE 2024/2881**), con curva de abatimiento por riego cisterna ($75\%$ de retención, $28,4\ \mu\text{g/m}^3$ a $100\text{ m}$). | Acoplamiento meteorológico dinámico local y mapas isoconcentración multi-receptor. |
| **5. 💶 Project Finance & OMIE** | Modelo financiero **DCF a 25 años**, cálculo de **VAN (NPV)**, **TIR (IRR)**, **LCOE** y **Payback** estático. | **Riesgo de Curtailment Nodal REE (P.O. 3.2)**, **Canibalización en Curva de Pato OMIE (Factor de Captura y cláusula PPA Zero-Price Floor)** y **Hibridación BESS LFP (Revenue Stacking)**. |
| **6. 🧠 Neural Lab, Sentinel & ADN** | **IA 1 (`HeliosSpatialTemporalTransformerPINN`, ~11.41M params, $R^2=0.9912$)**, **Centinela Físico en Runtime (`PhysicsSentinelSidecar`: 7 invariantes + 9 límites de clamping)** y **Bóveda Epistémica de 12 Papers Seminales PDF**. | **IA 2 (`HeliosBESSDeepActorCritic` TD3, ~5.96M params, $SOH=99.67\%\text{/año}$)** para arbitraje continuo de baterías BESS en mercados OMIE + Banda Secundaria aFRR REE + Curtailment. |

---

## 🛡️ La Doble Armadura Soberana (`ATHENA` & `ASTRAEA`)

1. **Cápsula Termodinámica & Epistémica (`AI-CORE: ATHENA` · `physics/` & `data/papers_seminales/`):**
   * `physics/scientific_dna.json` & `physics/sentinel_sidecar.py`: Fiscaliza en tiempo de ejecución **7 invariantes físicos** (límite radiativo extraterrestre AM0 $G_{POA} \le 1\,361\text{ W/m}^2$, positividad fotónica, balance térmico de Faiman, cota termodinámica de Shockley-Queisser / c-Si $\eta \le 29,4\%$, saturación de potencia AC de inversor, conservación estequiométrica de baterías y no-negatividad gaussiana de $PM_{10}$) y **9 límites duros de clamping**.
   * Bóveda documental con **12 papers seminales verificados** (Perez 1990, Hay & Davies 1980, Klucher 1979, Reindl 1990, Faiman 2008, King/Sandia 2004, De Soto 2006, Shockley & Queisser 1961, Richter 2013, Ho 1993, Pasquill 1961, Gifford 1961).
2. **Cápsula Jurídica & Forense (`VERI-AUDIT: ASTRAEA` · `compliance/`):**
   * `compliance/regulatory_dna.json`: Compendio de **116 normativas oficiales auditadas** estructuradas en **5 Pilares Jurídicos**, incorporando:
     * **Estándares ISO/IEC:** `IEC 61724-1:2021` (Monitoring & PR), `IEC 61215:2021` (Confiabilidad TOPCon), `IEC 61730:2023` (Seguridad fuego/eléctrica), `IEC 62446-1:2018` (Commissioning y ensayos I-V), `IEC 62109` (Inversores), `IEC TS 62804-1` (PID), `ISO/IEC 42001:2023` (Gestión de IA / AIMS), `ISO 45001:2018` (SST en obra civil), `ISO 14064` (Huella GEI), `ISO 14001:2015` (SGA), `ISO 50001:2018` (SGE), `ISO 14040/44` (ACV/LCA), `ISO 23247` (Gemelos Digitales) e `ISO/IEC 27037:2012` (Custodia Forense).
     * **Marco Eléctrico, de Red y BESS:** `Ley 24/2013`, `RDL 23/2020` (Avales 40 €/kW), `RDL 8/2023` (Hibridación BESS), `RD 1183/2020`, `RD 223/2008` (RAT líneas AT e ITC-LAT 01-09), `RD 337/2014` (Subestaciones SET), `RD 842/2002` (REBT ITC-BT 40), `P.O. 12.2 REE` (Huecos de tensión/FRT), `P.O. 3.2` (Curtailment) y `P.O. 7.2/7.3` (aFRR/mFRR).

---

## 🚀 Guía de Inicio Rápido (Quickstart)

### Opción 1: Lanzador Directo en 1-Clic (Windows)
```bash
INICIAR_HELIOS_V1.bat
```

### Opción 2: Ejecución Manual en Terminal
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar consola ejecutiva C6ISR
streamlit run app/main.py
```

---

## 🧪 Batería de Pruebas Automatizadas (`pytest`)

El repositorio cuenta con **46 pruebas unitarias y de integración** que verifican los motores físicos, regulatorios, financieros, neuronales y la interfaz completa de 6 pestañas:
```bash
pytest -v
```
**Resultado certificado:** `46 passed in 35.14s (100% PASS)`.

---

## 📜 Licenciamiento Dual (Open-Core vs. Enterprise)

* **Edición Open-Core (Zenodo / CERN & Hugging Face Spaces):** Liberada bajo **GNU GPLv3 / MIT** (código abierto) y **CC BY-NC-SA 4.0** (documentación y modelos físicos abiertos) para reproducibilidad científica y verificación académica.
* **Edición Enterprise Suite:** Los motores de arbitraje BESS con Deep RL (`enterprise/`), análisis de riesgo de curtailment y precios negativos OMIE, corredores de alta tensión y generador de dictámenes periciales EIA constituyen propiedad intelectual reservada bajo licencia comercial de **Kelvin Jesús Flores Yarihuaman — Yggdrasil Environmental Systems**.
