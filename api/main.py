from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import os
import json

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detectar si estamos en Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

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
    from .parser import ExcelParser, detect_and_parse_file, is_moura_file
    
    pricing_logic = PricingLogic()
    openai_helper = OpenAIHelper()
    excel_parser = ExcelParser()
    
    MODULES_AVAILABLE = True
    logger.info("✅ Módulos completos cargados exitosamente")
except ImportError as e:
    logger.warning(f"⚠️ Algunos módulos no están disponibles: {e}")
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
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-3 bg-light p-4 min-vh-100">
                            <h4 class="mb-4">
                                <i class="fas fa-chart-line text-primary"></i>
                                Rating: Calificación
                            </h4>
                            
                            <div class="card bg-primary text-white p-3 mb-3">
                                <h2 class="display-4 text-center">0</h2>
                                <p class="text-center mb-0">Productos Cargados</p>
                            </div>

                            <div class="card bg-warning text-white p-3 mb-3">
                                <h2 class="display-4 text-center">0</h2>
                                <p class="text-center mb-0">Con Alertas</p>
                            </div>

                            <div class="mt-4">
                                <h5><i class="fas fa-filter text-info"></i> Filtros</h5>
                                <select class="form-select mb-2">
                                    <option value="">Todos los canales</option>
                                </select>
                                
                                <select class="form-select mb-2">
                                    <option value="">Todas las marcas</option>
                                </select>
                                
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filtroAlertas">
                                    <label class="form-check-label" for="filtroAlertas">
                                        Solo con alertas
                                    </label>
                                </div>
                            </div>

                            <div class="mt-4">
                                <button class="btn btn-success w-100 mb-2" onclick="exportarCSV()">
                                    <i class="fas fa-download"></i> Exportar CSV
                                </button>
                                
                                <div class="alert alert-warning alert-sm">
                                    <i class="fas fa-exclamation-triangle"></i>
                                    Sistema en modo básico
                                </div>
                            </div>
                        </div>

                        <div class="col-md-9 p-4">
                            <h1 class="mb-4">
                                <i class="fas fa-rocket text-primary"></i>
                                AcuBat - Sistema de Pricing Inteligente
                            </h1>

                            <div class="alert alert-info">
                                <h4>🚀 Sistema Funcionando</h4>
                                <p>El sistema está funcionando en modo optimizado. Sube archivos Excel/CSV para comenzar.</p>
                            </div>

                            <div class="card shadow-sm">
                                <div class="card-body">
                                    <h5 class="card-title">
                                        <i class="fas fa-cloud-upload-alt text-primary"></i>
                                        Cargar Lista de Precios
                                    </h5>
                                    
                                    <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-primary mb-3"></i>
                                        <h5>Arrastra tu archivo aquí</h5>
                                        <p class="text-muted">Soporta Excel (.xlsx, .xls) y CSV (.csv)</p>
                                        <button class="btn btn-primary">
                                            <i class="fas fa-file-upload"></i>
                                            Seleccionar Archivo
                                        </button>
                                    </div>

                                    <input type="file" id="fileInput" accept=".xlsx,.xls,.csv" style="display: none;">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                <script>
                    const uploadArea = document.getElementById('uploadArea');
                    const fileInput = document.getElementById('fileInput');

                    uploadArea.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        uploadArea.classList.add('dragover');
                    });

                    uploadArea.addEventListener('dragleave', () => {
                        uploadArea.classList.remove('dragover');
                    });

                    uploadArea.addEventListener('drop', (e) => {
                        e.preventDefault();
                        uploadArea.classList.remove('dragover');
                        const files = e.dataTransfer.files;
                        if (files.length > 0) {
                            subirArchivo(files[0]);
                        }
                    });

                    fileInput.addEventListener('change', (e) => {
                        if (e.target.files.length > 0) {
                            subirArchivo(e.target.files[0]);
                        }
                    });

                    function subirArchivo(file) {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.mensaje) {
                                alert('✅ ' + data.mensaje);
                                location.reload();
                            } else {
                                alert('❌ Error: ' + (data.detail || 'Error desconocido'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('❌ Error al subir archivo');
                        });
                    }

                    function exportarCSV() {
                        window.location.href = '/export/csv';
                    }
                </script>
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
            "resumen_canales": resumen_canales,
            "is_vercel": IS_VERCEL
        })
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
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
        "is_vercel": IS_VERCEL,
        "productos_cargados": len(productos_actuales) if productos_actuales else 0
    }

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente",
        "productos_cargados": len(productos_actuales) if productos_actuales else 0,
        "modules_available": MODULES_AVAILABLE,
        "is_vercel": IS_VERCEL
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para subir archivo de productos"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema en modo básico. Módulos de procesamiento no disponibles.")
        
        # Verificar tipo de archivo
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no soportado: {file.filename}. Solo se permiten Excel (.xlsx, .xls) o CSV (.csv)")
        
        # Leer contenido del archivo
        contenido = file.file.read()
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        logger.info(f"Procesando archivo: {file.filename} ({len(contenido)} bytes)")
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Verificar si es archivo MOURA
            es_moura = is_moura_file(temp_file_path)
            logger.info(f"Archivo detectado como MOURA: {es_moura}")
            
            # Usar el nuevo sistema de detección y parsing
            productos_data = detect_and_parse_file(temp_file_path)
            
            if not productos_data:
                raise HTTPException(status_code=400, detail="No se pudieron extraer productos del archivo. Verifica que el archivo contenga datos válidos.")
            
            logger.info(f"Productos extraídos: {len(productos_data)}")
            
            # Procesar productos con pricing y rentabilidad
            productos_procesados = pricing_logic.procesar_productos_con_rentabilidad(productos_data)
            
            # Guardar productos en memoria
            global productos_actuales
            productos_actuales = productos_procesados
            
            return {
                "mensaje": f"✅ Archivo procesado exitosamente. {len(productos_procesados)} productos cargados.",
                "productos": len(productos_procesados),
                "archivo": file.filename,
                "tipo_detectado": "MOURA" if es_moura else "Genérico",
                "tamaño_archivo": len(contenido)
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al procesar archivo {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.post("/cargar-rentabilidades")
async def upload_rentabilidades(file: UploadFile = File(...)):
    """Endpoint para subir archivo de rentabilidades"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema en modo básico. Módulos de procesamiento no disponibles.")
        
        # Verificar que sea un archivo Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no soportado: {file.filename}. Solo se permiten archivos Excel (.xlsx, .xls) para rentabilidades")
        
        # Leer el archivo
        contenido = file.file.read()
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        logger.info(f"Procesando archivo de rentabilidades: {file.filename} ({len(contenido)} bytes)")
        
        # Guardar archivo temporalmente
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Cargar rentabilidades
            rentabilidad_cargada = pricing_logic.cargar_rentabilidades(temp_file_path)
            
            if not rentabilidad_cargada:
                raise HTTPException(status_code=400, detail="No se pudo cargar el archivo de rentabilidades. Verifica que el archivo contenga hojas con columnas: Canal, Línea, Margen Mínimo, Margen Óptimo")
            
            # Obtener resumen de rentabilidades
            resumen_rentabilidad = pricing_logic.rentabilidad_validator.obtener_resumen_rentabilidad()
            
            logger.info(f"Rentabilidades cargadas exitosamente: {resumen_rentabilidad.get('total_reglas', 0)} reglas")
            
            return {
                "mensaje": f"Archivo de rentabilidades cargado exitosamente. {resumen_rentabilidad.get('total_reglas', 0)} reglas procesadas.",
                "reglas_cargadas": resumen_rentabilidad.get('total_reglas', 0),
                "resumen_rentabilidad": resumen_rentabilidad,
                "archivo_original": file.filename,
                "tamaño_archivo": len(contenido)
            }
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar rentabilidades {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al cargar rentabilidades: {str(e)}")

@app.get("/api/estado-rentabilidad")
async def obtener_estado_rentabilidad():
    """Obtiene el estado de las rentabilidades cargadas"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de rentabilidad no disponible")
        
        archivo_cargado = pricing_logic.rentabilidad_validator.archivo_cargado
        resumen = pricing_logic.rentabilidad_validator.obtener_resumen_rentabilidad()
        
        return {
            "archivo_cargado": archivo_cargado,
            "total_reglas": resumen.get('total_reglas', 0),
            "resumen": resumen
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de rentabilidad: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

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

@app.get("/api/reporte-pricing")
async def obtener_reporte_pricing():
    """Obtener reporte completo de pricing"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos para analizar")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de reportes no disponible")
        
        # Generar reporte completo
        reporte = pricing_logic.generar_reporte_pricing(productos_actuales)
        
        return {
            "mensaje": "Reporte de pricing generado exitosamente",
            "reporte": reporte,
            "fecha_generacion": "2024-01-01"
        }
    except Exception as e:
        logger.error(f"Error generando reporte de pricing: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@app.get("/api/sugerencias-precio/{codigo_producto}")
async def obtener_sugerencias_precio(codigo_producto: str):
    """Obtener sugerencias de precio para un producto específico"""
    try:
        if not productos_actuales:
            raise HTTPException(status_code=404, detail="No hay productos cargados")
        
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de sugerencias no disponible")
        
        # Buscar producto por código
        producto = next((p for p in productos_actuales if p.codigo == codigo_producto), None)
        
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {codigo_producto} no encontrado")
        
        # Generar sugerencias
        sugerencias = pricing_logic.generar_sugerencias_precio(producto)
        
        return {
            "producto": {
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "precio_actual": producto.precio_final,
                "margen_actual": producto.margen
            },
            "sugerencias": sugerencias
        }
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias para {codigo_producto}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}") 