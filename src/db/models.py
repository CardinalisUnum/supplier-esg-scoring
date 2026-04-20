from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    esg_maturity: Mapped[float] = mapped_column(Float, nullable=False)
    efficiency: Mapped[float] = mapped_column(Float, nullable=False)

    true_metrics: Mapped["TrueESGMetrics"] = relationship(
        back_populates="supplier", uselist=False, cascade="all, delete-orphan"
    )
    reported_metrics: Mapped["ReportedESGMetrics"] = relationship(
        back_populates="supplier", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("esg_maturity >= 0.0 AND esg_maturity <= 1.0", name="ck_supplier_esg_maturity"),
        CheckConstraint("efficiency >= 0.1 AND efficiency <= 1.0", name="ck_supplier_efficiency"),
    )


class TrueESGMetrics(Base):
    __tablename__ = "true_esg_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), unique=True, nullable=False)
    true_emissions: Mapped[float] = mapped_column(Float, nullable=False)
    true_violations: Mapped[int] = mapped_column(Integer, nullable=False)
    true_injury_rate: Mapped[float] = mapped_column(Float, nullable=False)
    true_policy_exists: Mapped[bool] = mapped_column(Boolean, nullable=False)

    supplier: Mapped[Supplier] = relationship(back_populates="true_metrics")


class ReportedESGMetrics(Base):
    __tablename__ = "reported_esg_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), unique=True, nullable=False)
    reported_emissions: Mapped[float] = mapped_column(Float, nullable=False)
    reported_violations: Mapped[int] = mapped_column(Integer, nullable=False)
    reported_injury_rate: Mapped[float] = mapped_column(Float, nullable=False)
    reported_policy_exists: Mapped[bool] = mapped_column(Boolean, nullable=False)

    supplier: Mapped[Supplier] = relationship(back_populates="reported_metrics")
