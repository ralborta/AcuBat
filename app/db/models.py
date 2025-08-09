from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    nombre = Column(String(100), nullable=False)
    tenant_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    products = relationship("Product", back_populates="tenant")
    lists_raw = relationship("ListRaw", back_populates="tenant")
    rulesets = relationship("Ruleset", back_populates="tenant")
    users = relationship("User", back_populates="tenant")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    sku = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    linea = Column(String(50), nullable=False)
    atributos = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    tenant = relationship("Tenant", back_populates="products")
    
    # Índices
    __table_args__ = (
        Index('idx_product_tenant_sku', 'tenant_id', 'sku'),
        Index('idx_product_marca', 'tenant_id', 'marca'),
    )

class ListRaw(Base):
    __tablename__ = "lists_raw"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    storage_url = Column(String(500), nullable=False)
    list_metadata = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    tenant = relationship("Tenant", back_populates="lists_raw")
    normalized_items = relationship("NormalizedItem", back_populates="list_raw")
    price_runs = relationship("PriceRun", back_populates="list_raw")

class NormalizedItem(Base):
    __tablename__ = "normalized_items"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    list_id = Column(String, ForeignKey("lists_raw.id"), nullable=False)
    sku = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    linea = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    attrs = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    list_raw = relationship("ListRaw", back_populates="normalized_items")
    
    # Índices
    __table_args__ = (
        Index('idx_normalized_list_sku', 'list_id', 'sku'),
    )

class Ruleset(Base):
    __tablename__ = "rulesets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    tenant = relationship("Tenant", back_populates="rulesets")
    price_runs = relationship("PriceRun", back_populates="ruleset")
    
    # Índices
    __table_args__ = (
        Index('idx_ruleset_tenant_version', 'tenant_id', 'version'),
    )

class PriceRun(Base):
    __tablename__ = "price_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    list_id = Column(String, ForeignKey("lists_raw.id"), nullable=False)
    ruleset_id = Column(String, ForeignKey("rulesets.id"), nullable=False)
    resumen = Column(JSON, default={})
    status = Column(String(20), default="running")  # running, completed, failed
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relaciones
    list_raw = relationship("ListRaw", back_populates="price_runs")
    ruleset = relationship("Ruleset", back_populates="price_runs")
    price_items = relationship("PriceItem", back_populates="price_run")
    publishes = relationship("Publish", back_populates="price_run")

class PriceItem(Base):
    __tablename__ = "price_items"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("price_runs.id"), nullable=False)
    sku = Column(String(50), nullable=False)
    inputs = Column(JSON, default={})
    outputs = Column(JSON, default={})
    breakdown = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    price_run = relationship("PriceRun", back_populates="price_items")
    
    # Índices
    __table_args__ = (
        Index('idx_priceitem_run_sku', 'run_id', 'sku'),
    )

class Publish(Base):
    __tablename__ = "publishes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("price_runs.id"), nullable=False)
    canal = Column(String(50), nullable=False)
    export_url = Column(String(500), nullable=False)
    changelog = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    price_run = relationship("PriceRun", back_populates="publishes")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    rol = Column(String(20), default="viewer")  # admin, manager, viewer
    api_key = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    tenant = relationship("Tenant", back_populates="users")
    
    # Índices
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_api_key', 'api_key'),
    )
