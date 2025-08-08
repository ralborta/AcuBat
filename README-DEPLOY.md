# 🚀 Guía de Deploy - AcuBat Pricing Platform

Guía completa para desplegar la plataforma de pricing de AcuBat en GitHub, Vercel y Railway.

## 📋 Prerrequisitos

- [Git](https://git-scm.com/) instalado
- [Docker](https://docker.com/) instalado
- Cuenta en [GitHub](https://github.com/)
- Cuenta en [Vercel](https://vercel.com/)
- Cuenta en [Railway](https://railway.app/)

## 🔄 1. GitHub Setup

### 1.1 Inicializar repositorio

```bash
# Clonar o inicializar el repositorio
git init
git add .
git commit -m "Initial commit: AcuBat Pricing Platform"

# Crear repositorio en GitHub y agregar origin
git remote add origin https://github.com/TU_USUARIO/acubat-pricing-platform.git
git branch -M main
git push -u origin main
```

### 1.2 Verificar CI/CD

Los workflows de GitHub Actions se ejecutarán automáticamente:
- **Backend CI**: `backend-ci.yml` - Tests Python y build Docker
- **Frontend CI**: `frontend-ci.yml` - Build Next.js

## 🎯 2. Vercel (Frontend)

### 2.1 Crear proyecto

1. Ir a [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Importar desde GitHub: `acubat-pricing-platform`
4. Configurar:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 2.2 Variables de entorno

En Vercel Dashboard → Project Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_BASE_URL=https://TU_BACKEND_RAILWAY.railway.app/api/v1
NEXT_PUBLIC_API_KEY=TU_API_KEY_SECRET
```

### 2.3 Deploy

```bash
# Vercel detectará cambios automáticamente
git push origin main
```

## 🚂 3. Railway (Backend + Database)

### 3.1 Crear proyecto

1. Ir a [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Seleccionar "Deploy from GitHub repo"
4. Elegir `acubat-pricing-platform`
5. Configurar:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 3.2 Provisionar PostgreSQL

1. En Railway Dashboard → "New"
2. Seleccionar "Database" → "PostgreSQL"
3. Copiar la `DATABASE_URL` generada

### 3.3 Variables de entorno

En Railway Dashboard → Variables:

```bash
DATABASE_URL=postgresql://... # Copiada del paso anterior
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=TU_ACCESS_KEY
S3_SECRET_KEY=TU_SECRET_KEY
S3_BUCKET=acubat-pricing
API_SECRET=TU_SECRET_FUERTE_PARA_PROD
CORS_ORIGINS=https://TU_DOMINIO_VERCEL.vercel.app
ENV=production
```

### 3.4 Migraciones y seed

En Railway Dashboard → Deployments → View Logs → Shell:

```bash
# Ejecutar migraciones
alembic upgrade head

# Inicializar datos
python init_db.py
```

### 3.5 Obtener URL del backend

Copiar la URL pública del backend (ej: `https://acubat-backend.railway.app`) y actualizarla en Vercel.

## 🐳 4. Desarrollo Local

### 4.1 Levantar servicios

```bash
# Levantar todos los servicios
docker compose -f docker-compose.dev.yml up -d

# Verificar que estén corriendo
docker compose -f docker-compose.dev.yml ps
```

### 4.2 Inicializar base de datos

```bash
cd backend
python init_db.py
```

### 4.3 Acceder a servicios

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Adminer (DB)**: http://localhost:8080

## 🧪 5. Smoke Tests

### 5.1 Health Check

```bash
curl -X GET "https://TU_BACKEND_RAILWAY.railway.app/health"
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 5.2 Upload Excel

```bash
curl -X POST "https://TU_BACKEND_RAILWAY.railway.app/api/v1/upload" \
  -H "x-api-key: TU_API_KEY" \
  -F "file=@backend/app/examples/moura_sample.xlsx" \
  -F "tenant_id=acubat-tenant-id"
```

**Respuesta esperada:**
```json
{
  "id": "list-uuid",
  "filename": "moura_sample.xlsx",
  "normalized_items_count": 3,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5.3 Simular Pricing

```bash
curl -X POST "https://TU_BACKEND_RAILWAY.railway.app/api/v1/simulate" \
  -H "x-api-key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "acubat-tenant-id",
    "list_id": "LIST_ID_FROM_UPLOAD",
    "ruleset_id": "RULESET_ID_FROM_INIT"
  }'
```

**Respuesta esperada:**
```json
{
  "run_id": "run-uuid",
  "status": "completed",
  "summary": {
    "total_items": 3,
    "cambio_promedio": 0.05,
    "skus_afectados": 2,
    "skus_bloqueados_por_gate": 0
  }
}
```

### 5.4 Obtener resultados

```bash
curl -X GET "https://TU_BACKEND_RAILWAY.railway.app/api/v1/runs/RUN_ID" \
  -H "x-api-key: TU_API_KEY"
```

**Respuesta esperada:**
```json
{
  "run_id": "run-uuid",
  "status": "completed",
  "summary": {
    "total_items": 3,
    "cambio_promedio": 0.05,
    "skus_afectados": 2,
    "skus_bloqueados_por_gate": 0,
    "margen_promedio": 0.15,
    "rentabilidad_promedio": 0.12
  },
  "price_items": [
    {
      "sku": "BAT001",
      "inputs": {"base_price": 1000, "cost": 800},
      "outputs": {"K": 7050, "P": 6697, "markup": -0.119, "rentabilidad": 0.05},
      "breakdown": {"desc1": 0.50, "desc_contado": 0.06, "IVA": 0.21}
    }
  ]
}
```

### 5.5 Publicar resultados

```bash
curl -X POST "https://TU_BACKEND_RAILWAY.railway.app/api/v1/publish" \
  -H "x-api-key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "acubat-tenant-id",
    "run_id": "RUN_ID",
    "channel": "minorista",
    "changelog": "Actualización de precios Q1 2024"
  }'
```

**Respuesta esperada:**
```json
{
  "publish_id": "publish-uuid",
  "export_url": "https://s3.example.com/export.csv",
  "channel": "minorista",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5.6 Descargar CSV

```bash
curl -X GET "https://TU_BACKEND_RAILWAY.railway.app/api/v1/export.csv?publish_id=PUBLISH_ID" \
  -H "x-api-key: TU_API_KEY" \
  --output pricing_export.csv
```

## 🔧 6. Configuración QA Gates

### 6.1 Variables por defecto

```bash
QA_GLOBAL_THRESHOLD=0.08    # 8% cambio promedio
QA_SKU_THRESHOLD=0.15       # 15% cambio por SKU
AUTO_PUBLISH=false          # Deshabilitado por defecto
```

### 6.2 Personalizar por tenant

En la tabla `tenants.metadata`:

```json
{
  "qa_gates": {
    "global_threshold": 0.10,
    "sku_threshold": 0.20,
    "auto_publish": true
  }
}
```

## 📊 7. Verificación Final

### 7.1 Flujo completo desde Frontend

1. **Acceder**: https://TU_DOMINIO_VERCEL.vercel.app
2. **Upload**: Subir `backend/app/examples/moura_sample.xlsx`
3. **Simular**: Ejecutar simulación con ruleset Moura
4. **Verificar**: K, P, Q (markup), R (rentabilidad), PVP
5. **Publicar**: Generar CSV y descargar

### 7.2 Validación de resultados

Los resultados deben coincidir con Excel original (±0.5% por redondeos):

- **Batería 60Ah**: K ≈ 7050, P ≈ 6697, markup ≈ -11.9%
- **Batería Pesada**: IVA reducido 10.5%, redondeo ceil50
- **Batería Moto**: Cálculos correctos con descuentos

## 🚨 8. Troubleshooting

### 8.1 Backend no responde

```bash
# Verificar logs en Railway
railway logs

# Verificar variables de entorno
railway variables
```

### 8.2 Frontend no conecta al backend

```bash
# Verificar CORS_ORIGINS en Railway
# Debe incluir el dominio de Vercel
```

### 8.3 Base de datos no migra

```bash
# Ejecutar manualmente en Railway Shell
alembic upgrade head
python init_db.py
```

### 8.4 S3 no funciona

```bash
# Verificar credenciales S3
# Crear bucket si no existe
# Verificar permisos IAM
```

## 📞 9. Soporte

- **Issues**: [GitHub Issues](https://github.com/TU_USUARIO/acubat-pricing-platform/issues)
- **Documentación**: [README.md](./README.md)
- **API Docs**: https://TU_BACKEND_RAILWAY.railway.app/docs

---

**¡La plataforma está lista para producción! 🎉**
