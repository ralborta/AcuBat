# 📖 Guía de Uso - Backend Acubat

## 🚀 Inicio Rápido

### 1. Instalación
```bash
# Ejecutar script de instalación
./install.sh

# O manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ejecutar el Servidor
```bash
# Opción 1: Usar script de inicio
./run.py

# Opción 2: Usar uvicorn directamente
uvicorn api.main:app --reload

# Opción 3: Con entorno virtual
source venv/bin/activate
uvicorn api.main:app --reload
```

### 3. Acceder al Sistema
- **Panel Web**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Página de Alertas**: http://localhost:8000/alertas

## 📊 Funcionalidades Principales

### Carga de Archivos Excel
1. Ve al panel principal
2. Arrastra un archivo Excel o haz clic en "Seleccionar Archivo"
3. El sistema procesará automáticamente el archivo
4. Verás los productos en la tabla con alertas identificadas

### Estructura del Excel
El sistema espera columnas con estos nombres (o similares):
- `codigo` o `código`: Código del producto
- `nombre` o `descripción`: Nombre/descripción del producto
- `capacidad`: Capacidad en Ah
- `marca`: Marca del producto
- `canal`: Canal de venta (minorista, mayorista, distribuidor)
- `precio_base`: Precio base/costo
- `precio_final`: Precio final de venta

### Filtros Disponibles
- **Canal**: Minorista, Mayorista, Distribuidor
- **Marca**: Moura, Acubat, Lubeck, Solar
- **Estado**: Con alertas, Sin alertas
- **Búsqueda**: Por código o nombre

## 🚨 Sistema de Alertas

### Tipos de Alertas
1. **Margen Bajo** (🟡): Margen por debajo del mínimo esperado
2. **Sin Código** (⚫): Producto sin código identificado
3. **Precio Liberado** (🔵): Precio sin markup aplicado
4. **Sin Markup** (🔴): Margen de 0%
5. **Precio Fuera de Rango** (🟠): Precio fuera del rango esperado para la marca

### Lógica de Negocio
- **Minorista**: 35% markup + redondeo a múltiplos de $100
- **Mayorista**: 25% markup
- **Distribuidor**: 15% markup

## 🤖 Funciones de IA (OpenAI)

### Configuración
1. Crea un archivo `.env` basado en `env.example`
2. Agrega tu clave de OpenAI: `OPENAI_API_KEY=tu_clave_aqui`

### Funciones Disponibles
- **Análisis de Productos**: Sugerencias automáticas para productos con alertas
- **Detección de Anomalías**: Identificación de problemas en los datos
- **Sugerencias de Markup**: Recomendaciones de precios óptimos
- **Clasificación Automática**: Identificación automática de marca y canal

## 📡 API Endpoints

### Principales
- `GET /api/productos` - Lista todos los productos
- `GET /api/alertas` - Solo productos con alertas
- `POST /upload` - Subir archivo Excel
- `POST /api/analizar-ai` - Análisis con IA
- `GET /api/resumen` - Estadísticas generales

### Filtros en API
```bash
# Filtrar por canal
GET /api/productos?canal=minorista

# Filtrar por marca
GET /api/productos?marca=moura

# Solo productos con alertas
GET /api/productos?con_alertas=true
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# .env
OPENAI_API_KEY=tu_clave_aqui
DEBUG=True
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Personalización de Markup
Edita `api/logic.py` para modificar:
- Porcentajes de markup por canal
- Márgenes mínimos aceptables
- Rangos de precios por marca

## 🛠️ Solución de Problemas

### Error: "No module named 'pydantic'"
```bash
# Activar entorno virtual e instalar dependencias
source venv/bin/activate
pip install -r requirements.txt
```

### Error al subir archivo Excel
- Verifica que el archivo sea .xlsx o .xls
- Asegúrate de que tenga las columnas requeridas
- Revisa los logs del servidor

### OpenAI no funciona
- Verifica que tengas una clave válida en .env
- El sistema funciona sin OpenAI (funciones básicas)

### Puerto ocupado
```bash
# Cambiar puerto
uvicorn api.main:app --port 8001
```

## 📈 Próximas Funcionalidades

- [ ] Integración con Make.com
- [ ] Notificaciones por WhatsApp/Email
- [ ] Exportación a PDF/Excel
- [ ] Dashboard con métricas avanzadas
- [ ] Sistema de usuarios y permisos
- [ ] Base de datos persistente

## 🆘 Soporte

Para problemas o sugerencias:
1. Revisa los logs del servidor
2. Verifica la documentación de la API en `/docs`
3. Consulta este archivo de guía

---

**¡Disfruta usando el Backend Acubat! 🚀** 