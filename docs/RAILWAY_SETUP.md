# 🚂 Railway Setup - AcuBat Pricing Platform

Guía completa para desplegar el backend de AcuBat Pricing Platform en Railway.

## 📋 Prerrequisitos

- Cuenta en [Railway](https://railway.app/)
- Repositorio GitHub configurado
- Variables de entorno preparadas

## 🔄 1. Crear Proyecto Railway

### 1.1 Acceder a Railway

1. Ir a [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Seleccionar "Deploy from GitHub repo"

### 1.2 Conectar Repositorio

1. Buscar y seleccionar `acubat-pricing-platform`
2. Configurar:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## 🗄️ 2. Provisionar PostgreSQL

### 2.1 Crear Base de Datos

1. En Railway Dashboard → "New"
2. Seleccionar "Database" → "PostgreSQL"
3. Esperar a que se provisione
4. **Copiar la `DATABASE_URL` generada**

### 2.2 Configurar Variables

En Railway Dashboard → Variables, agregar:

```bash
DATABASE_URL=postgresql://... # Copiada del paso anterior
```

## 🔧 3. Configurar Variables de Entorno

### 3.1 Variables Requeridas

En Railway Dashboard → Variables, agregar todas estas:

```bash
# Base de datos (ya configurada)
DATABASE_URL=postgresql://...

# S3 Storage
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=TU_ACCESS_KEY_AWS
S3_SECRET_KEY=TU_SECRET_KEY_AWS
S3_BUCKET=acubat-pricing
S3_SECURE=true

# Seguridad
API_SECRET=TU_SECRET_FUERTE_PARA_PROD
SECRET_KEY=TU_SECRET_KEY_FUERTE

# CORS
CORS_ORIGINS=https://TU_DOMINIO_VERCEL.vercel.app

# Entorno
ENV=production
DEBUG=false

# QA Gates
QA_GLOBAL_THRESHOLD=0.08
QA_SKU_THRESHOLD=0.15
AUTO_PUBLISH=false
```

### 3.2 Configuración S3

#### Opción A: AWS S3
```bash
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
S3_BUCKET=acubat-pricing
S3_SECURE=true
```

#### Opción B: Cloudflare R2
```bash
S3_ENDPOINT=https://TU_ACCOUNT_ID.r2.cloudflarestorage.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=acubat-pricing
S3_SECURE=true
```

#### Opción C: MinIO (para desarrollo)
```bash
S3_ENDPOINT=minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=acubat-pricing
S3_SECURE=false
```

## 🚀 4. Deploy y Migraciones

### 4.1 Primer Deploy

1. Railway detectará automáticamente el repositorio
2. Se ejecutará el build con `pip install -r requirements.txt`
3. Se iniciará el servidor con `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 4.2 Ejecutar Migraciones

En Railway Dashboard → Deployments → View Logs → Shell:

```bash
# Ejecutar migraciones de Alembic
alembic upgrade head

# Inicializar datos de ejemplo
python init_db.py
```

### 4.3 Verificar Deploy

```bash
# Verificar que el servidor esté corriendo
curl https://TU_BACKEND_RAILWAY.railway.app/health

# Verificar API docs
curl https://TU_BACKEND_RAILWAY.railway.app/docs
```

## 🔗 5. Configurar Frontend (Vercel)

### 5.1 Obtener URL del Backend

1. En Railway Dashboard → Settings
2. Copiar la URL pública (ej: `https://acubat-backend.railway.app`)

### 5.2 Actualizar Vercel

En Vercel Dashboard → Project Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_BASE_URL=https://TU_BACKEND_RAILWAY.railway.app/api/v1
NEXT_PUBLIC_API_KEY=TU_API_KEY_SECRET
```

## 🧪 6. Smoke Tests

### 6.1 Health Check

```bash
curl -X GET "https://TU_BACKEND_RAILWAY.railway.app/health" \
  -H "x-api-key: TU_API_KEY"
```

### 6.2 API Documentation

```bash
# Swagger UI
open https://TU_BACKEND_RAILWAY.railway.app/docs

# ReDoc
open https://TU_BACKEND_RAILWAY.railway.app/redoc
```

### 6.3 Test Upload

```bash
curl -X POST "https://TU_BACKEND_RAILWAY.railway.app/api/v1/upload" \
  -H "x-api-key: TU_API_KEY" \
  -F "file=@backend/app/examples/moura_sample.xlsx" \
  -F "tenant_id=acubat-tenant-id"
```

## 🔍 7. Monitoreo

### 7.1 Logs

En Railway Dashboard → Deployments → View Logs:

```bash
# Ver logs en tiempo real
railway logs

# Ver logs de un deployment específico
railway logs --deployment <deployment-id>
```

### 7.2 Métricas

- **CPU Usage**: Monitorear uso de CPU
- **Memory Usage**: Monitorear uso de memoria
- **Response Time**: Tiempo de respuesta de la API
- **Error Rate**: Tasa de errores

### 7.3 Alertas

Configurar alertas para:
- CPU > 80%
- Memory > 80%
- Error rate > 5%
- Response time > 2s

## 🚨 8. Troubleshooting

### 8.1 Deploy Falla

```bash
# Verificar logs
railway logs

# Verificar variables de entorno
railway variables

# Rebuild manual
railway up
```

### 8.2 Base de Datos No Conecta

```bash
# Verificar DATABASE_URL
echo $DATABASE_URL

# Probar conexión
railway run python -c "
from app.db.base import engine
print(engine.execute('SELECT 1').scalar())
"
```

### 8.3 S3 No Funciona

```bash
# Verificar credenciales
railway run python -c "
from app.services.storage import storage_service
print(storage_service.client.list_buckets())
"
```

### 8.4 CORS Errors

```bash
# Verificar CORS_ORIGINS
echo $CORS_ORIGINS

# Agregar dominio de Vercel
railway variables set CORS_ORIGINS="https://TU_DOMINIO_VERCEL.vercel.app"
```

## 🔄 9. Actualizaciones

### 9.1 Deploy Automático

Railway detecta automáticamente cambios en GitHub:
- Push a `main` → Deploy automático
- Pull Request → Preview deployment

### 9.2 Deploy Manual

```bash
# Forzar deploy
railway up

# Deploy específico
railway up --service backend
```

### 9.3 Rollback

En Railway Dashboard → Deployments:
1. Seleccionar deployment anterior
2. Click "Promote to Production"

## 💰 10. Costos

### 10.1 Estimación Mensual

- **PostgreSQL**: $5-20/mes (dependiendo del uso)
- **Backend**: $5-15/mes (dependiendo del tráfico)
- **Total**: $10-35/mes

### 10.2 Optimización

- **Auto-sleep**: Activar para desarrollo
- **Resource limits**: Configurar límites de CPU/memoria
- **Database optimization**: Índices y queries optimizadas

## 📞 11. Soporte

- **Railway Docs**: [docs.railway.app](https://docs.railway.app/)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **GitHub Issues**: [Issues del proyecto](https://github.com/TU_USUARIO/acubat-pricing-platform/issues)

---

**¡El backend está listo para producción en Railway! 🎉**
