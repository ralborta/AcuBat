from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class Canal(str, Enum):
    MINORISTA = "minorista"
    MAYORISTA = "mayorista"
    DISTRIBUIDOR = "distribuidor"

class Marca(str, Enum):
    MOURA = "moura"
    ACUBAT = "acubat"
    LUBECK = "lubeck"
    SOLAR = "solar"

class TipoAlerta(str, Enum):
    MARGEN_BAJO = "margen_bajo"
    SIN_CODIGO = "sin_codigo"
    PRECIO_LIBERADO = "precio_liberado"
    SIN_MARKUP = "sin_markup"
    PRECIO_FUERA_RANGO = "precio_fuera_rango"

class Producto(BaseModel):
    codigo: str
    nombre: str
    capacidad: Optional[str] = None
    marca: Marca
    canal: Canal
    categoria: str = "General"
    precio_base: float
    precio_final: float
    stock: int = 0
    margen: float = 0.0
    markup_aplicado: Optional[float] = None  # Porcentaje de markup aplicado
    alertas: List[TipoAlerta] = []
    sugerencias_ai: Optional[str] = None
    sugerencias_openai: Optional[str] = None  # Campo para compatibilidad
    estado_rentabilidad: str = "Sin referencia"  # OK, Revisar, Ajustar, Sin referencia
    margen_minimo_esperado: float = 0.0
    margen_optimo_esperado: float = 0.0
    fecha_procesamiento: datetime = datetime.now()
    origen_archivo: Optional[str] = None  # Archivo de origen

class ProductoResponse(BaseModel):
    productos: List[Producto]
    total_productos: int
    productos_con_alertas: int
    resumen_marcas: dict
    resumen_canales: dict

class Alerta(BaseModel):
    tipo: TipoAlerta
    mensaje: str
    severidad: str  # "baja", "media", "alta"
    producto_codigo: str
    sugerencia: Optional[str] = None

class ConfiguracionMarkup(BaseModel):
    canal: Canal
    porcentaje: float
    aplicar_redondeo: bool = False

class ProcesamientoRequest(BaseModel):
    archivo_nombre: str
    aplicar_markup: bool = True
    usar_openai: bool = False 