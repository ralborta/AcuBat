# AcuBat Pricing Platform - Frontend

Frontend de la plataforma de pricing parametrizable construido con Next.js 14, TypeScript, Tailwind CSS y shadcn/ui.

## 🚀 Características

- **Next.js 14** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos
- **shadcn/ui** para componentes
- **Recharts** para gráficos
- **React Hook Form** para formularios
- **Zod** para validación

## 📁 Estructura

```
frontend/
├── app/                    # App Router de Next.js
│   ├── layout.tsx         # Layout principal
│   ├── page.tsx           # Página del dashboard
│   └── globals.css        # Estilos globales
├── components/            # Componentes reutilizables
│   ├── ui/               # Componentes base (shadcn/ui)
│   └── layout/           # Componentes de layout
├── lib/                  # Utilidades
├── hooks/                # Custom hooks
└── types/                # Tipos TypeScript
```

## 🛠️ Instalación

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
```bash
cp env.example .env.local
```

### 3. Ejecutar en desarrollo
```bash
npm run dev
```

### 4. Construir para producción
```bash
npm run build
npm start
```

## 🎨 Componentes

### Layout
- **Sidebar**: Navegación lateral con colapso
- **Header**: Barra superior con búsqueda y acciones
- **Dashboard**: Página principal con métricas y gráficos

### UI Components
- **Button**: Botones con variantes
- **Card**: Tarjetas para contenido
- **Input**: Campos de entrada
- **Progress**: Barras de progreso
- **Toast**: Notificaciones

## 📊 Dashboard

El dashboard incluye:

- **Métricas clave**: Total de productos, márgenes, tasa de éxito
- **Gráficos interactivos**: Productos por día, distribución de márgenes
- **Navegación**: Sidebar colapsible con todas las secciones
- **Responsive**: Diseño adaptativo para móviles

## 🔧 Desarrollo

### Scripts disponibles
- `npm run dev`: Servidor de desarrollo
- `npm run build`: Construcción para producción
- `npm run start`: Servidor de producción
- `npm run lint`: Linting con ESLint
- `npm run type-check`: Verificación de tipos

### Tecnologías principales
- **Next.js 14**: Framework React con App Router
- **TypeScript**: Tipado estático
- **Tailwind CSS**: Framework de CSS utility-first
- **shadcn/ui**: Componentes de UI modernos
- **Recharts**: Biblioteca de gráficos
- **Lucide React**: Iconos

## 🚀 Deploy

### Vercel (Recomendado)

1. Ir a [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Importar desde GitHub: `acubat-pricing-platform`
4. Configurar:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Variables de entorno

En Vercel Dashboard → Project Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_BASE_URL=https://TU_BACKEND_RAILWAY.railway.app/api/v1
NEXT_PUBLIC_API_KEY=TU_API_KEY_SECRET
```

### Deploy

```bash
# Vercel detectará cambios automáticamente
git push origin main
```

### Otros
- **Netlify**: Compatible con Next.js
- **Railway**: Deploy full-stack
- **Docker**: Contenedorización

## 📱 Responsive

El diseño es completamente responsive:
- **Desktop**: Layout completo con sidebar
- **Tablet**: Sidebar colapsible
- **Mobile**: Navegación optimizada

## 🎯 Próximos pasos

- [ ] Página de carga de archivos
- [ ] Simulaciones de pricing
- [ ] Gestión de rulesets
- [ ] Reportes y exportación
- [ ] Configuración del sistema
