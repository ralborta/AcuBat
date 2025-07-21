"""
Analizador inteligente de planillas de rentabilidad complejas
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class RentabilidadAnalyzer:
    """Analizador inteligente para planillas de rentabilidad complejas"""
    
    def __init__(self):
        self.reglas_extraidas = {}
        self.diagnostico = {}
        
    def analizar_planilla_compleja(self, file_path: str) -> Dict:
        """
        Analiza una planilla compleja y extrae reglas de rentabilidad
        """
        try:
            logger.info(f"🔍 Analizando planilla compleja: {file_path}")
            
            # Leer todas las hojas
            excel_file = pd.ExcelFile(file_path)
            hojas = excel_file.sheet_names
            
            logger.info(f"📋 Hojas encontradas: {hojas}")
            
            diagnostico = {
                'archivo': file_path,
                'total_hojas': len(hojas),
                'hojas_analizadas': [],
                'reglas_encontradas': 0,
                'problemas_detectados': [],
                'recomendaciones': []
            }
            
            # Analizar cada hoja
            for hoja in hojas:
                try:
                    logger.info(f"📊 Analizando hoja: {hoja}")
                    
                    # Leer la hoja
                    df = pd.read_excel(file_path, sheet_name=hoja)
                    
                    # Analizar estructura de la hoja
                    analisis_hoja = self._analizar_estructura_hoja(df, hoja)
                    diagnostico['hojas_analizadas'].append(analisis_hoja)
                    
                    # Intentar extraer reglas de esta hoja
                    reglas_hoja = self._extraer_reglas_hoja(df, hoja)
                    if reglas_hoja:
                        self.reglas_extraidas[hoja] = reglas_hoja
                        diagnostico['reglas_encontradas'] += len(reglas_hoja)
                    
                except Exception as e:
                    logger.warning(f"Error analizando hoja {hoja}: {e}")
                    diagnostico['problemas_detectados'].append(f"Hoja {hoja}: {str(e)}")
            
            # Generar recomendaciones
            diagnostico['recomendaciones'] = self._generar_recomendaciones(diagnostico)
            
            self.diagnostico = diagnostico
            
            logger.info(f"✅ Análisis completado: {diagnostico['reglas_encontradas']} reglas encontradas")
            
            return diagnostico
            
        except Exception as e:
            logger.error(f"Error analizando planilla: {e}")
            return {'error': str(e)}
    
    def _analizar_estructura_hoja(self, df: pd.DataFrame, nombre_hoja: str) -> Dict:
        """Analiza la estructura de una hoja específica"""
        
        analisis = {
            'nombre': nombre_hoja,
            'filas': len(df),
            'columnas': len(df.columns),
            'nombres_columnas': list(df.columns),
            'tipos_datos': {},
            'valores_unicos': {},
            'posibles_margenes': [],
            'posibles_canales': [],
            'problemas': []
        }
        
        # Analizar tipos de datos
        for col in df.columns:
            col_str = str(col)
            analisis['tipos_datos'][col_str] = str(df[col].dtype)
            
            # Buscar valores únicos (máximo 10)
            valores_unicos = df[col].dropna().unique()
            if len(valores_unicos) <= 10:
                analisis['valores_unicos'][col_str] = list(valores_unicos)
            
            # Buscar posibles márgenes
            if self._es_posible_margen(col_str, df[col]):
                analisis['posibles_margenes'].append(col_str)
            
            # Buscar posibles canales
            if self._es_posible_canal(col_str, df[col]):
                analisis['posibles_canales'].append(col_str)
        
        # Detectar problemas
        if len(df.columns) > 20:
            analisis['problemas'].append("Demasiadas columnas (>20)")
        
        if len(df) > 1000:
            analisis['problemas'].append("Demasiadas filas (>1000)")
        
        columnas_unnamed = [col for col in df.columns if 'unnamed' in str(col).lower()]
        if columnas_unnamed:
            analisis['problemas'].append(f"Columnas sin nombre: {len(columnas_unnamed)}")
        
        return analisis
    
    def _es_posible_margen(self, nombre_col: str, serie: pd.Series) -> bool:
        """Determina si una columna podría contener márgenes"""
        
        nombre_lower = nombre_col.lower()
        
        # Por nombre
        if any(keyword in nombre_lower for keyword in ['margen', 'margin', 'rentabilidad', 'profit', 'porcentaje']):
            return True
        
        # Por valores
        try:
            valores_numericos = pd.to_numeric(serie.dropna(), errors='coerce')
            if len(valores_numericos) > 0:
                # Si los valores están entre 0 y 100, podrían ser porcentajes
                if valores_numericos.min() >= 0 and valores_numericos.max() <= 100:
                    return True
        except:
            pass
        
        return False
    
    def _es_posible_canal(self, nombre_col: str, serie: pd.Series) -> bool:
        """Determina si una columna podría contener canales"""
        
        nombre_lower = nombre_col.lower()
        
        # Por nombre
        if any(keyword in nombre_lower for keyword in ['canal', 'channel', 'tipo', 'type', 'categoria']):
            return True
        
        # Por valores
        valores_unicos = serie.dropna().unique()
        if len(valores_unicos) <= 10:
            valores_str = [str(v).lower() for v in valores_unicos]
            if any(keyword in ' '.join(valores_str) for keyword in ['minorista', 'mayorista', 'distribuidor', 'retail', 'wholesale']):
                return True
        
        return False
    
    def _extraer_reglas_hoja(self, df: pd.DataFrame, nombre_hoja: str) -> List[Dict]:
        """Intenta extraer reglas de rentabilidad de una hoja"""
        
        reglas = []
        
        try:
            # Buscar columnas de márgenes
            columnas_margen = []
            for col in df.columns:
                if self._es_posible_margen(str(col), df[col]):
                    columnas_margen.append(col)
            
            # Buscar columnas de canales
            columnas_canal = []
            for col in df.columns:
                if self._es_posible_canal(str(col), df[col]):
                    columnas_canal.append(col)
            
            # Si encontramos márgenes, crear reglas básicas
            if columnas_margen:
                for idx, row in df.iterrows():
                    try:
                        # Extraer márgenes
                        margenes = []
                        for col_margen in columnas_margen:
                            valor = row[col_margen]
                            if pd.notna(valor):
                                margen = self._convertir_a_porcentaje(valor)
                                if margen is not None:
                                    margenes.append(margen)
                        
                        # Extraer canal
                        canal = "Minorista"  # Default
                        for col_canal in columnas_canal:
                            valor_canal = row[col_canal]
                            if pd.notna(valor_canal):
                                canal = self._normalizar_canal(str(valor_canal))
                                break
                        
                        # Crear regla si tenemos márgenes
                        if margenes:
                            margen_min = min(margenes)
                            margen_opt = max(margenes) if len(margenes) > 1 else margen_min * 1.5
                            
                            regla = {
                                'marca': nombre_hoja.title(),
                                'canal': canal,
                                'linea': 'Estándar',
                                'margen_minimo': margen_min,
                                'margen_optimo': margen_opt,
                                'hoja_origen': nombre_hoja,
                                'fila_origen': idx
                            }
                            
                            reglas.append(regla)
                            
                    except Exception as e:
                        logger.debug(f"Error procesando fila {idx}: {e}")
                        continue
            
            logger.info(f"Extraídas {len(reglas)} reglas de hoja {nombre_hoja}")
            
        except Exception as e:
            logger.warning(f"Error extrayendo reglas de {nombre_hoja}: {e}")
        
        return reglas
    
    def _convertir_a_porcentaje(self, valor) -> Optional[float]:
        """Convierte un valor a porcentaje"""
        try:
            if pd.isna(valor):
                return None
            
            valor_str = str(valor).strip()
            if not valor_str:
                return None
            
            # Remover símbolos de porcentaje
            valor_str = re.sub(r'[^\d.,]', '', valor_str)
            if not valor_str:
                return None
            
            # Convertir coma decimal a punto
            valor_str = valor_str.replace(',', '.')
            
            valor_float = float(valor_str)
            
            # Si es mayor a 1, asumir que ya es porcentaje
            if valor_float > 1:
                return valor_float
            else:
                return valor_float * 100
                
        except:
            return None
    
    def _normalizar_canal(self, canal: str) -> str:
        """Normaliza el nombre del canal"""
        canal_lower = canal.lower()
        
        if any(keyword in canal_lower for keyword in ['minorista', 'retail']):
            return "Minorista"
        elif any(keyword in canal_lower for keyword in ['mayorista', 'wholesale']):
            return "Mayorista"
        elif any(keyword in canal_lower for keyword in ['distribuidor', 'dealer']):
            return "Distribuidor"
        else:
            return canal.title()
    
    def _generar_recomendaciones(self, diagnostico: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        
        recomendaciones = []
        
        if diagnostico['total_hojas'] > 10:
            recomendaciones.append("La planilla tiene muchas hojas. Considera consolidar en menos hojas.")
        
        if diagnostico['reglas_encontradas'] == 0:
            recomendaciones.append("No se encontraron reglas de rentabilidad. Verifica el formato de las columnas.")
        
        problemas_unnamed = [p for p in diagnostico['problemas_detectados'] if 'unnamed' in p.lower()]
        if problemas_unnamed:
            recomendaciones.append("Hay columnas sin nombre. Asigna nombres descriptivos a todas las columnas.")
        
        if len(diagnostico['problemas_detectados']) > 5:
            recomendaciones.append("La planilla tiene muchos problemas estructurales. Considera simplificar el formato.")
        
        return recomendaciones
    
    def obtener_reglas_extraidas(self) -> Dict:
        """Retorna las reglas extraídas"""
        return self.reglas_extraidas
    
    def obtener_diagnostico(self) -> Dict:
        """Retorna el diagnóstico completo"""
        return self.diagnostico 