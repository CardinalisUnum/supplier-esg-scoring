from typing import List, Optional
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

# 1. Entity Backbone
class Supplier(Base):
    __tablename__ = "suppliers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    industry: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String) # e.g., NCR, CALABARZON
    operating_context: Mapped[str] = mapped_column(String) # urban, industrial, rural
    size_tier: Mapped[str] = mapped_column(String)
    scale_spend: Mapped[float] = mapped_column(Float)
    
    # Latent variables (Used for generation math, saved for your ML evaluation later)
    esg_maturity: Mapped[float] = mapped_column(Float)
    efficiency_factor: Mapped[float] = mapped_column(Float)
    grid_intensity: Mapped[str] = mapped_column(String)
    regulatory_pressure: Mapped[str] = mapped_column(String)

    # Relational Links
    surveys: Mapped[List["ESGSurvey"]] = relationship(back_populates="supplier")
    audits: Mapped[List["Audit"]] = relationship(back_populates="supplier")
    estimates: Mapped[List["EmissionsEstimate"]] = relationship(back_populates="supplier")
    scores: Mapped[List["ESGScore"]] = relationship(back_populates="supplier")

# 2. Indicator Controls
class IndicatorDefinition(Base):
    __tablename__ = "indicator_definitions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True) # e.g., 'co2_emissions'
    category: Mapped[str] = mapped_column(String) # E, S, G
    subcategory: Mapped[str] = mapped_column(String)
    metric_type: Mapped[str] = mapped_column(String) # continuous, count, binary, percent
    unit: Mapped[str] = mapped_column(String)
    bias_direction: Mapped[int] = mapped_column(Integer) # +1 (overreport) or -1 (underreport)
    survey_method: Mapped[str] = mapped_column(String)

    surveys: Mapped[List["ESGSurvey"]] = relationship(back_populates="indicator")

# 3. The Core Survey Data (Replaces your true/reported split tables)
class ESGSurvey(Base):
    __tablename__ = "esg_surveys"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    indicator_id: Mapped[str] = mapped_column(ForeignKey("indicator_definitions.id"))
    reporting_period: Mapped[str] = mapped_column(String)
    
    true_value: Mapped[float] = mapped_column(Float)
    reported_value: Mapped[float] = mapped_column(Float)
    data_quality_flag: Mapped[str] = mapped_column(String)

    supplier: Mapped["Supplier"] = relationship(back_populates="surveys")
    indicator: Mapped["IndicatorDefinition"] = relationship(back_populates="surveys")

# 4. Sparse Audit Data
class Audit(Base):
    __tablename__ = "audits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    audit_date: Mapped[str] = mapped_column(String)
    audit_type: Mapped[str] = mapped_column(String)
    audit_score: Mapped[float] = mapped_column(Float)
    findings_count: Mapped[int] = mapped_column(Integer)

    supplier: Mapped["Supplier"] = relationship(back_populates="audits")

# 5. Modeled Estimates
class EmissionsEstimate(Base):
    __tablename__ = "emissions_estimates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    reporting_period: Mapped[str] = mapped_column(String)
    estimated_emissions: Mapped[float] = mapped_column(Float)
    estimation_method: Mapped[str] = mapped_column(String)
    confidence_score: Mapped[float] = mapped_column(Float)

    supplier: Mapped["Supplier"] = relationship(back_populates="estimates")

# 6. Final Outputs
class ESGScore(Base):
    __tablename__ = "esg_scores"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    reporting_period: Mapped[str] = mapped_column(String)
    environment_score: Mapped[float] = mapped_column(Float)
    social_score: Mapped[float] = mapped_column(Float)
    governance_score: Mapped[float] = mapped_column(Float)
    overall_esg_score: Mapped[float] = mapped_column(Float)
    risk_tier: Mapped[str] = mapped_column(String) # low, med, high

    supplier: Mapped["Supplier"] = relationship(back_populates="scores")
    