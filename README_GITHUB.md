# 🚀 Backend Acubat - Sistema de Gestión de Productos

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy on Vercel](https://img.shields.io/badge/Deploy%20on-Vercel-black.svg)](https://vercel.com)

Sistema backend profesional para procesamiento de archivos Excel con lógica de negocio, visualización moderna y alertas inteligentes con IA.

## 🌟 Características

- ✅ **Carga y procesamiento de archivos Excel** con normalización automática
- ✅ **Lógica de negocio completa** (markup, redondeo, validaciones)
- ✅ **Panel web moderno** con Bootstrap y diseño responsive
- ✅ **Sistema de alertas inteligente** con colores e iconos
- ✅ **Integración con OpenAI** para validaciones y sugerencias
- ✅ **API REST completa** con documentación automática
- ✅ **Filtros avanzados** por canal, marca y estado
- ✅ **Despliegue en Vercel** listo para producción

## 🚀 Despliegue Rápido

### Opción 1: Vercel (Recomendado)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/tu-usuario/acubat-backend)

1. Haz clic en el botón "Deploy with Vercel"
2. Conecta tu cuenta de GitHub
3. Configura las variables de entorno (opcional)
4. ¡Listo! Tu aplicación estará disponible en `https://tu-app.vercel.app`

### Opción 2: Despliegue Manual

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/acubat-backend.git
cd acubat-backend

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn api.main:app --reload
```

## 🛠️ Instalación Local

### Prerrequisitos

- Python 3.11+
- pip

### Pasos de Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/acubat-backend.git
cd acubat-backend

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (opcional)
cp env.example .env
# Editar .env con tus configuraciones

# 5. Ejecutar servidor
uvicorn api.main:app --reload
```

### Acceso al Sistema

- **Panel Web**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alertas**: http://localhost:8000/alertas

## 📊 Funcionalidades

### Procesamiento de Excel
- Lectura automática de archivos .xlsx y .xls
- Normalización de columnas (código, nombre, capacidad, marca, canal, precios)
- Detección automática de marca por código (MO=Moura, ZX=Solar, LB=Lubeck)
- Validación y limpieza de datos

### Lógica de Negocio
- **Markup por canal**:
  - Minorista: 35% + redondeo a múltiplos de $100
  - Mayorista: 25%
  - Distribuidor: 15%
- **Validaciones automáticas**:
  - Márgenes mínimos por canal
  - Rangos de precios por marca
  - Productos sin código
  - Precios liberados

### Sistema de Alertas
- 🟡 **Margen Bajo**: Por debajo del mínimo esperado
- ⚫ **Sin Código**: Producto sin código identificado
- 🔵 **Precio Liberado**: Sin markup aplicado
- 🔴 **Sin Markup**: Margen de 0%
- 🟠 **Precio Fuera de Rango**: Fuera del rango esperado

### Funciones de IA (OpenAI)
- Análisis automático de productos con alertas
- Detección de anomalías en datos
- Sugerencias de markup óptimo
- Clasificación automática de productos

## 📡 API Endpoints

### Principales
- `GET /` - Panel web principal
- `GET /alertas` - Página de alertas
- `GET /api/productos` - Lista todos los productos
- `GET /api/alertas` - Solo productos con alertas
- `POST /upload` - Subir archivo Excel
- `POST /api/analizar-ai` - Análisis con IA
- `GET /api/resumen` - Estadísticas generales

### Filtros
```bash
# Filtrar por canal
GET /api/productos?canal=minorista

# Filtrar por marca
GET /api/productos?marca=moura

# Solo productos con alertas
GET /api/productos?con_alertas=true
```

## 🔧 Configuración

### Variables de Entorno

```bash
# .env
OPENAI_API_KEY=tu_clave_de_openai_aqui
DEBUG=True
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Personalización

Edita `api/logic.py` para modificar:
- Porcentajes de markup por canal
- Márgenes mínimos aceptables
- Rangos de precios por marca

## 📁 Estructura del Proyecto

```
acubat-backend/
├── api/
│   ├── main.py         # Backend FastAPI (endpoints)
│   ├── logic.py        # Reglas de negocio
│   ├── parser.py       # Lectura de Excel
│   ├── openai_helper.py # Funciones de IA
│   └── models.py       # Modelos de datos
├── templates/          # HTML con Bootstrap
│   ├── index.html      # Panel principal
│   └── alertas.html    # Página de alertas
├── data/               # Archivos fuente
├── static/             # CSS y JS
├── requirements.txt    # Dependencias
├── vercel.json         # Configuración Vercel
└── README.md          # Documentación
```

## 🚀 Despliegue en Vercel

### Configuración Automática
El proyecto incluye `vercel.json` para despliegue automático en Vercel.

### Variables de Entorno en Vercel
1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Agrega:
   - `OPENAI_API_KEY`: Tu clave de OpenAI (opcional)

### Comandos de Despliegue
```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel

# Desplegar a producción
vercel --prod
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- 📧 Email: tu-email@ejemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/acubat-backend/issues)
- 📚 Documentación: [API Docs](https://tu-app.vercel.app/docs)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [OpenAI](https://openai.com/) - API de IA
- [Vercel](https://vercel.com/) - Plataforma de despliegue

---

**¡Disfruta usando el Backend Acubat! 🚀**

[![Star on GitHub](https://img.shields.io/github/stars/tu-usuario/acubat-backend?style=social)](https://github.com/tu-usuario/acubat-backend)
[![Fork on GitHub](https://img.shields.io/github/forks/tu-usuario/acubat-backend?style=social)](https://github.com/tu-usuario/acubat-backend) 