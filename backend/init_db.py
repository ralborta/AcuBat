#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo para AcuBat
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import SessionLocal, engine
from app.db.models import Base, Tenant, Ruleset, User
from app.services.rules_engine import MOURA_RULESET
import uuid
import secrets

def init_database():
    """Inicializa la base de datos con datos de ejemplo"""
    print("🚀 Inicializando base de datos para AcuBat Pricing Platform...")
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")
    
    db = SessionLocal()
    try:
        # Verificar si ya existe el tenant AcuBat
        existing_tenant = db.query(Tenant).filter(Tenant.nombre == "AcuBat").first()
        if existing_tenant:
            print(f"✅ Tenant AcuBat ya existe: {existing_tenant.id}")
            acubat_tenant = existing_tenant
        else:
            # Crear tenant AcuBat
            acubat_tenant = Tenant(
                id=str(uuid.uuid4()), 
                nombre="AcuBat", 
                tenant_metadata={
                    "qa_gates": {
                        "global_threshold": 0.08,
                        "sku_threshold": 0.15,
                        "auto_publish": False
                    }
                }
            )
            db.add(acubat_tenant)
            db.commit()
            db.refresh(acubat_tenant)
            print(f"✅ Tenant AcuBat creado: {acubat_tenant.id}")

        # Verificar si ya existe el ruleset Moura
        existing_ruleset = db.query(Ruleset).filter(
            Ruleset.tenant_id == acubat_tenant.id,
            Ruleset.nombre == "moura_base"
        ).first()
        
        if existing_ruleset:
            print(f"✅ Ruleset Moura ya existe: {existing_ruleset.id}")
            moura_ruleset = existing_ruleset
        else:
            # Crear ruleset Moura
            moura_ruleset = Ruleset(
                id=str(uuid.uuid4()), 
                tenant_id=acubat_tenant.id, 
                nombre="moura_base",
                version="v1", 
                config=MOURA_RULESET, 
                is_active=True
            )
            db.add(moura_ruleset)
            db.commit()
            db.refresh(moura_ruleset)
            print(f"✅ Ruleset Moura creado: {moura_ruleset.id}")

        # Verificar si ya existe el usuario admin
        existing_user = db.query(User).filter(
            User.tenant_id == acubat_tenant.id,
            User.email == "admin@acubat.com"
        ).first()
        
        if existing_user:
            print(f"✅ Usuario admin ya existe: {existing_user.email}")
            admin_user = existing_user
        else:
            # Crear usuario admin
            admin_user = User(
                id=str(uuid.uuid4()), 
                tenant_id=acubat_tenant.id, 
                email="admin@acubat.com",
                rol="admin", 
                api_key=f"acubat_{secrets.token_urlsafe(32)}", 
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Usuario admin creado: {admin_user.email}")
            print(f"🔑 API Key: {admin_user.api_key}")

        print("\n🎉 Base de datos inicializada exitosamente!")
        print(f"📊 Tenant ID: {acubat_tenant.id}")
        print(f"⚙️  Ruleset ID: {moura_ruleset.id}")
        print(f"👤 Admin API Key: {admin_user.api_key}")
        
        return {
            "tenant_id": acubat_tenant.id,
            "ruleset_id": moura_ruleset.id,
            "api_key": admin_user.api_key
        }
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
