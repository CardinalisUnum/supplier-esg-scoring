import yaml
import random
import math
import numpy as np
from src.db.models import Supplier, IndicatorDefinition, ESGSurvey, Audit, ESGScore

# --- 1. CONFIGURATION & ENTITY GENERATION ---

def load_config(filepath="configs/simulation_v1.yaml") -> dict:
    """Loads the statistical parameters and taxonomy from the YAML config."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def generate_suppliers(num_suppliers: int, config: dict) -> list[Supplier]:
    """Generates suppliers matching the 6-table schema and Philippine context[cite: 22, 27]."""
    suppliers = []
    industries = config['taxonomy']['industries']
    regions = config['taxonomy']['regions']
    sizes = config['taxonomy']['sizes']
    operating_contexts = ['urban', 'industrial', 'rural']
    
    for _ in range(num_suppliers):
        region = random.choice(regions)
        context = random.choice(operating_contexts)
        
        # Latent logic [cite: 48-50]
        maturity = np.clip(np.random.beta(config['parameters']['esg_maturity_shape_alpha'], 
                                          config['parameters']['esg_maturity_shape_beta']), 0, 1)
        efficiency = np.clip(np.random.normal(1.0, 0.15), 0.6, 1.4)
        
        grid_int = "high" if context == "industrial" else "med" if context == "urban" else "low"
        reg_press = "high" if region == "NCR" else "med"
        
        suppliers.append(Supplier(
            industry=random.choice(industries),
            region=region,
            operating_context=context,
            size_tier=random.choice(sizes),
            scale_spend=round(np.random.lognormal(10, 1), 2),
            esg_maturity=round(maturity, 3),
            efficiency_factor=round(efficiency, 3),
            grid_intensity=grid_int,
            regulatory_pressure=reg_press
        ))
    return suppliers

# --- 2. INDICATORS & SURVEYS (THE BIAS ENGINE) ---

def seed_indicators() -> list[IndicatorDefinition]:
    """Creates the 8 core ESG indicators mandated by the spec [cite: 66-74]."""
    return [
        IndicatorDefinition(id="co2_emissions", category="E", subcategory="emissions", metric_type="continuous", unit="tonsCO2e", bias_direction=-1, survey_method="direct"),
        IndicatorDefinition(id="energy_consumption", category="E", subcategory="energy", metric_type="continuous", unit="MWh", bias_direction=-1, survey_method="direct"),
        IndicatorDefinition(id="renewable_energy_pct", category="E", subcategory="energy", metric_type="percent", unit="%", bias_direction=1, survey_method="indirect"),
        IndicatorDefinition(id="injury_rate", category="S", subcategory="safety", metric_type="continuous", unit="per_100FTE", bias_direction=-1, survey_method="indirect"),
        IndicatorDefinition(id="labor_violations", category="S", subcategory="labor", metric_type="count", unit="count", bias_direction=-1, survey_method="estimated"),
        IndicatorDefinition(id="training_hours", category="S", subcategory="training", metric_type="continuous", unit="hours", bias_direction=1, survey_method="indirect"),
        IndicatorDefinition(id="anti_corruption_policy", category="G", subcategory="policy", metric_type="binary", unit="yes/no", bias_direction=1, survey_method="direct"),
        IndicatorDefinition(id="esg_reporting_framework", category="G", subcategory="policy", metric_type="binary", unit="yes/no", bias_direction=1, survey_method="direct")
    ]

def generate_surveys(suppliers: list, indicators: list, alpha=0.15, beta=1.5) -> list[ESGSurvey]:
    """Applies dynamic mathematical greenwashing bias [cite: 120-121, 140-141]."""
    surveys = []
    method_factors = {"direct": 1.0, "indirect": 0.6, "estimated": 0.3}
    reg_factors = {"low": 1.0, "med": 0.8, "high": 0.6}
    
    for supplier in suppliers:
        reg_factor = reg_factors.get(supplier.regulatory_pressure, 1.0)
        bias_mag = alpha * (supplier.esg_maturity ** beta) 
        
        for ind in indicators:
            # 1. Generate True Value
            true_val = 0.0
            if ind.metric_type == "continuous":
                true_val = max(0, np.random.normal(100, 20) * (1.5 - supplier.esg_maturity))
            elif ind.metric_type == "percent":
                true_val = np.clip(np.random.normal(40 + (supplier.esg_maturity * 30), 10), 0, 100)
            elif ind.metric_type == "count":
                true_val = float(np.random.poisson(5 * (1 - supplier.esg_maturity)))
            elif ind.metric_type == "binary":
                p = 1 / (1 + math.exp(-(-1 + 3 * supplier.esg_maturity))) 
                true_val = 1.0 if np.random.random() < p else 0.0

            # 2. Apply Distortion
            method_factor = method_factors.get(ind.survey_method, 1.0)
            noise = np.random.normal(0, 0.05)
            
            if ind.metric_type == "binary":
                p_flip = 0.10 * method_factor * (1 - reg_factor)
                reported_val = (1.0 - true_val) if np.random.random() < p_flip else true_val
            else:
                distortion = 1 + (ind.bias_direction * bias_mag * method_factor * reg_factor) + noise
                reported_val = max(0.0, true_val * distortion)
                if ind.metric_type == "percent": reported_val = min(100.0, reported_val)
                if ind.metric_type == "count": reported_val = round(reported_val)

            surveys.append(ESGSurvey(
                supplier_id=supplier.id, indicator_id=ind.id, reporting_period="2025",
                true_value=round(true_val, 2), reported_value=round(reported_val, 2),
                data_quality_flag="estimated" if ind.survey_method == "estimated" else "self_reported"
            ))
    return surveys

# --- 3. AUDITS & RISK SCORING ---

def generate_audits(suppliers: list[Supplier]) -> list[Audit]:
    """Generates sparse audit events (approx 10% base rate) [cite: 153-159]."""
    audits = []
    for s in suppliers:
        # Size and regulation drive audit probability [cite: 158-159]
        size_mult = {"Small": 0.5, "Medium": 1.0, "Large": 2.0, "Enterprise": 2.5}.get(s.size_tier, 1.0)
        reg_mult = {"low": 0.8, "med": 1.0, "high": 1.2}.get(s.regulatory_pressure, 1.0)
        
        if random.random() < (0.10 * size_mult * reg_mult):
            score = np.clip(40 + (50 * s.esg_maturity) + np.random.normal(0, 10), 0, 100)
            audits.append(Audit(
                supplier_id=s.id, audit_date="2025-Q4",
                audit_type=random.choice(["site", "document", "third_party"]),
                audit_score=round(score, 2),
                findings_count=np.random.poisson(max(0.5, 5 * (1 - s.esg_maturity)))
            ))
    return audits

def calculate_scores(suppliers: list[Supplier], surveys: list[ESGSurvey]) -> list[ESGScore]:
    """Calculates weighted ESG scores and risk tiers [cite: 201-210]."""
    scores = []
    for s in suppliers:
        s_surveys = [sv for sv in surveys if sv.supplier_id == s.id]
        
        # Calculate sub-scores [cite: 202-204]
        e_vals = [sv.reported_value for sv in s_surveys if sv.indicator_id in ["co2_emissions", "energy_consumption", "renewable_energy_pct"]]
        s_vals = [sv.reported_value for sv in s_surveys if sv.indicator_id in ["injury_rate", "labor_violations", "training_hours"]]
        g_vals = [sv.reported_value for sv in s_surveys if sv.indicator_id in ["anti_corruption_policy", "esg_reporting_framework"]]

        e_score = np.mean(e_vals) if e_vals else 50
        s_score = np.mean(s_vals) if s_vals else 50
        g_score = (sum(g_vals) / len(g_vals)) * 100 if g_vals else 50

        # Weighted overall score [cite: 206]
        overall = np.clip((0.4 * e_score) + (0.3 * s_score) + (0.3 * g_score), 0, 100)
        tier = "high" if overall < 40 else "med" if overall < 70 else "low"

        scores.append(ESGScore(
            supplier_id=s.id, reporting_period="2025",
            environment_score=round(e_score, 2), social_score=round(s_score, 2),
            governance_score=round(g_score, 2), overall_esg_score=round(overall, 2),
            risk_tier=tier
        ))
    return scores