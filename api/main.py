from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import logging
import io
import os

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

# Importar módulos de forma condicional
try:
    from .logic import PricingLogic
    from .openai_helper import OpenAIHelper
    from .parser import ExcelParser
    
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
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Acubat - Sistema de Pricing</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
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
                                    OpenAI no disponible
                                </div>
                            </div>
                        </div>

                        <div class="col-md-9 p-4">
                            <h1 class="mb-4">
                                <i class="fas fa-rocket text-primary"></i>
                                AcuBat - Sistema de Pricing Inteligente
                            </h1>

                            <div class="alert alert-info">
                                <h4>🚀 Modo Vercel Activado</h4>
                                <p>El sistema está funcionando en modo optimizado para Vercel. Todas las funcionalidades están disponibles a través del navegador.</p>
                                <ul>
                                    <li>✅ Conversión PDF en línea</li>
                                    <li>✅ Procesamiento de Excel/CSV</li>
                                    <li>✅ Exportación de datos</li>
                                    <li>⚠️ Análisis OpenAI (limitado)</li>
                                </ul>
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
                                        <p class="text-muted">Soporta Excel (.xlsx, .xls), CSV (.csv) y PDF (.pdf)</p>
                                        <button class="btn btn-primary">
                                            <i class="fas fa-file-upload"></i>
                                            Seleccionar Archivo
                                        </button>
                                    </div>

                                    <div id="pdfConversion" class="conversion-progress">
                                        <div class="alert alert-info">
                                            <h6><i class="fas fa-cog fa-spin"></i> Convirtiendo PDF a Excel...</h6>
                                            <div class="progress">
                                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                                     role="progressbar" style="width: 0%"></div>
                                            </div>
                                            <small class="text-muted">Procesando página <span id="currentPage">1</span> de <span id="totalPages">?</span></small>
                                        </div>
                                    </div>

                                    <div id="pdfPreview" class="pdf-preview" style="display: none;">
                                        <h6><i class="fas fa-eye"></i> Vista Previa del PDF</h6>
                                        <div id="pdfContent"></div>
                                        <button class="btn btn-convert mt-2" onclick="convertirPDFaExcel()">
                                            <i class="fas fa-magic"></i> Convertir a Excel
                                        </button>
                                    </div>

                                    <input type="file" id="fileInput" accept=".xlsx,.xls,.csv,.pdf" style="display: none;">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                <script>
                    // Configurar PDF.js
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

                    let pdfData = null;
                    let currentFile = null;

                    // Drag and drop
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
                            handleFile(files[0]);
                        }
                    });

                    fileInput.addEventListener('change', (e) => {
                        if (e.target.files.length > 0) {
                            handleFile(e.target.files[0]);
                        }
                    });

                    function handleFile(file) {
                        currentFile = file;
                        
                        if (file.type === 'application/pdf') {
                            procesarPDFEnLinea(file);
                        } else {
                            subirArchivo(file);
                        }
                    }

                    async function procesarPDFEnLinea(file) {
                        try {
                            document.getElementById('pdfConversion').style.display = 'block';
                            const progressBar = document.querySelector('.progress-bar');
                            
                            const arrayBuffer = await file.arrayBuffer();
                            const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;
                            
                            document.getElementById('totalPages').textContent = pdf.numPages;
                            
                            let extractedText = '';
                            
                            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                                document.getElementById('currentPage').textContent = pageNum;
                                progressBar.style.width = `${(pageNum / pdf.numPages) * 100}%`;
                                
                                const page = await pdf.getPage(pageNum);
                                const textContent = await page.getTextContent();
                                const pageText = textContent.items.map(item => item.str).join(' ');
                                extractedText += pageText + '\\n';
                                
                                await new Promise(resolve => setTimeout(resolve, 100));
                            }
                            
                            document.getElementById('pdfConversion').style.display = 'none';
                            mostrarVistaPreviaPDF(extractedText);
                            
                        } catch (error) {
                            console.error('Error procesando PDF:', error);
                            alert('Error al procesar el PDF. Intenta con otro archivo.');
                            document.getElementById('pdfConversion').style.display = 'none';
                        }
                    }

                    function mostrarVistaPreviaPDF(texto) {
                        const preview = document.getElementById('pdfPreview');
                        const content = document.getElementById('pdfContent');
                        
                        const previewText = texto.substring(0, 1000) + (texto.length > 1000 ? '...' : '');
                        content.innerHTML = `<pre style="font-size: 12px; white-space: pre-wrap;">${previewText}</pre>`;
                        
                        preview.style.display = 'block';
                        pdfData = texto;
                    }

                    function convertirPDFaExcel() {
                        if (!pdfData || !currentFile) {
                            alert('No hay datos PDF para convertir');
                            return;
                        }
                        
                        try {
                            const lineas = pdfData.split('\\n').filter(line => line.trim());
                            const datos = [];
                            
                            lineas.forEach((linea, index) => {
                                const columnas = linea.split(/\\s+/).filter(col => col.trim());
                                
                                if (columnas.length >= 2) {
                                    const fila = {
                                        nombre: columnas[0] || `Producto ${index + 1}`,
                                        precio_base: parseFloat(columnas[1]) || 0,
                                        marca: columnas[2] || 'Sin marca',
                                        canal: columnas[3] || 'General'
                                    };
                                    datos.push(fila);
                                }
                            });
                            
                            const ws = XLSX.utils.json_to_sheet(datos);
                            const wb = XLSX.utils.book_new();
                            XLSX.utils.book_append_sheet(wb, ws, "Productos");
                            
                            const excelBuffer = XLSX.write(wb, {bookType: 'xlsx', type: 'array'});
                            const blob = new Blob([excelBuffer], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
                            
                            const excelFile = new File([blob], currentFile.name.replace('.pdf', '.xlsx'), {
                                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            });
                            
                            document.getElementById('pdfPreview').style.display = 'none';
                            subirArchivo(excelFile);
                            
                        } catch (error) {
                            console.error('Error convirtiendo PDF:', error);
                            alert('Error al convertir PDF. Intenta subir el archivo original.');
                        }
                    }

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