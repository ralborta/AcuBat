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
    precio_base: float
    precio_final: float
    margen: float
    alertas: List[TipoAlerta] = []
    sugerencias_ai: Optional[str] = None
    fecha_procesamiento: datetime = datetime.now()

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