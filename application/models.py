from sqlalchemy import Boolean, Column, func, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from application.database import Base


class Experiment(Base):
    __tablename__ = "experiment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True, server_default="t")
    variants = relationship(
        "Variant",
        backref="experiment_variant.experiment_id",
        primaryjoin="Experiment.id == Variant.experiment_id",
        lazy="dynamic",
        order_by="desc(Variant.ratio)",
    )
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Variant(Base):
    __tablename__ = "experiment_variant"
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey(Experiment.id))
    name = Column(String)
    ratio = Column(Integer, default=50)
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class VariantViews(Base):
    __tablename__ = "variant_view"
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey(Variant.id))
    device_id = Column(String, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
