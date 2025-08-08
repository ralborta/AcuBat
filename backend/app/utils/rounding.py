import math
from typing import Union

def rounding(value: Union[float, int], method: str = 'round') -> float:
    """
    Función de redondeo personalizada
    
    Args:
        value: Valor a redondear
        method: Método de redondeo
        
    Returns:
        Valor redondeado según el método especificado
    """
    if not isinstance(value, (int, float)):
        raise ValueError("El valor debe ser numérico")
    
    if method == 'ceil50':
        return math.ceil(value / 50) * 50
    elif method == 'floor50':
        return math.floor(value / 50) * 50
    elif method == 'round50':
        return round(value / 50) * 50
    elif method == 'ceil100':
        return math.ceil(value / 100) * 100
    elif method == 'floor100':
        return math.floor(value / 100) * 100
    elif method == 'round100':
        return round(value / 100) * 100
    elif method == 'ceil25':
        return math.ceil(value / 25) * 25
    elif method == 'floor25':
        return math.floor(value / 25) * 25
    elif method == 'round25':
        return round(value / 25) * 25
    elif method == 'ceil10':
        return math.ceil(value / 10) * 10
    elif method == 'floor10':
        return math.floor(value / 10) * 10
    elif method == 'round10':
        return round(value / 10) * 10
    elif method == 'ceil':
        return math.ceil(value)
    elif method == 'floor':
        return math.floor(value)
    else:
        return round(value)

def validate_rounding_method(method: str) -> bool:
    """
    Valida si un método de redondeo es válido
    
    Args:
        method: Método a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    valid_methods = [
        'ceil50', 'floor50', 'round50',
        'ceil100', 'floor100', 'round100',
        'ceil25', 'floor25', 'round25',
        'ceil10', 'floor10', 'round10',
        'ceil', 'floor', 'round'
    ]
    return method in valid_methods
