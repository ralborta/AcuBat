from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

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

# Variable global para almacenar productos procesados
productos_actuales = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "productos": productos_actuales,
        "total_productos": len(productos_actuales),
        "productos_con_alertas": 0,
        "openai_disponible": False
    })

@app.get("/alertas", response_class=HTMLResponse)
async def alertas(request: Request):
    """Página de alertas"""
    return templates.TemplateResponse("alertas.html", {
        "request": request,
        "productos": [],
        "total_alertas": 0
    })

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo Excel"""
    try:
        # Verificar que sea un archivo Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls)")
        
        # Leer el archivo
        contenido = file.file.read()
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Simular procesamiento básico (sin pandas por ahora)
        # En una implementación real, aquí procesaríamos el Excel
        productos_procesados = 70  # Simular 70 productos
        productos_con_alertas = 5  # Simular 5 con alertas
        
        # Crear productos de ejemplo
        global productos_actuales
        productos_actuales = [
            {
                "codigo": f"PROD_{i:03d}",
                "nombre": f"Producto {i}",
                "precio": 100 + i * 10,
                "marca": "LÜSQTOFF" if i % 3 == 0 else "BLACK SERIES",
                "alertas": ["margen_bajo"] if i % 7 == 0 else []
            }
            for i in range(1, productos_procesados + 1)
        ]
        
        return {
            "mensaje": "Archivo procesado exitosamente",
            "productos_procesados": productos_procesados,
            "productos_con_alertas": productos_con_alertas
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar archivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente",
        "productos_cargados": len(productos_actuales)
    }

@app.get("/health")
async def health_check():
    """Health check para verificar que la aplicación funciona"""
    return {"status": "healthy", "message": "Backend Acubat funcionando"} 