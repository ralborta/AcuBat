import os
import openai
from typing import List, Optional, Dict
from .models import Producto, TipoAlerta
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIHelper:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            self.disponible = True
        else:
            logger.warning("OpenAI API key no encontrada. Las funciones de IA estarán deshabilitadas.")
            self.disponible = False

    def analizar_producto(self, producto: Producto) -> Optional[str]:
        """Analiza un producto usando OpenAI y retorna sugerencias"""
        if not self.disponible:
            return None
        
        try:
            prompt = self._crear_prompt_analisis(producto)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de productos y precios. Analiza el producto y proporciona sugerencias breves y útiles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error al analizar producto con OpenAI: {e}")
            return None

    def analizar_lista_productos(self, productos: List[Producto]) -> Dict[str, str]:
        """Analiza una lista de productos y retorna sugerencias para cada uno"""
        if not self.disponible:
            return {}
        
        sugerencias = {}
        
        for producto in productos:
            sugerencia = self.analizar_producto(producto)
            if sugerencia:
                sugerencias[producto.codigo] = sugerencia
        
        return sugerencias

    def detectar_anomalias(self, productos: List[Producto]) -> List[Dict]:
        """Detecta anomalías en la lista de productos"""
        if not self.disponible:
            return []
        
        try:
            # Crear resumen de productos para análisis
            resumen = self._crear_resumen_productos(productos)
            
            prompt = f"""
            Analiza la siguiente lista de productos y detecta anomalías o problemas:

            {resumen}

            Identifica:
            1. Productos con precios inusuales
            2. Márgenes inconsistentes
            3. Productos mal clasificados
            4. Posibles errores en códigos o nombres

            Responde en formato JSON con la estructura:
            [
                {{
                    "tipo": "precio_inusual|margen_inconsistente|clasificacion_erronea|error_datos",
                    "producto_codigo": "CODIGO",
                    "descripcion": "Descripción del problema",
                    "severidad": "baja|media|alta",
                    "sugerencia": "Sugerencia de corrección"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en detección de anomalías en datos de productos. Responde solo en formato JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            import json
            try:
                anomalias = json.loads(response.choices[0].message.content)
                return anomalias
            except json.JSONDecodeError:
                logger.error("Error al parsear respuesta JSON de OpenAI")
                return []
                
        except Exception as e:
            logger.error(f"Error al detectar anomalías: {e}")
            return []

    def sugerir_markup(self, producto: Producto, contexto_mercado: str = "") -> Optional[Dict]:
        """Sugiere markup óptimo para un producto"""
        if not self.disponible:
            return None
        
        try:
            prompt = f"""
            Analiza el siguiente producto y sugiere un markup óptimo:

            Producto: {producto.nombre}
            Código: {producto.codigo}
            Marca: {producto.marca.value}
            Canal: {producto.canal.value}
            Precio base: ${producto.precio_base:.2f}
            Precio actual: ${producto.precio_final:.2f}
            Margen actual: {producto.margen:.1f}%

            Contexto del mercado: {contexto_mercado}

            Sugiere:
            1. Markup recomendado (%)
            2. Precio final sugerido
            3. Justificación breve

            Responde en formato JSON:
            {{
                "markup_recomendado": 35.0,
                "precio_sugerido": 135.00,
                "justificacion": "Markup estándar para minoristas en este rango de precio"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en estrategia de precios. Responde solo en formato JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            try:
                sugerencia = json.loads(response.choices[0].message.content)
                return sugerencia
            except json.JSONDecodeError:
                logger.error("Error al parsear sugerencia de markup")
                return None
                
        except Exception as e:
            logger.error(f"Error al sugerir markup: {e}")
            return None

    def clasificar_producto(self, nombre: str, codigo: str = "") -> Optional[Dict]:
        """Clasifica automáticamente un producto"""
        if not self.disponible:
            return None
        
        try:
            prompt = f"""
            Clasifica el siguiente producto:

            Nombre: {nombre}
            Código: {codigo}

            Determina:
            1. Marca más probable (moura, acubat, lubeck, solar)
            2. Canal recomendado (minorista, mayorista, distribuidor)
            3. Capacidad estimada en Ah
            4. Rango de precio esperado

            Responde en formato JSON:
            {{
                "marca": "moura",
                "canal": "minorista",
                "capacidad": "60 Ah",
                "rango_precio": {{"min": 80, "max": 120}},
                "confianza": 0.85
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en clasificación de productos de baterías. Responde solo en formato JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            import json
            try:
                clasificacion = json.loads(response.choices[0].message.content)
                return clasificacion
            except json.JSONDecodeError:
                logger.error("Error al parsear clasificación")
                return None
                
        except Exception as e:
            logger.error(f"Error al clasificar producto: {e}")
            return None

    def _crear_prompt_analisis(self, producto: Producto) -> str:
        """Crea el prompt para análisis de un producto individual"""
        alertas_texto = ", ".join([alerta.value for alerta in producto.alertas]) if producto.alertas else "Ninguna"
        
        return f"""
        Analiza este producto de batería:

        Código: {producto.codigo}
        Nombre: {producto.nombre}
        Capacidad: {producto.capacidad or 'No especificada'}
        Marca: {producto.marca.value}
        Canal: {producto.canal.value}
        Precio base: ${producto.precio_base:.2f}
        Precio final: ${producto.precio_final:.2f}
        Margen: {producto.margen:.1f}%
        Alertas: {alertas_texto}

        Proporciona una sugerencia breve (máximo 2 líneas) sobre:
        - Si el precio está bien posicionado
        - Si hay algún problema evidente
        - Sugerencia de mejora si aplica

        Responde de forma concisa y práctica.
        """

    def _crear_resumen_productos(self, productos: List[Producto]) -> str:
        """Crea un resumen de productos para análisis masivo"""
        resumen = f"Total de productos: {len(productos)}\n\n"
        
        # Agrupar por marca
        por_marca = {}
        for producto in productos:
            marca = producto.marca.value
            if marca not in por_marca:
                por_marca[marca] = []
            por_marca[marca].append(producto)
        
        for marca, productos_marca in por_marca.items():
            resumen += f"Marca {marca}: {len(productos_marca)} productos\n"
            precios = [p.precio_final for p in productos_marca]
            margenes = [p.margen for p in productos_marca]
            
            resumen += f"  - Precio promedio: ${sum(precios)/len(precios):.2f}\n"
            resumen += f"  - Margen promedio: {sum(margenes)/len(margenes):.1f}%\n"
            resumen += f"  - Productos con alertas: {len([p for p in productos_marca if p.alertas])}\n\n"
        
        return resumen

    def esta_disponible(self) -> bool:
        """Verifica si OpenAI está disponible"""
        return self.disponible 