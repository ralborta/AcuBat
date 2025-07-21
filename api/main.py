from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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

# Variables globales para almacenar datos
rentabilidades_data = None
rentabilidades_filename = None
precios_data = None
precios_filename = None

# Importar módulos de forma segura
try:
    from .logic import PricingLogic
    from .openai_helper import OpenAIHelper
    from .parser import ExcelParser, detect_and_parse_file, is_moura_file
    from .models import Producto, Marca, Canal
    
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
            "productos_con_alertas": len([p for p in productos_actuales if p.get('alertas')]) if productos_actuales else 0,
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

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar que la aplicación funciona"""
    return {
        "mensaje": "✅ API funcionando correctamente",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "ok"
    }

@app.get("/test-simple")
async def test_simple():
    """Endpoint de test simple para verificar que el servidor funciona"""
    return {
        "status": "ok",
        "mensaje": "Servidor funcionando correctamente",
        "timestamp": "2024-12-19"
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Endpoint de test para subir archivos"""
    try:
        logger.info(f"=== TEST UPLOAD ===")
        logger.info(f"Archivo: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        return {
            "status": "ok",
            "archivo": file.filename,
            "tamaño": len(contenido),
            "content_type": file.content_type,
            "mensaje": "Archivo recibido correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error en test upload: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

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
        logger.info(f"=== INICIO UPLOAD ===")
        logger.info(f"Archivo recibido: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Verificación básica
        if not file.filename:
            raise HTTPException(status_code=400, detail="No se proporcionó nombre de archivo")
        
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail=f"Tipo de archivo no soportado: {file.filename}")
        
        # Leer contenido del archivo
        contenido = file.file.read()
        logger.info(f"Contenido leído: {len(contenido)} bytes")
        
        if not contenido:
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Por ahora, solo devolver información básica
        logger.info(f"=== UPLOAD BÁSICO EXITOSO ===")
        
        return {
            "mensaje": f"✅ Archivo recibido correctamente: {file.filename} ({len(contenido)} bytes)",
            "archivo": file.filename,
            "tamaño": len(contenido),
            "tipo": file.content_type,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en upload: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

@app.post("/cargar-rentabilidades")
async def upload_rentabilidades(file: UploadFile = File(...)):
    """Endpoint SIMPLE para subir archivo de rentabilidades"""
    global rentabilidades_data, rentabilidades_filename
    
    try:
        logger.info(f"=== CARGA SIMPLE DE RENTABILIDADES ===")
        logger.info(f"Archivo: {file.filename}")
        
        # Verificar que sea Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {
                "status": "error",
                "mensaje": "Solo archivos Excel (.xlsx, .xls)"
            }
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if len(contenido) == 0:
            return {
                "status": "error", 
                "mensaje": "Archivo vacío"
            }
        
        # Guardar temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Leer y guardar en memoria
            import pandas as pd
            excel_file = pd.ExcelFile(temp_file_path)
            
            # Guardar datos en memoria
            rentabilidades_data = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                rentabilidades_data[sheet_name] = df.to_dict('records')
            
            rentabilidades_filename = file.filename
            
            logger.info(f"✅ Archivo guardado en memoria: {file.filename} con {len(excel_file.sheet_names)} hojas")
            
            return {
                "status": "success",
                "mensaje": f"Archivo de rentabilidades cargado exitosamente: {file.filename}",
                "hojas": excel_file.sheet_names,
                "total_hojas": len(excel_file.sheet_names),
                "tamaño": len(contenido),
                "archivo_guardado": file.filename
            }
            
        except Exception as e:
            logger.error(f"Error leyendo Excel: {str(e)}")
            return {
                "status": "error",
                "mensaje": f"Error al leer archivo Excel: {str(e)}"
            }
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return {
            "status": "error",
            "mensaje": f"Error: {str(e)}"
        }

@app.post("/cargar-precios")
async def upload_precios(file: UploadFile = File(...)):
    """Endpoint para subir archivo de precios"""
    global precios_data, precios_filename
    
    try:
        logger.info(f"=== CARGA SIMPLE DE PRECIOS ===")
        logger.info(f"Archivo: {file.filename}")
        
        # Verificar que sea Excel
        if not file.filename.endswith(('.xlsx', '.xls')):
            return {
                "status": "error",
                "mensaje": "Solo archivos Excel (.xlsx, .xls)"
            }
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if len(contenido) == 0:
            return {
                "status": "error", 
                "mensaje": "Archivo vacío"
            }
        
        # Guardar temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Leer y guardar en memoria
            import pandas as pd
            excel_file = pd.ExcelFile(temp_file_path)
            
            # Guardar datos en memoria
            precios_data = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                precios_data[sheet_name] = df.to_dict('records')
            
            precios_filename = file.filename
            
            logger.info(f"✅ Archivo guardado en memoria: {file.filename} con {len(excel_file.sheet_names)} hojas")
            
            return {
                "status": "success",
                "mensaje": f"Archivo de precios cargado exitosamente: {file.filename}",
                "hojas": excel_file.sheet_names,
                "total_hojas": len(excel_file.sheet_names),
                "tamaño": len(contenido),
                "archivo_guardado": file.filename
            }
            
        except Exception as e:
            logger.error(f"Error leyendo Excel: {str(e)}")
            return {
                "status": "error",
                "mensaje": f"Error al leer archivo Excel: {str(e)}"
            }
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return {
            "status": "error",
            "mensaje": f"Error: {str(e)}"
        }

@app.post("/diagnostico-excel")
async def diagnostico_excel(file: UploadFile = File(...)):
    """Endpoint para diagnóstico completo de archivos Excel"""
    try:
        logger.info(f"=== DIAGNÓSTICO COMPLETO EXCEL ===")
        logger.info(f"Archivo: {file.filename}")
        logger.info(f"Content-Type: {file.content_type}")
        
        # Leer archivo
        contenido = file.file.read()
        logger.info(f"Tamaño: {len(contenido)} bytes")
        
        if not contenido:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        
        # Guardar temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            import pandas as pd
            
            # Leer Excel
            excel_file = pd.ExcelFile(temp_file_path)
            logger.info(f"Excel con {len(excel_file.sheet_names)} hojas")
            
            diagnostico_completo = {
                "archivo": file.filename,
                "tamaño_bytes": len(contenido),
                "total_hojas": len(excel_file.sheet_names),
                "hojas": []
            }
            
            # Analizar cada hoja
            for i, sheet_name in enumerate(excel_file.sheet_names):
                logger.info(f"=== ANALIZANDO HOJA {i+1}: {sheet_name} ===")
                
                # Leer hoja
                df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
                
                # Información básica
                info_hoja = {
                    "nombre": sheet_name,
                    "filas": len(df),
                    "columnas": len(df.columns),
                    "nombres_columnas": list(df.columns),
                    "tipos_columnas": df.dtypes.to_dict(),
                    "es_hoja_moura": 'moura' in sheet_name.lower(),
                    "primeras_filas": df.head(3).to_dict('records')
                }
                
                # Buscar columnas requeridas
                columnas_requeridas = {
                    "canal": False,
                    "línea": False, 
                    "margen_minimo": False,
                    "margen_optimo": False
                }
                
                for col in df.columns:
                    col_str = str(col).lower().strip()
                    if any(palabra in col_str for palabra in ['canal', 'channel']):
                        columnas_requeridas["canal"] = True
                    if any(palabra in col_str for palabra in ['línea', 'linea', 'line']):
                        columnas_requeridas["línea"] = True
                    if any(palabra in col_str for palabra in ['margen mínimo', 'margen_minimo', 'minimo']):
                        columnas_requeridas["margen_minimo"] = True
                    if any(palabra in col_str for palabra in ['margen óptimo', 'margen_optimo', 'optimo']):
                        columnas_requeridas["margen_optimo"] = True
                
                info_hoja["columnas_requeridas_encontradas"] = columnas_requeridas
                info_hoja["tiene_todas_las_columnas"] = all(columnas_requeridas.values())
                
                diagnostico_completo["hojas"].append(info_hoja)
                
                logger.info(f"Hoja '{sheet_name}': {len(df)} filas, {len(df.columns)} columnas")
                logger.info(f"Columnas: {list(df.columns)}")
                logger.info(f"Es Moura: {info_hoja['es_hoja_moura']}")
                logger.info(f"Tiene todas las columnas: {info_hoja['tiene_todas_las_columnas']}")
            
            # Resumen
            hojas_moura = [h for h in diagnostico_completo["hojas"] if h["es_hoja_moura"]]
            hojas_validas = [h for h in diagnostico_completo["hojas"] if h["tiene_todas_las_columnas"]]
            
            diagnostico_completo["resumen"] = {
                "hojas_moura_encontradas": len(hojas_moura),
                "hojas_con_todas_las_columnas": len(hojas_validas),
                "puede_procesarse": len(hojas_moura) > 0 and len(hojas_validas) > 0
            }
            
            logger.info(f"=== DIAGNÓSTICO COMPLETO ===")
            logger.info(f"Resumen: {diagnostico_completo['resumen']}")
            
            return diagnostico_completo
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en diagnóstico: {str(e)}")

@app.get("/api/diagnostico-archivos")
async def diagnostico_archivos():
    """Diagnosticar qué archivos y hojas están cargados"""
    global precios_data, rentabilidades_data, precios_filename, rentabilidades_filename
    
    try:
        resultado = {
            "precios": {
                "cargado": precios_data is not None,
                "archivo": precios_filename,
                "hojas": list(precios_data.keys()) if precios_data else []
            },
            "rentabilidades": {
                "cargado": rentabilidades_data is not None,
                "archivo": rentabilidades_filename,
                "hojas": list(rentabilidades_data.keys()) if rentabilidades_data else []
            }
        }
        
        # Agregar información de columnas si hay datos
        if precios_data and len(precios_data) > 0:
            primera_hoja = list(precios_data.keys())[0]
            if len(precios_data[primera_hoja]) > 0:
                resultado["precios"]["columnas"] = list(precios_data[primera_hoja][0].keys())
        
        if rentabilidades_data and len(rentabilidades_data) > 0:
            primera_hoja = list(rentabilidades_data.keys())[0]
            if len(rentabilidades_data[primera_hoja]) > 0:
                resultado["rentabilidades"]["columnas"] = list(rentabilidades_data[primera_hoja][0].keys())
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en diagnóstico: {str(e)}")
        return {
            "error": str(e),
            "precios": {"cargado": False},
            "rentabilidades": {"cargado": False}
        }

@app.get("/api/diagnostico-detallado")
async def diagnostico_detallado():
    """Diagnóstico detallado de los datos cargados"""
    global precios_data, rentabilidades_data
    
    try:
        resultado = {
            "precios": {
                "cargado": precios_data is not None,
                "hojas": list(precios_data.keys()) if precios_data else [],
                "datos_ejemplo": [],
                "total_productos": 0
            },
            "rentabilidades": {
                "cargado": rentabilidades_data is not None,
                "hojas": list(rentabilidades_data.keys()) if rentabilidades_data else [],
                "datos_ejemplo": [],
                "total_reglas": 0
            }
        }
        
        # Mostrar primeros 3 productos como ejemplo
        if precios_data and len(precios_data) > 0:
            primera_hoja = list(precios_data.keys())[0]
            productos = precios_data[primera_hoja]
            resultado["precios"]["total_productos"] = len(productos)
            
            # Mostrar hasta 3 productos con manejo de errores
            for i in range(min(3, len(productos))):
                try:
                    producto = productos[i]
                    # Limpiar datos para evitar errores de serialización
                    producto_limpio = {}
                    for key, value in producto.items():
                        if isinstance(value, (str, int, float, bool)):
                            producto_limpio[str(key)] = str(value)
                        else:
                            producto_limpio[str(key)] = str(value) if value is not None else ""
                    resultado["precios"]["datos_ejemplo"].append(producto_limpio)
                except Exception as e:
                    logger.error(f"Error procesando producto {i}: {e}")
                    resultado["precios"]["datos_ejemplo"].append({"error": f"Error en producto {i}: {str(e)}"})
        
        # Mostrar primeras 3 reglas como ejemplo
        if rentabilidades_data and len(rentabilidades_data) > 0:
            primera_hoja = list(rentabilidades_data.keys())[0]
            reglas = rentabilidades_data[primera_hoja]
            resultado["rentabilidades"]["total_reglas"] = len(reglas)
            
            # Mostrar hasta 3 reglas con manejo de errores
            for i in range(min(3, len(reglas))):
                try:
                    regla = reglas[i]
                    # Limpiar datos para evitar errores de serialización
                    regla_limpia = {}
                    for key, value in regla.items():
                        if isinstance(value, (str, int, float, bool)):
                            regla_limpia[str(key)] = str(value)
                        else:
                            regla_limpia[str(key)] = str(value) if value is not None else ""
                    resultado["rentabilidades"]["datos_ejemplo"].append(regla_limpia)
                except Exception as e:
                    logger.error(f"Error procesando regla {i}: {e}")
                    resultado["rentabilidades"]["datos_ejemplo"].append({"error": f"Error en regla {i}: {str(e)}"})
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en diagnóstico detallado: {str(e)}")
        return {
            "error": str(e),
            "precios": {"cargado": False, "datos_ejemplo": []},
            "rentabilidades": {"cargado": False, "datos_ejemplo": []}
        }

@app.get("/api/estado-rentabilidad")
async def obtener_estado_rentabilidad():
    """Obtiene el estado de las rentabilidades cargadas"""
    try:
        if not MODULES_AVAILABLE:
            raise HTTPException(status_code=503, detail="Módulo de rentabilidad no disponible")
        
        archivo_cargado = rentabilidades_filename
        resumen = {} # No hay un resumen directo en memoria, solo el archivo
        
        return {
            "archivo_cargado": archivo_cargado,
            "total_reglas": 0, # No hay reglas en memoria
            "resumen": resumen
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de rentabilidad: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@app.get("/api/verificar-rentabilidades")
async def verificar_rentabilidades():
    """Endpoint para verificar si hay rentabilidades cargadas"""
    global rentabilidades_data, rentabilidades_filename
    
    if rentabilidades_data is None:
        return {
            "status": "no_cargado",
            "mensaje": "No hay archivo de rentabilidades cargado",
            "archivo": None,
            "hojas": []
        }
    
    return {
        "status": "cargado",
        "mensaje": f"Archivo de rentabilidades cargado: {rentabilidades_filename}",
        "archivo": rentabilidades_filename,
        "hojas": list(rentabilidades_data.keys()),
        "total_hojas": len(rentabilidades_data)
    }

@app.get("/api/estado-archivos")
async def obtener_estado_archivos():
    """Obtiene el estado actual de los archivos cargados"""
    global precios_data, rentabilidades_data
    
    try:
        logger.info(f"🔍 Verificando estado de archivos:")
        logger.info(f"  - precios_data: {precios_data is not None} ({type(precios_data)})")
        logger.info(f"  - rentabilidades_data: {rentabilidades_data is not None} ({type(rentabilidades_data)})")
        
        estado = {
            "precios_cargados": precios_data is not None,
            "rentabilidades_cargadas": rentabilidades_data is not None,
            "listo_para_procesar": precios_data is not None and rentabilidades_data is not None
        }
        
        logger.info(f"✅ Estado retornado: {estado}")
        return estado
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de archivos: {e}")
        return {
            "precios_cargados": False,
            "rentabilidades_cargadas": False,
            "listo_para_procesar": False
        }

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
            productos_filtrados = [p for p in productos_filtrados if p.get('marca') == marca]
        
        if con_alertas is not None:
            if con_alertas:
                productos_filtrados = [p for p in productos_filtrados if p.get('alertas')]
            else:
                productos_filtrados = [p for p in productos_filtrados if not p.get('alertas')]
        
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
        producto = next((p for p in productos_actuales if p.get('codigo') == codigo_producto), None)
        
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {codigo_producto} no encontrado")
        
        # Generar sugerencias
        sugerencias = pricing_logic.generar_sugerencias_precio(producto)
        
        return {
            "producto": {
                "codigo": producto.get('codigo'),
                "nombre": producto.get('nombre'),
                "precio_actual": producto.get('precio_final'),
                "margen_actual": producto.get('margen')
            },
            "sugerencias": sugerencias
        }
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias para {codigo_producto}: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}") 

@app.post("/calcular-precios-con-rentabilidad")
async def calcular_precios_con_rentabilidad():
    """Endpoint para calcular precios con el nuevo flujo simplificado"""
    global precios_data, rentabilidades_data
    
    try:
        logger.info("🚀 Iniciando proceso de pricing simplificado...")
        
        # Verificar que tengamos ambos archivos
        logger.info(f"🔍 Verificando archivos antes de procesar:")
        logger.info(f"  - precios_data: {precios_data is not None}")
        logger.info(f"  - rentabilidades_data: {rentabilidades_data is not None}")
        
        if precios_data is None:
            logger.warning("❌ No hay archivo de precios cargado")
            return {
                "status": "error",
                "mensaje": "❌ No hay archivo de precios cargado. Carga primero la lista de precios."
            }
        
        if rentabilidades_data is None:
            logger.warning("❌ No hay archivo de rentabilidades cargado")
            return {
                "status": "error", 
                "mensaje": "❌ No hay archivo de rentabilidades cargado. Carga primero las reglas de rentabilidad."
            }
        
        # Buscar hojas disponibles
        hojas_precios = list(precios_data.keys())
        hojas_rentabilidad = list(rentabilidades_data.keys())
        
        # Buscar coincidencias por nombre (priorizar Moura)
        hoja_precios = None
        hoja_rentabilidad = None
        
        # Buscar hoja "Moura" en rentabilidades
        for hoja_rent in hojas_rentabilidad:
            if 'moura' in hoja_rent.lower():
                hoja_rentabilidad = hoja_rent
                break
        
        # Si no hay hoja Moura en rentabilidades, usar la primera
        if not hoja_rentabilidad:
            hoja_rentabilidad = hojas_rentabilidad[0] if hojas_rentabilidad else None
        
        # Buscar cualquier hoja de precios que contenga productos Moura
        # (códigos que empiecen con M)
        for hoja_precio in hojas_precios:
            precios_hoja_temp = precios_data[hoja_precio]
            if precios_hoja_temp:
                # Verificar si hay productos con códigos que empiecen con M (Moura)
                for producto in precios_hoja_temp[:5]:  # Revisar solo los primeros 5
                    codigo = str(producto.get('CODIGO BATERIAS', '')).strip()
                    if codigo and codigo.startswith('M') and len(codigo) > 1:
                        hoja_precios = hoja_precio
                        break
                if hoja_precios:
                    break
        
        # Si no se encuentra hoja con productos Moura, usar la primera
        if not hoja_precios:
            hoja_precios = hojas_precios[0] if hojas_precios else None
        
        if not hoja_precios:
            return {
                "status": "error",
                "mensaje": "No se encontraron hojas en el archivo de precios"
            }
        
        if not hoja_rentabilidad:
            return {
                "status": "error", 
                "mensaje": "No se encontraron hojas en el archivo de rentabilidades"
            }
        
        logger.info(f"✅ Procesando: Precios en '{hoja_precios}' y Rentabilidad en '{hoja_rentabilidad}'")
        
        # Verificar que realmente estamos usando la hoja Moura
        if 'moura' not in hoja_rentabilidad.lower():
            logger.warning(f"⚠️ ADVERTENCIA: No se está usando la hoja Moura. Hoja seleccionada: {hoja_rentabilidad}")
        
        # Obtener datos
        precios_hoja = precios_data[hoja_precios]
        rentabilidad_hoja = rentabilidades_data[hoja_rentabilidad]
        
        logger.info(f"Productos en precios: {len(precios_hoja)}")
        logger.info(f"Reglas en rentabilidad: {len(rentabilidad_hoja)}")
        logger.info(f"Primer producto: {precios_hoja[0] if precios_hoja else 'No hay productos'}")
        logger.info(f"Primera regla: {rentabilidad_hoja[0] if rentabilidad_hoja else 'No hay reglas'}")
        
        # Logging detallado de la estructura de datos
        if precios_hoja:
            logger.info(f"Claves del primer producto: {list(precios_hoja[0].keys())}")
            logger.info(f"Valores del primer producto: {precios_hoja[0]}")
        if rentabilidad_hoja:
            logger.info(f"Claves de la primera regla: {list(rentabilidad_hoja[0].keys())}")
            logger.info(f"Valores de la primera regla: {rentabilidad_hoja[0]}")
            
            # Verificar si las reglas tienen códigos de productos Moura
            logger.info(f"🔍 Verificando reglas de rentabilidad para productos Moura:")
            for i, regla in enumerate(rentabilidad_hoja[:5]):
                # Buscar cualquier campo que pueda contener códigos de productos
                for key, value in regla.items():
                    if str(value) != 'nan' and value is not None:
                        if isinstance(value, str) and value.startswith('M') and len(value) > 1:
                            logger.info(f"  ✅ Regla {i+1}: Encontrado código Moura '{value}' en columna '{key}'")
                        elif key.lower() in ['codigo', 'modelo', 'producto', 'articulo']:
                            logger.info(f"  📋 Regla {i+1}: Columna '{key}' = '{value}'")
        
        # Convertir datos a productos
        productos = []
        logger.info(f"🔄 Convirtiendo {len(precios_hoja)} productos...")
        for i, item in enumerate(precios_hoja):
            try:
                logger.info(f"  Procesando producto {i+1}: {item}")
                # Extraer datos del archivo de precios
                codigo = str(item.get('CODIGO BATERIAS', '')).strip()
                nombre = str(item.get('DENOMINACION COMERCIAL / ALGUNAS APLICACIONES (4)', '')).strip()
                precio_lista = item.get('Precio de Lista', 0)
                
                # Solo procesar productos válidos (con código y precio)
                if codigo and codigo != 'nan' and precio_lista and precio_lista != 'nan':
                    producto = Producto(
                        codigo=codigo,
                        nombre=nombre if nombre != 'nan' else f'Producto {codigo}',
                        marca=Marca.MOURA,  # Por ahora solo Moura
                        canal=Canal.MINORISTA,  # Por defecto minorista
                        categoria='Baterías',
                        precio_base=float(precio_lista),
                        precio_final=0,
                        margen=0,
                        markup_aplicado=0,
                        estado_rentabilidad='',
                        margen_minimo_esperado=0,
                        margen_optimo_esperado=0,
                        alertas=[],
                        sugerencias_openai=''
                    )
                    productos.append(producto)
                    logger.info(f"  ✅ Producto {i+1} convertido: {codigo} - ${precio_lista}")
                else:
                    logger.info(f"  ⚠️ Producto {i+1} saltado: código='{codigo}', precio='{precio_lista}'")
                    continue
            except Exception as e:
                logger.error(f"Error convirtiendo producto {i+1}: {e}")
                continue
        
        logger.info(f"✅ Total productos convertidos: {len(productos)}")
        
        # Procesar productos directamente con los datos en memoria
        logger.info("🔄 Procesando productos con datos en memoria...")
        logger.info(f"Total productos a procesar: {len(productos)}")
        
        productos_procesados = []
        pasos_completados = []
        
        for producto in productos:
            try:
                # Buscar regla de rentabilidad correspondiente
                regla_encontrada = None
                
                # Buscar por código de producto
                for regla in rentabilidad_hoja:
                    if 'codigo' in regla:
                        if str(regla['codigo']).strip() == str(producto.codigo).strip():
                            regla_encontrada = regla
                            break
                
                # Si no se encuentra, usar primera regla como default
                if not regla_encontrada and len(rentabilidad_hoja) > 0:
                    regla_encontrada = rentabilidad_hoja[0]
                
                # Calcular precio con markup
                precio_base = producto.precio_base
                markup = float(regla_encontrada.get('markup', 20)) if regla_encontrada else 20
                
                # Aplicar markup
                precio_con_markup = precio_base * (1 + markup / 100)
                
                # Redondear a múltiplos de 100
                precio_final = round(precio_con_markup / 100) * 100
                
                # Calcular margen
                margen = ((precio_final - precio_base) / precio_final) * 100
                
                # Actualizar producto
                producto.precio_final = precio_final
                producto.margen = margen
                producto.markup_aplicado = markup
                
                # Verificar rentabilidad
                margen_minimo = float(regla_encontrada.get('margen_minimo', 10)) if regla_encontrada else 10
                margen_optimo = float(regla_encontrada.get('margen_optimo', 25)) if regla_encontrada else 25
                
                if margen < margen_minimo:
                    producto.alertas.append(f"Margen bajo: {margen:.1f}% < {margen_minimo}%")
                    producto.estado_rentabilidad = "CRÍTICO"
                elif margen < margen_optimo:
                    producto.alertas.append(f"Margen subóptimo: {margen:.1f}% < {margen_optimo}%")
                    producto.estado_rentabilidad = "ADVERTENCIA"
                else:
                    producto.estado_rentabilidad = "ÓPTIMO"
                
                productos_procesados.append(producto)
                
            except Exception as e:
                logger.error(f"Error procesando producto {producto.codigo}: {e}")
                continue
        
        # Actualizar datos globales
        global productos_actuales
        productos_actuales = productos_procesados
        
        pasos_completados = [
            "✅ Archivos cargados",
            "✅ Productos convertidos",
            "✅ Reglas de rentabilidad aplicadas", 
            "✅ Precios calculados",
            "✅ Validación completada"
        ]
        
        logger.info(f"✅ Proceso completado exitosamente - {len(productos_procesados)} productos")
        logger.info(f"📊 Resumen: {len(productos_procesados)} productos procesados de {len(productos)} originales")
        
        # Convertir productos a diccionarios para JSON
        productos_json = []
        for producto in productos_procesados:
            productos_json.append({
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "precio_base": producto.precio_base,
                "precio_final": producto.precio_final,
                "margen": producto.margen,
                "estado": producto.estado_rentabilidad,
                "alertas": producto.alertas,
                "markup_aplicado": producto.markup_aplicado
            })
        
        return {
            "status": "success",
            "mensaje": f"Proceso completado exitosamente para {len(productos_procesados)} productos",
            "productos": len(productos_procesados),
            "productos_detalle": productos_json,  # Lista completa de productos
            "pasos_completados": pasos_completados,
            "resumen": {
                "total_productos": len(productos_procesados),
                "con_alertas": len([p for p in productos_procesados if p.alertas]),
                "margen_promedio": sum([p.margen for p in productos_procesados]) / len(productos_procesados) if productos_procesados else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculando precios: {str(e)}")
        return {
            "status": "error",
            "mensaje": f"Error: {str(e)}"
        } 

@app.get("/api/logs")
async def obtener_logs():
    """Endpoint para obtener logs del servidor"""
    try:
        # Capturar logs recientes
        logs = []
        
        # Verificar estado de archivos
        logs.append(f"📁 Estado de archivos:")
        logs.append(f"  - precios_data: {'✅ Cargado' if precios_data else '❌ No cargado'}")
        logs.append(f"  - rentabilidades_data: {'✅ Cargado' if rentabilidades_data else '❌ No cargado'}")
        
        if precios_data:
            logs.append(f"  - Hojas de precios: {list(precios_data.keys())}")
            for hoja, datos in precios_data.items():
                logs.append(f"    - {hoja}: {len(datos)} productos")
                if datos:
                    logs.append(f"      Primer producto: {datos[0]}")
        
        if rentabilidades_data:
            logs.append(f"  - Hojas de rentabilidad: {list(rentabilidades_data.keys())}")
            for hoja, datos in rentabilidades_data.items():
                logs.append(f"    - {hoja}: {len(datos)} reglas")
                if datos:
                    logs.append(f"      Primera regla: {datos[0]}")
        
        logs.append(f"📊 Productos actuales: {len(productos_actuales)}")
        
        return {
            "status": "success",
            "logs": logs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "mensaje": f"Error obteniendo logs: {str(e)}"
        } 

@app.get("/api/listar-archivos")
async def listar_archivos():
    """Lista todos los archivos disponibles en el directorio de trabajo"""
    try:
        # Obtener directorio actual
        current_dir = os.getcwd()
        
        # Listar todos los archivos
        archivos = []
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, current_dir)
                
                # Obtener información del archivo
                try:
                    file_size = os.path.getsize(file_path)
                    archivos.append({
                        "nombre": file,
                        "ruta": relative_path,
                        "tamaño": file_size,
                        "tamaño_mb": round(file_size / (1024 * 1024), 2)
                    })
                except:
                    archivos.append({
                        "nombre": file,
                        "ruta": relative_path,
                        "tamaño": "error",
                        "tamaño_mb": "error"
                    })
        
        # Filtrar solo archivos Excel
        archivos_excel = [f for f in archivos if f["nombre"].lower().endswith('.xlsx')]
        
        return {
            "directorio_actual": current_dir,
            "total_archivos": len(archivos),
            "archivos_excel": archivos_excel,
            "todos_los_archivos": archivos[:20]  # Solo los primeros 20 para no saturar
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "directorio_actual": os.getcwd() if os.getcwd() else "No disponible"
        }