from sqlalchemy import Column, String, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base
import enum
import uuid

class AssetStatus(str, enum.Enum):
    active = "active"
    stale = "stale"
    archived = "archived"

class AssetType(str, enum.Enum):
    domain = "domain"
    subdomain = "subdomain"
    ip_address = "ip_address"
    service = "service"
    certificate = "certificate"
    technology = "technology"

class Asset(Base):
    __tablename__ = "assets"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type       = Column(Enum(AssetType), nullable=False)
    value      = Column(String, nullable=False, index=True)
    status     = Column(Enum(AssetStatus), default=AssetStatus.active)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source     = Column(String, default="import")
    tags       = Column(JSON, default=list)
    metadata_  = Column("metadata", JSON, default=dict)

    relationships_out = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.source_id",
        back_populates="source"
    )
    relationships_in = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.target_id",
        back_populates="target"
    )

class AssetRelationship(Base):
    __tablename__ = "asset_relationships"

    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id        = Column(String, ForeignKey("assets.id"), nullable=False)
    target_id        = Column(String, ForeignKey("assets.id"), nullable=False)
    relationship_type = Column(String, nullable=False)

    source = relationship("Asset", foreign_keys=[source_id], back_populates="relationships_out")
    target = relationship("Asset", foreign_keys=[target_id], back_populates="relationships_in")