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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con panel de productos"""
    try:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Acubat - Sistema de Pricing</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
            <style>
                .upload-area {
                    border: 2px dashed #007bff;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    background: #f8f9fa;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }
                .upload-area:hover {
                    border-color: #0056b3;
                    background: #e9ecef;
                }
                .upload-area.dragover {
                    border-color: #28a745;
                    background: #d4edda;
                }
                .conversion-progress {
                    display: none;
                    margin-top: 20px;
                }
                .pdf-preview {
                    max-height: 300px;
                    overflow-y: auto;
                    border: 1px solid #ddd;
                    padding: 10px;
                    background: white;
                    margin-top: 10px;
                }
                .stats-card {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .btn-convert {
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    transition: all 0.3s ease;
                }
                .btn-convert:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-3 bg-light p-4 min-vh-100">
                        <h4 class="mb-4">
                            <i class="fas fa-chart-line text-primary"></i>
                            Rating: Calificación
                        </h4>
                        
                        <div class="stats-card">
                            <h2 class="display-4 text-center" id="totalProductos">0</h2>
                            <p class="text-center mb-0">Productos Cargados</p>
                        </div>

                        <div class="stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                            <h2 class="display-4 text-center" id="totalAlertas">0</h2>
                            <p class="text-center mb-0">Con Alertas</p>
                        </div>

                        <div class="mt-4">
                            <h5><i class="fas fa-filter text-info"></i> Filtros</h5>
                            <select id="filtroCanal" class="form-select mb-2">
                                <option value="">Todos los canales</option>
                            </select>
                            
                            <select id="filtroMarca" class="form-select mb-2">
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
                            
                            <div class="alert alert-info alert-sm">
                                <i class="fas fa-info-circle"></i>
                                Modo Vercel - Conversión en línea
                            </div>
                        </div>
                    </div>

                    <div class="col-md-9 p-4">
                        <h1 class="mb-4">
                            <i class="fas fa-rocket text-primary"></i>
                            AcuBat - Sistema de Pricing Inteligente
                        </h1>

                        <div class="alert alert-success">
                            <h4>🚀 Sistema Funcionando en Vercel</h4>
                            <p>El sistema está funcionando en modo optimizado para Vercel con conversión PDF en línea.</p>
                            <ul>
                                <li>✅ Conversión PDF en línea (sin servidor)</li>
                                <li>✅ Procesamiento de Excel/CSV</li>
                                <li>✅ Exportación de datos</li>
                                <li>✅ Filtros y análisis</li>
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

                        <div class="mt-4" id="resultadosSection" style="display: none;">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4><i class="fas fa-list text-success"></i> Productos Procesados</h4>
                                <div>
                                    <button class="btn btn-outline-primary btn-sm" onclick="limpiarProductos()">
                                        <i class="fas fa-trash"></i> Limpiar
                                    </button>
                                </div>
                            </div>

                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Producto</th>
                                            <th>Marca</th>
                                            <th>Canal</th>
                                            <th>Precio Base</th>
                                            <th>Precio Final</th>
                                            <th>Margen</th>
                                            <th>Estado</th>
                                        </tr>
                                    </thead>
                                    <tbody id="productosTable">
                                    </tbody>
                                </table>
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
                let productosActuales = [];

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
                        procesarArchivoEnLinea(file);
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
                        
                        procesarProductos(datos);
                        document.getElementById('pdfPreview').style.display = 'none';
                        
                    } catch (error) {
                        console.error('Error convirtiendo PDF:', error);
                        alert('Error al convertir PDF. Intenta subir el archivo original.');
                    }
                }

                async function procesarArchivoEnLinea(file) {
                    try {
                        if (file.name.endsWith('.csv')) {
                            const text = await file.text();
                            const lineas = text.split('\\n');
                            const headers = lineas[0].split(',').map(h => h.trim());
                            const datos = [];
                            
                            for (let i = 1; i < lineas.length; i++) {
                                if (lineas[i].trim()) {
                                    const valores = lineas[i].split(',').map(v => v.trim());
                                    const fila = {};
                                    headers.forEach((header, index) => {
                                        fila[header] = valores[index] || '';
                                    });
                                    datos.push(fila);
                                }
                            }
                            
                            procesarProductos(datos);
                        } else {
                            // Para Excel, usar XLSX.js
                            const arrayBuffer = await file.arrayBuffer();
                            const workbook = XLSX.read(arrayBuffer, {type: 'array'});
                            const sheetName = workbook.SheetNames[0];
                            const worksheet = workbook.Sheets[sheetName];
                            const datos = XLSX.utils.sheet_to_json(worksheet);
                            
                            procesarProductos(datos);
                        }
                    } catch (error) {
                        console.error('Error procesando archivo:', error);
                        alert('Error al procesar el archivo. Verifica el formato.');
                    }
                }

                function procesarProductos(datos) {
                    // Simular procesamiento de pricing
                    productosActuales = datos.map((item, index) => {
                        const precioBase = parseFloat(item.precio_base || item.precio || item.Precio || 0);
                        const markup = 0.15; // 15% markup
                        const precioFinal = precioBase * (1 + markup);
                        const margen = ((precioFinal - precioBase) / precioFinal) * 100;
                        
                        return {
                            nombre: item.nombre || item.producto || item.Producto || `Producto ${index + 1}`,
                            marca: item.marca || item.Marca || 'Sin marca',
                            canal: item.canal || item.Canal || 'General',
                            precio_base: precioBase,
                            precio_final: precioFinal,
                            margen: margen,
                            alertas: margen < 10 ? ['Margen bajo'] : []
                        };
                    });
                    
                    actualizarInterfaz();
                }

                function actualizarInterfaz() {
                    // Actualizar contadores
                    document.getElementById('totalProductos').textContent = productosActuales.length;
                    const alertas = productosActuales.filter(p => p.alertas.length > 0).length;
                    document.getElementById('totalAlertas').textContent = alertas;
                    
                    // Actualizar tabla
                    const tbody = document.getElementById('productosTable');
                    tbody.innerHTML = '';
                    
                    productosActuales.forEach(producto => {
                        const row = document.createElement('tr');
                        row.className = 'producto-row';
                        row.dataset.canal = producto.canal;
                        row.dataset.marca = producto.marca;
                        row.dataset.alertas = producto.alertas.length > 0 ? 'true' : 'false';
                        
                        row.innerHTML = `
                            <td>${producto.nombre}</td>
                            <td>${producto.marca}</td>
                            <td>${producto.canal}</td>
                            <td>$${producto.precio_base.toFixed(2)}</td>
                            <td>$${producto.precio_final.toFixed(2)}</td>
                            <td>${producto.margen.toFixed(1)}%</td>
                            <td>
                                ${producto.alertas.length > 0 ? 
                                    '<span class="badge bg-warning"><i class="fas fa-exclamation-triangle"></i> Alerta</span>' :
                                    '<span class="badge bg-success"><i class="fas fa-check"></i> OK</span>'
                                }
                            </td>
                        `;
                        
                        tbody.appendChild(row);
                    });
                    
                    // Mostrar sección de resultados
                    document.getElementById('resultadosSection').style.display = 'block';
                    
                    // Actualizar filtros
                    actualizarFiltros();
                }

                function actualizarFiltros() {
                    const canales = [...new Set(productosActuales.map(p => p.canal))];
                    const marcas = [...new Set(productosActuales.map(p => p.marca))];
                    
                    const filtroCanal = document.getElementById('filtroCanal');
                    const filtroMarca = document.getElementById('filtroMarca');
                    
                    filtroCanal.innerHTML = '<option value="">Todos los canales</option>';
                    filtroMarca.innerHTML = '<option value="">Todas las marcas</option>';
                    
                    canales.forEach(canal => {
                        filtroCanal.innerHTML += `<option value="${canal}">${canal}</option>`;
                    });
                    
                    marcas.forEach(marca => {
                        filtroMarca.innerHTML += `<option value="${marca}">${marca}</option>`;
                    });
                }

                // Filtros
                document.getElementById('filtroCanal').addEventListener('change', aplicarFiltros);
                document.getElementById('filtroMarca').addEventListener('change', aplicarFiltros);
                document.getElementById('filtroAlertas').addEventListener('change', aplicarFiltros);

                function aplicarFiltros() {
                    const canal = document.getElementById('filtroCanal').value;
                    const marca = document.getElementById('filtroMarca').value;
                    const alertas = document.getElementById('filtroAlertas').checked;
                    
                    const filas = document.querySelectorAll('.producto-row');
                    
                    filas.forEach(fila => {
                        let mostrar = true;
                        
                        if (canal && fila.dataset.canal !== canal) mostrar = false;
                        if (marca && fila.dataset.marca !== marca) mostrar = false;
                        if (alertas && fila.dataset.alertas !== 'true') mostrar = false;
                        
                        fila.style.display = mostrar ? '' : 'none';
                    });
                }

                function exportarCSV() {
                    if (productosActuales.length === 0) {
                        alert('No hay productos para exportar');
                        return;
                    }
                    
                    const headers = ['Producto', 'Marca', 'Canal', 'Precio Base', 'Precio Final', 'Margen', 'Alertas'];
                    const csvContent = [
                        headers.join(','),
                        ...productosActuales.map(p => [
                            p.nombre,
                            p.marca,
                            p.canal,
                            p.precio_base,
                            p.precio_final,
                            p.margen.toFixed(1),
                            p.alertas.join(';')
                        ].join(','))
                    ].join('\\n');
                    
                    const blob = new Blob([csvContent], {type: 'text/csv'});
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'productos_pricing.csv';
                    a.click();
                    window.URL.revokeObjectURL(url);
                }

                function limpiarProductos() {
                    if (confirm('¿Estás seguro de que quieres limpiar todos los productos?')) {
                        productosActuales = [];
                        document.getElementById('resultadosSection').style.display = 'none';
                        document.getElementById('totalProductos').textContent = '0';
                        document.getElementById('totalAlertas').textContent = '0';
                    }
                }
            </script>
        </body>
        </html>
        """)

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
        "message": "Backend Acubat funcionando en modo Vercel",
        "is_vercel": IS_VERCEL,
        "productos_cargados": len(productos_actuales) if productos_actuales else 0
    }

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    return {
        "status": "ok",
        "mensaje": "Aplicación funcionando correctamente en modo Vercel",
        "productos_cargados": len(productos_actuales) if productos_actuales else 0,
        "is_vercel": IS_VERCEL
    } 