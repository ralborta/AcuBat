# AcuBat Pricing Platform

Plataforma de pricing parametrizable y multi-producto que reemplaza múltiples hojas de Excel por un motor de reglas configurable.

## 🏗️ Arquitectura

```
acubat-pricing-platform/
├── frontend/          # Next.js + TypeScript + Tailwind + shadcn/ui
├── backend/           # FastAPI + SQLAlchemy + PostgreSQL
├── docker-compose.dev.yml
└── README.md
```

## 🚀 Características

- **Multi-tenant** desde el día 1
- **Motor de reglas genérico** y configurable
- **Carga y parseo** de múltiples hojas de Excel
- **Simulaciones** en tiempo real
- **Control de versiones** de rulesets
- **Dashboard** con KPIs y métricas
- **Publicación** y exportación de resultados

## 🛠️ Tecnologías

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Hook Form
- Zod

### Backend
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Pydantic
- Pandas + OpenPyXL
- MinIO (S3)

## 🏃‍♂️ Quick Start

### 1. Clonar repositorio
```bash
git clone <repo-url>
cd acubat-pricing-platform
```

### 2. Configurar variables de entorno
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 3. Levantar con Docker
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 4. Acceder a la aplicación
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Adminer (DB):** http://localhost:8080

## 📁 Estructura del Proyecto

### Frontend (`/frontend`)
```
frontend/
├── app/                 # App Router
├── components/          # Componentes reutilizables
├── lib/                 # Utilidades y configuraciones
├── types/               # Tipos TypeScript
└── public/              # Assets estáticos
```

### Backend (`/backend`)
```
backend/
├── app/
│   ├── api/            # Endpoints de la API
│   ├── core/           # Configuración y utilidades
│   ├── db/             # Modelos y migraciones
│   ├── services/       # Lógica de negocio
│   └── schemas/        # Esquemas Pydantic
├── tests/              # Tests unitarios
└── alembic/            # Migraciones de base de datos
```

## 🎯 Primer Tenant: AcuBat

La plataforma está configurada inicialmente para AcuBat con:

- **Ruleset:** `moura_base_v1`
- **Productos:** Baterías Moura
- **Canales:** Minorista y Mayorista
- **Parámetros:** IVA, descuentos, comisiones, IIBB

## 🔧 Desarrollo

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## 🚀 Deploy

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Railway)
```bash
cd backend
railway up
```

## 📊 Dashboard

El dashboard incluye:

- **Métricas clave:** Total de productos, márgenes promedio, tasa de éxito
- **Gráficos:** Productos por marca, distribución de márgenes
- **Simulaciones:** Historial de runs y resultados
- **Publicaciones:** Estado de exportaciones

## 🔐 Seguridad

- **API Keys** por tenant
- **RBAC:** Admin, Manager, Viewer
- **Aislamiento** completo entre tenants
- **Validación** de datos con Pydantic

## 📈 Roadmap

- [ ] Soporte para más marcas (Varta, Willard)
- [ ] Integración con ERPs
- [ ] Notificaciones en tiempo real
- [ ] API pública para partners
- [ ] Machine Learning para optimización de precios

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.
