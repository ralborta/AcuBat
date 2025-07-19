# 🚀 ACUBAT - Fase 2: Sistema de Pricing por Canal

## 📋 Resumen de la Fase 2

La Fase 2 implementa un sistema completo de **pricing inteligente por canal** con análisis de OpenAI, que incluye:

- ✅ **Cálculo automático de precios** por canal y marca
- ✅ **Aplicación de markup** configurable
- ✅ **Redondeo inteligente** (múltiplos de $100 para minorista)
- ✅ **Cálculo de márgenes** y validación de rangos
- ✅ **Alertas automáticas** para precios problemáticos
- ✅ **Análisis con OpenAI** para sugerencias inteligentes
- ✅ **Exportación a CSV** con todos los datos procesados
- ✅ **Interfaz web mejorada** con filtros y resúmenes

## 🏗️ Arquitectura del Sistema

### Archivos Principales

```
api/
├── logic.py          # Lógica de pricing y márgenes
├── openai_helper.py  # Integración con OpenAI
├── parser.py         # Procesamiento de archivos Excel/CSV
├── models.py         # Modelos de datos actualizados
└── main.py          # API endpoints actualizados

templates/
└── index.html       # Interfaz web mejorada

ejemplo_pricing.xlsx  # Archivo de ejemplo para pruebas
test_fase2.py        # Script de pruebas
```

## 🎯 Funcionalidades Implementadas

### 1. Sistema de Pricing Inteligente

#### Configuración de Markup por Canal y Marca

```python
markup_config = {
    (Canal.MINORISTA, Marca.MOURA): 0.35,      # 35%
    (Canal.MINORISTA, Marca.ACUBAT): 0.45,     # 45%
    (Canal.MINORISTA, Marca.LUBECK): 0.40,     # 40%
    (Canal.MINORISTA, Marca.SOLAR): 0.38,      # 38%
    
    (Canal.MAYORISTA, Marca.MOURA): 0.20,      # 20%
    (Canal.MAYORISTA, Marca.ACUBAT): 0.25,     # 25%
    (Canal.MAYORISTA, Marca.LUBECK): 0.22,     # 22%
    (Canal.MAYORISTA, Marca.SOLAR): 0.20,      # 20%
    
    (Canal.DISTRIBUIDOR, Marca.MOURA): 0.15,   # 15%
    (Canal.DISTRIBUIDOR, Marca.ACUBAT): 0.18,  # 18%
    (Canal.DISTRIBUIDOR, Marca.LUBECK): 0.16,  # 16%
    (Canal.DISTRIBUIDOR, Marca.SOLAR): 0.15,   # 15%
}
```

#### Proceso de Cálculo

1. **Precio con Markup**: `precio_final = precio_base * (1 + markup%)`
2. **Redondeo**: Múltiplos de $100 para minorista, 2 decimales para otros
3. **Margen**: `margen = (precio_final - precio_base) / precio_base * 100`

### 2. Sistema de Alertas

#### Tipos de Alertas

- 🔴 **Margen Bajo**: < 10%
- 🟡 **Sobreprecio**: > 80%
- ⚠️ **Sin Código**: Producto sin código identificable
- 🔓 **Precio Liberado**: Sin markup aplicado
- ❌ **Sin Markup**: Error en el cálculo

### 3. Integración con OpenAI

#### Análisis Individual de Productos

```python
# Análisis automático para productos con alertas o márgenes extremos
if producto.alertas or producto.margen < 10 or producto.margen > 80:
    sugerencia = openai_helper.analizar_producto(producto)
```

#### Resumen Ejecutivo

Genera análisis completo con:
- Estadísticas generales
- Alertas por tipo
- Resumen por marca y canal
- Recomendaciones estratégicas

### 4. Interfaz Web Mejorada

#### Nuevas Características

- 📊 **Resúmenes por Marca y Canal**
- 🔍 **Filtros avanzados** (canal, marca, alertas)
- 📈 **Indicadores visuales** de márgenes
- 🤖 **Botones de IA** para sugerencias
- 📄 **Exportación a CSV**
- 🎨 **Diseño responsive** y moderno

## 🚀 Cómo Usar el Sistema

### 1. Instalación y Configuración

```bash
# Clonar el repositorio
git clone <repo-url>
cd Acubat

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar OpenAI (opcional)
export OPENAI_API_KEY="tu-api-key-aqui"
```

### 2. Ejecutar el Sistema

```bash
# Iniciar servidor
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Abrir en navegador
open http://localhost:8000
```

### 3. Procesar Archivos

1. **Subir archivo Excel/CSV** con formato:
   ```
   MODELO,DESCRIPCION,MARCA,RUBRO,PRECIO LISTA,PVP ON LINE,Q. PALLET
   BAT001,Batería 60Ah Moura,MOURA,BATERIAS,120.50,162.68,10
   ```

2. **El sistema automáticamente**:
   - Aplica markup según canal y marca
   - Calcula precios finales
   - Evalúa alertas
   - Analiza con IA (si está disponible)

3. **Revisar resultados** en la interfaz web

### 4. Exportar Datos

- **CSV Completo**: Botón "Exportar CSV" en el dashboard
- **Filtros**: Aplicar filtros antes de exportar
- **Formato**: Incluye todos los campos procesados

## 📊 Ejemplos de Uso

### Ejemplo 1: Producto Minorista Moura

```
Entrada:
- Código: BAT001
- Marca: MOURA
- Canal: MINORISTA
- Precio Base: $120.50

Procesamiento:
- Markup: 35%
- Precio con Markup: $162.68
- Redondeo: $200.00 (múltiplo de $100)
- Margen: 66.0%
- Estado: OK
```

### Ejemplo 2: Producto Mayorista Acubat

```
Entrada:
- Código: BAT004
- Marca: ACUBAT
- Canal: MAYORISTA
- Precio Base: $160.00

Procesamiento:
- Markup: 25%
- Precio con Markup: $200.00
- Redondeo: $200.00 (2 decimales)
- Margen: 25.0%
- Estado: OK
```

## 🔧 Configuración Avanzada

### Modificar Markups

Editar `api/logic.py`:

```python
self.markup_config = {
    (Canal.MINORISTA, Marca.MOURA): 0.40,  # Cambiar a 40%
    # ... otros markups
}
```

### Ajustar Alertas

```python
# En api/logic.py
self.margen_minimo = 0.15  # Cambiar a 15%
self.margen_maximo = 0.70  # Cambiar a 70%
```

### Configurar OpenAI

```bash
# Variables de entorno
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-3.5-turbo"  # Opcional
```

## 🧪 Pruebas

### Ejecutar Pruebas Automáticas

```bash
python3 test_fase2.py
```

### Pruebas Manuales

1. **Subir archivo de ejemplo**:
   ```bash
   curl -X POST "http://localhost:8000/upload" \
        -F "file=@ejemplo_pricing.xlsx"
   ```

2. **Obtener análisis IA**:
   ```bash
   curl "http://localhost:8000/api/analisis-openai"
   ```

3. **Exportar CSV**:
   ```bash
   curl "http://localhost:8000/export/csv" -o productos.csv
   ```

## 📈 Métricas y KPIs

### Métricas Automáticas

- **Total de productos procesados**
- **Productos con alertas**
- **Margen promedio por marca/canal**
- **Distribución de alertas por tipo**

### Dashboard en Tiempo Real

- 📊 Resúmenes visuales
- 🎯 Indicadores de rendimiento
- 🔍 Filtros interactivos
- 📄 Exportación inmediata

## 🔮 Próximas Mejoras (Fase 3)

- 📊 **Gráficos interactivos** con Plotly
- 🔄 **Sincronización con ERP** en tiempo real
- 📱 **App móvil** para consultas rápidas
- 🤖 **IA más avanzada** con GPT-4
- 📈 **Análisis predictivo** de precios
- 🔔 **Notificaciones automáticas** por email

## 🆘 Soporte

### Problemas Comunes

1. **OpenAI no disponible**:
   - Verificar `OPENAI_API_KEY` en variables de entorno
   - El sistema funciona sin IA

2. **Error al procesar archivo**:
   - Verificar formato del Excel/CSV
   - Columnas requeridas: MODELO, DESCRIPCION, MARCA, PRECIO LISTA

3. **Markup no aplicado**:
   - Verificar combinación canal+marca en configuración
   - Revisar logs del servidor

### Logs y Debugging

```bash
# Ver logs del servidor
tail -f logs/app.log

# Probar componentes individuales
python3 -c "from api.logic import PricingLogic; print('OK')"
```

---

**¡La Fase 2 está lista para producción! 🎉**

El sistema de pricing inteligente está completamente funcional y listo para procesar archivos reales de productos con análisis automático de precios y márgenes. 