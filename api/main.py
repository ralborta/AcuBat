from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import os

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Backend Acubat",
    description="Sistema de gestión de productos con procesamiento de Excel y alertas inteligentes",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Variables globales para almacenar productos procesados
productos_actuales = []

# Importar módulos de forma segura
try:
    from .logic import PricingLogic
    from .openai_helper import OpenAIHelper
    from .parser import ExcelParser
    
    pricing_logic = PricingLogic()
    openai_helper = OpenAIHelper()
    excel_parser = ExcelParser()
    
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Algunos módulos no están disponibles: {e}")
    MODULES_AVAILABLE = False

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    try:
        if not MODULES_AVAILABLE:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Acubat - Sistema de Pricing</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h1>🚀 AcuBat - Sistema de Pricing Inteligente</h1>
                    <div class="alert alert-warning">
                        <h4>⚠️ Sistema en Modo Básico</h4>
                        <p>Algunos módulos no están disponibles en este entorno. El sistema funciona en modo básico.</p>
                    </div>
                    <div class="card">
                        <div class="card-body">
                            <h5>✅ Funcionalidades Disponibles:</h5>
                            <ul>
                                <li>✅ Health Check del sistema</li>
                                <li>✅ Verificación de estado</li>
                                <li>⚠️ Procesamiento de archivos (limitado)</li>
                            </ul>
                        </div>
                    </div>
                    <a href="/health" class="btn btn-primary">Verificar Estado</a>
                </div>
            </body>
            </html>
            """)
        
        # Generar resúmenes si los módulos están disponibles
        resumen_marcas = pricing_logic.obtener_resumen_marcas(productos_actuales) if productos_actuales and MODULES_AVAILABLE else {}
        resumen_canales = pricing_logic.obtener_resumen_canales(productos_actuales) if productos_actuales and MODULES_AVAILABLE else {}
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "productos": productos_actuales if productos_actuales else [],
            "total_productos": len(productos_actuales) if productos_actuales else 0,
            "productos_con_alertas": len([p for p in productos_actuales if p.alertas]) if productos_actuales else 0,
            "openai_disponible": openai_helper.esta_disponible() if MODULES_AVAILABLE else False,
            "resumen_marcas": resumen_marcas,
            "resumen_canales": resumen_canales
        })
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        # Retornar una página simple en caso de error
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Acubat - Error</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <h1>🚀 Backend Acubat</h1>
                <div class="alert alert-danger">
                    <h4>❌ Error cargando la página</h4>
                    <p>{str(e)}</p>
                </div>
                <p>Productos cargados: {len(productos_actuales) if productos_actuales else 0}</p>
                <a href="/health" class="btn btn-primary">Health Check</a>
            </div>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check para verificar que la aplicación funciona"""
    return {
        "status": "healthy", 
        "message": "Backend Acubat funcionando",
        "modules_available": MODULES_AVAILABLE,
        "productos_cargados": len(productos_actuales) if productos_actuales else 0
    }

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente",
        "productos_cargados": len(productos_actuales) if productos_actuales else 0,
        "modules_available": MODULES_AVAILABLE
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo Excel y procesar con pricing"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema en modo básico. Módulos de procesamiento no disponibles.")
        
        # Verificar que sea un archivo soportado
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls) o CSV (.csv)")
        
        # Leer el archivo
        contenido = file.file.read()
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Guardar archivo temporalmente
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Procesar archivo Excel/CSV
            productos = excel_parser.leer_excel(temp_file_path)
            
            if not productos:
                raise HTTPException(status_code=400, detail="No se pudieron procesar productos del archivo")
            
            # Aplicar pricing logic
            productos_procesados = pricing_logic.procesar_productos(productos)
            
            # Analizar con OpenAI si está disponible
            if openai_helper.esta_disponible():
                productos_analizados = openai_helper.analizar_lote_productos(productos_procesados)
                productos_procesados = productos_analizados
            
            # Actualizar productos globales
            global productos_actuales
            productos_actuales = productos_procesados
            
            # Generar resúmenes
            resumen_marcas = pricing_logic.obtener_resumen_marcas(productos_procesados)
            resumen_canales = pricing_logic.obtener_resumen_canales(productos_procesados)
            
            productos_con_alertas = len([p for p in productos_procesados if p.alertas])
            
            return {
                "mensaje": "Archivo procesado exitosamente con pricing",
                "productos_procesados": len(productos_procesados),
                "productos_con_alertas": productos_con_alertas,
                "resumen_marcas": resumen_marcas,
                "resumen_canales": resumen_canales,
                "openai_utilizado": openai_helper.esta_disponible(),
                "archivo_original": file.filename
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.get("/export/csv")
async def export_csv():
    """Exportar productos a CSV"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para exportar")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de exportación no disponible")
        
        # Crear CSV
        csv_content = pricing_logic.exportar_a_csv(productos_actuales)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=productos_pricing.csv"}
        )
    except Exception as e:
        logger.error(f"Error al exportar CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error al exportar: {str(e)}")

@app.get("/api/analisis-openai")
async def obtener_analisis_openai():
    """Obtener análisis de OpenAI de productos actuales"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para analizar")
        
        if not MODULES_AVAILABLE or not openai_helper.esta_disponible():
            raise HTTPException(status_code=503, detail="Análisis OpenAI no disponible")
        
        # Analizar productos con OpenAI
        productos_analizados = openai_helper.analizar_lote_productos(productos_actuales)
        
        return {
            "mensaje": "Análisis OpenAI completado",
            "productos_analizados": len(productos_analizados),
            "sugerencias_generadas": len([p for p in productos_analizados if p.sugerencias_openai])
        }
    except Exception as e:
        logger.error(f"Error en análisis OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/api/filtrar")
async def filtrar_productos(
    canal: str = None,
    marca: str = None,
    con_alertas: bool = None
):
    """Filtrar productos por criterios"""
    try:
        if not productos_actuales:
            return {"productos": [], "total": 0}
        
        productos_filtrados = productos_actuales.copy()
        
        if canal:
            productos_filtrados = [p for p in productos_filtrados if p.canal == canal]
        
        if marca:
            productos_filtrados = [p for p in productos_filtrados if p.marca == marca]
        
        if con_alertas is not None:
            if con_alertas:
                productos_filtrados = [p for p in productos_filtrados if p.alertas]
            else:
                productos_filtrados = [p for p in productos_filtrados if not p.alertas]
        
        return {
            "productos": productos_filtrados,
            "total": len(productos_filtrados),
            "filtros_aplicados": {
                "canal": canal,
                "marca": marca,
                "con_alertas": con_alertas
            }
        }
    except Exception as e:
        logger.error(f"Error al filtrar productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al filtrar: {str(e)}") 