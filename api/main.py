from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import pandas as pd

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
        
        # Crear buffer en memoria
        buffer = io.BytesIO(contenido)
        
        # Leer Excel
        try:
            df = pd.read_excel(buffer, engine='openpyxl')
        except:
            buffer.seek(0)
            df = pd.read_excel(buffer, engine='xlrd')
        
        # Verificar que tenga datos
        if df.empty:
            raise HTTPException(status_code=400, detail="El archivo Excel está vacío")
        
        # Procesamiento básico
        productos_procesados = len(df)
        productos_con_alertas = 0
        
        # Actualizar productos globales (simplificado)
        global productos_actuales
        productos_actuales = [{"codigo": f"PROD_{i}", "nombre": str(row.iloc[0]) if len(row) > 0 else "Sin nombre"} 
                             for i, row in df.iterrows()]
        
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