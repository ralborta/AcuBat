import os
import logging
from typing import Optional, List
from .models import Producto, TipoAlerta
import openai

logger = logging.getLogger(__name__)

class OpenAIHelper:
    def __init__(self):
        # Configurar API key de OpenAI
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("Cliente OpenAI configurado correctamente")
            except Exception as e:
                logger.error(f"Error configurando cliente OpenAI: {e}")
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY no encontrada en variables de entorno")

    def analizar_producto(self, producto: Producto) -> Optional[str]:
        """Analiza un producto individual usando OpenAI"""
        if not self.client:
            return None
        
        try:
            # Preparar prompt para análisis
            prompt = self._crear_prompt_analisis(producto)
            
            # Llamar a OpenAI con timeout y manejo de errores
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de precios y márgenes comerciales. Analiza los productos y proporciona sugerencias concisas y útiles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.3,
                timeout=30  # Timeout de 30 segundos
            )
            
            sugerencia = response.choices[0].message.content.strip()
            logger.info(f"Análisis OpenAI para {producto.codigo}: {sugerencia[:50]}...")
            
            return sugerencia
            
        except openai.RateLimitError:
            logger.warning("Rate limit de OpenAI alcanzado")
            return "Análisis temporalmente no disponible (rate limit)"
        except openai.APIError as e:
            logger.error(f"Error de API OpenAI: {e}")
            return "Error de conexión con OpenAI"
        except Exception as e:
            logger.error(f"Error en análisis OpenAI para {producto.codigo}: {e}")
            return None

    def analizar_lote_productos(self, productos: List[Producto]) -> List[Producto]:
        """Analiza un lote de productos usando OpenAI"""
        if not self.client:
            logger.warning("OpenAI no disponible, saltando análisis")
            return productos
        
        productos_analizados = []
        productos_analizados_count = 0
        
        for i, producto in enumerate(productos):
            try:
                # Solo analizar productos con alertas o márgenes extremos (máximo 10 productos)
                if (producto.alertas or producto.margen < 10 or producto.margen > 80) and productos_analizados_count < 10:
                    logger.info(f"Analizando producto {i+1}/{len(productos)}: {producto.codigo}")
                    sugerencia = self.analizar_producto(producto)
                    if sugerencia:
                        producto.sugerencias_openai = sugerencia
                        productos_analizados_count += 1
                else:
                    producto.sugerencias_openai = ""
                
                productos_analizados.append(producto)
                
            except Exception as e:
                logger.error(f"Error analizando producto {producto.codigo}: {e}")
                producto.sugerencias_openai = "Error en análisis"
                productos_analizados.append(producto)
        
        logger.info(f"Analizados {productos_analizados_count} productos con OpenAI de {len(productos)} total")
        return productos_analizados

    def _crear_prompt_analisis(self, producto: Producto) -> str:
        """Crea el prompt para análisis de OpenAI"""
        alertas_texto = ", ".join(producto.alertas) if producto.alertas else "Sin alertas"
        
        prompt = f"""
Analiza este producto de baterías y proporciona una sugerencia concisa:

**Producto:**
- Código: {producto.codigo}
- Descripción: {producto.nombre}
- Marca: {producto.marca.value}
- Canal: {producto.canal.value}
- Precio base: ${producto.precio_base:,.2f}
- Precio final: ${producto.precio_final:,.2f}
- Margen: {producto.margen:.1f}%
- Alertas: {alertas_texto}

**Pregunta:**
¿Este precio parece correcto para el canal y la marca? ¿Qué sugerencia darías?

Responde de forma concisa (máximo 2 líneas) y práctica.
"""
        return prompt

    def generar_resumen_analisis(self, productos: List[Producto]) -> str:
        """Genera un resumen de análisis para todos los productos"""
        if not self.client:
            return "Análisis OpenAI no disponible"
        
        try:
            # Preparar datos para resumen
            total_productos = len(productos)
            productos_con_alertas = len([p for p in productos if p.alertas])
            margen_promedio = sum(p.margen for p in productos) / total_productos if productos else 0
            
            # Contar alertas por tipo
            alertas_por_tipo = {}
            for producto in productos:
                for alerta in producto.alertas:
                    alertas_por_tipo[alerta] = alertas_por_tipo.get(alerta, 0) + 1
            
            # Resumen por marca
            resumen_marcas = {}
            for producto in productos:
                marca = producto.marca.value
                if marca not in resumen_marcas:
                    resumen_marcas[marca] = {'total': 0, 'con_alertas': 0, 'margen_promedio': 0}
                resumen_marcas[marca]['total'] += 1
                if producto.alertas:
                    resumen_marcas[marca]['con_alertas'] += 1
                resumen_marcas[marca]['margen_promedio'] += producto.margen
            
            # Calcular promedios por marca
            for marca in resumen_marcas:
                total = resumen_marcas[marca]['total']
                if total > 0:
                    resumen_marcas[marca]['margen_promedio'] = round(resumen_marcas[marca]['margen_promedio'] / total, 1)
            
            prompt = f"""
Genera un resumen ejecutivo del análisis de precios de baterías:

**Estadísticas generales:**
- Total productos: {total_productos}
- Productos con alertas: {productos_con_alertas}
- Margen promedio: {margen_promedio:.1f}%

**Alertas por tipo:**
{chr(10).join([f"- {alerta}: {cantidad}" for alerta, cantidad in alertas_por_tipo.items()])}

**Resumen por marca:**
{chr(10).join([f"- {marca}: {data['total']} productos, {data['con_alertas']} alertas, margen {data['margen_promedio']}%" for marca, data in resumen_marcas.items()])}

**Recomendaciones principales:**
Proporciona 2-3 recomendaciones clave para optimizar la estrategia de precios de baterías.

Responde de forma ejecutiva y práctica.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un consultor experto en estrategia de precios de baterías. Proporciona análisis ejecutivos y recomendaciones prácticas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.3,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.RateLimitError:
            return "Análisis temporalmente no disponible (rate limit)"
        except openai.APIError as e:
            logger.error(f"Error de API OpenAI: {e}")
            return "Error de conexión con OpenAI"
        except Exception as e:
            logger.error(f"Error generando resumen de análisis: {e}")
            return f"Error generando resumen: {str(e)}"

    def esta_disponible(self) -> bool:
        """Verifica si OpenAI está disponible"""
        return self.client is not None and self.api_key is not None 