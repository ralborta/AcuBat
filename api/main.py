from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
import shutil
from typing import List, Optional
import logging

from .models import Producto, Canal, Marca, TipoAlerta, ProductoResponse
from .parser import ExcelParser
from .logic import LogicaNegocio
from .openai_helper import OpenAIHelper

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Backend Acubat",
    description="Sistema de gestión de productos con procesamiento de Excel y alertas inteligentes",
    version="1.0.0"
)

# Configurar archivos estáticos y templates
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # En Vercel no necesitamos archivos estáticos
templates = Jinja2Templates(directory="templates")

# Inicializar componentes
parser = ExcelParser()
logica = LogicaNegocio()
openai_helper = OpenAIHelper()

# Variable global para almacenar productos procesados
productos_actuales: List[Producto] = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "productos": productos_actuales,
        "total_productos": len(productos_actuales),
        "productos_con_alertas": len([p for p in productos_actuales if p.alertas]),
        "openai_disponible": openai_helper.esta_disponible()
    })

@app.get("/alertas", response_class=HTMLResponse)
async def alertas(request: Request):
    """Página de alertas"""
    productos_con_alertas = [p for p in productos_actuales if p.alertas]
    return templates.TemplateResponse("alertas.html", {
        "request": request,
        "productos": productos_con_alertas,
        "total_alertas": len(productos_con_alertas)
    })

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo Excel"""
    try:
        # Verificar que sea un archivo Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls)")
        
        # Guardar archivo temporalmente
        ruta_archivo = f"data/{file.filename}"
        os.makedirs("data", exist_ok=True)
        
        with open(ruta_archivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Procesar archivo
        productos = parser.leer_excel(ruta_archivo)
        productos_procesados = logica.procesar_productos(productos)
        
        # Actualizar productos globales
        global productos_actuales
        productos_actuales = productos_procesados
        
        # Limpiar archivo temporal
        os.remove(ruta_archivo)
        
        return {
            "mensaje": "Archivo procesado exitosamente",
            "productos_procesados": len(productos_procesados),
            "productos_con_alertas": len([p for p in productos_procesados if p.alertas])
        }
        
    except Exception as e:
        logger.error(f"Error al procesar archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.get("/api/productos")
async def get_productos(
    canal: Optional[Canal] = None,
    marca: Optional[Marca] = None,
    con_alertas: Optional[bool] = None
):
    """API endpoint para obtener productos con filtros"""
    productos_filtrados = logica.obtener_productos_filtrados(
        productos_actuales, canal, marca, con_alertas
    )
    
    resumen = logica.generar_resumen(productos_filtrados)
    
    return ProductoResponse(
        productos=productos_filtrados,
        total_productos=resumen["total_productos"],
        productos_con_alertas=resumen["productos_con_alertas"],
        resumen_marcas=resumen["resumen_marcas"],
        resumen_canales=resumen["resumen_canales"]
    )

@app.get("/api/alertas")
async def get_alertas():
    """API endpoint para obtener solo productos con alertas"""
    productos_con_alertas = [p for p in productos_actuales if p.alertas]
    
    return {
        "productos": productos_con_alertas,
        "total_alertas": len(productos_con_alertas),
        "tipos_alertas": {
            "margen_bajo": len([p for p in productos_con_alertas if TipoAlerta.MARGEN_BAJO in p.alertas]),
            "sin_codigo": len([p for p in productos_con_alertas if TipoAlerta.SIN_CODIGO in p.alertas]),
            "precio_liberado": len([p for p in productos_con_alertas if TipoAlerta.PRECIO_LIBERADO in p.alertas]),
            "sin_markup": len([p for p in productos_con_alertas if TipoAlerta.SIN_MARKUP in p.alertas]),
            "precio_fuera_rango": len([p for p in productos_con_alertas if TipoAlerta.PRECIO_FUERA_RANGO in p.alertas])
        }
    }

@app.post("/api/analizar-ai")
async def analizar_con_ai():
    """Analiza productos con OpenAI"""
    if not openai_helper.esta_disponible():
        raise HTTPException(status_code=400, detail="OpenAI no está disponible")
    
    try:
        # Analizar productos con alertas
        productos_con_alertas = [p for p in productos_actuales if p.alertas]
        sugerencias = openai_helper.analizar_lista_productos(productos_con_alertas)
        
        # Detectar anomalías
        anomalias = openai_helper.detectar_anomalias(productos_actuales)
        
        return {
            "sugerencias": sugerencias,
            "anomalias": anomalias,
            "productos_analizados": len(productos_con_alertas)
        }
        
    except Exception as e:
        logger.error(f"Error en análisis con IA: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.post("/api/sugerir-markup/{codigo_producto}")
async def sugerir_markup(codigo_producto: str, contexto: str = Form("")):
    """Sugiere markup para un producto específico"""
    if not openai_helper.esta_disponible():
        raise HTTPException(status_code=400, detail="OpenAI no está disponible")
    
    producto = next((p for p in productos_actuales if p.codigo == codigo_producto), None)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    try:
        sugerencia = openai_helper.sugerir_markup(producto, contexto)
        return sugerencia
        
    except Exception as e:
        logger.error(f"Error al sugerir markup: {e}")
        raise HTTPException(status_code=500, detail=f"Error al sugerir markup: {str(e)}")

@app.get("/api/resumen")
async def get_resumen():
    """Obtiene resumen estadístico de productos"""
    resumen = logica.generar_resumen(productos_actuales)
    return resumen

@app.post("/api/crear-ejemplo")
async def crear_archivo_ejemplo():
    """Crea un archivo Excel de ejemplo para testing"""
    try:
        ruta_archivo = parser.crear_archivo_ejemplo()
        return {"mensaje": "Archivo de ejemplo creado", "ruta": ruta_archivo}
    except Exception as e:
        logger.error(f"Error al crear archivo de ejemplo: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "productos_cargados": len(productos_actuales),
        "openai_disponible": openai_helper.esta_disponible(),
        "productos_con_alertas": len([p for p in productos_actuales if p.alertas]),
        "marcas_disponibles": [marca.value for marca in Marca],
        "canales_disponibles": [canal.value for canal in Canal]
    }

# Endpoint para limpiar datos
@app.delete("/api/limpiar")
async def limpiar_datos():
    """Limpia todos los productos cargados"""
    global productos_actuales
    productos_actuales = []
    return {"mensaje": "Datos limpiados exitosamente"}

# Manejo de errores
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error": "Página no encontrada",
        "mensaje": "La página que buscas no existe."
    })

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error": "Error interno del servidor",
        "mensaje": "Ha ocurrido un error inesperado."
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 