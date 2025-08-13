# 🚀 AcuBat Demo - Modo SQLite

## **¿Qué es esto?**

Esta es una **versión de demo** de AcuBat que funciona **SIN base de datos PostgreSQL**. Usa **SQLite en memoria** con **datos de ejemplo pre-cargados**.

## **¿Por qué SQLite?**

- ✅ **Sin problemas de Railway** - No depende de PostgreSQL
- ✅ **Demo inmediata** - Funciona en 5 minutos
- ✅ **Datos realistas** - Productos, tenants y rulesets de ejemplo
- ✅ **Todas las funcionalidades** - Upload, simulación, análisis

## **🚀 Cómo Usar la Demo**

### **1. Variables de Entorno**

```bash
# Copiar configuración de demo
cp env.demo .env

# O configurar manualmente:
DEMO_MODE=true
DATABASE_URL=sqlite:///:memory:
```

### **2. Ejecutar la App**

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Datos de Demo Disponibles**

#### **Tenant:**
- **ID**: `demo-tenant-001`
- **Nombre**: Demo Company

#### **Productos:**
- **BAT-001**: Moura Automotriz 60Ah AGM
- **BAT-002**: Moura Automotriz 70Ah AGM  
- **BAT-003**: Varta Industrial 100Ah Gel

#### **Ruleset:**
- **ID**: `demo-ruleset-001`
- **Nombre**: Reglas Demo 2024
- **Markups**: Base 25%, Automotriz 30%, Industrial 35%

#### **Lista de Precios:**
- **ID**: `demo-list-001`
- **Archivo**: lista_precios_demo.xlsx

## **🔗 Endpoints de Demo**

### **Información General:**
- `GET /` - Estado de la app + modo demo
- `GET /health` - Health check + tipo de DB
- `GET /demo/data` - **Datos de demo disponibles**

### **API Completa:**
- `POST /api/v1/upload` - Subir archivos Excel
- `POST /api/v1/simulate` - Ejecutar simulación
- `GET /api/v1/runs/{id}` - Ver resultados
- `POST /api/v1/publish` - Publicar resultados

## **📊 Ejemplo de Simulación**

```bash
curl -X POST "http://localhost:8000/api/v1/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "demo-tenant-001",
    "list_id": "demo-list-001", 
    "ruleset_id": "demo-ruleset-001"
  }'
```

## **🔄 Volver a PostgreSQL**

Para volver a PostgreSQL después de la demo:

1. **Comentar** la línea `DEMO_MODE=true` en `.env`
2. **Configurar** variables de Railway PostgreSQL
3. **Reiniciar** la aplicación

## **⚠️ Limitaciones del Modo Demo**

- **Datos en memoria** - Se pierden al reiniciar
- **Sin persistencia** - No hay historial entre sesiones
- **Sin autenticación** - Acceso directo a todas las funciones
- **Almacenamiento local** - Archivos se guardan temporalmente

## **🎯 Perfecto Para:**

- ✅ **Demos a clientes** - Funcionalidad completa
- ✅ **Presentaciones** - Sin problemas técnicos
- ✅ **Testing rápido** - Desarrollo y debugging
- ✅ **Evitar problemas Railway** - Solución temporal

## **🚨 Solución de Problemas**

### **Error de Base de Datos:**
```bash
# Verificar que esté en modo demo
echo $DEMO_MODE
# Debe ser: true
```

### **App No Inicia:**
```bash
# Verificar configuración
cat .env | grep DEMO_MODE
cat .env | grep DATABASE_URL
```

### **Datos No Aparecen:**
```bash
# Verificar endpoint de demo
curl http://localhost:8000/demo/data
```

---

**¡Tu demo está lista! 🎉**
