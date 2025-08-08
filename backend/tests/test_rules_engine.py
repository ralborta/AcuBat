import pytest
from app.services.rules_engine import RulesEngine, MOURA_RULESET

class TestRulesEngine:
    """Tests para el motor de reglas"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.engine = RulesEngine()
        self.engine.load_ruleset(MOURA_RULESET)
    
    def test_moura_bateria_automotriz(self):
        """Test para batería automotriz Moura"""
        # Datos de ejemplo: Batería automotriz 60Ah
        item_data = {
            'sku': 'MOU-60AH',
            'marca': 'Moura',
            'linea': 'Automotriz',
            'base_price': 15000.0,
            'cost': 8000.0
        }
        
        result = self.engine.calculate_pricing(item_data)
        
        # Verificar que no hay errores
        assert 'error' not in result
        
        outputs = result['outputs']
        
        # Verificar variables principales
        assert 'K' in outputs
        assert 'P' in outputs
        assert 'markup' in outputs
        assert 'rentabilidad' in outputs
        assert 'precio_publico' in outputs
        
        # Verificar cálculos (aproximados)
        # K = neto1 * (1 - desc_contado) = 7500 * 0.94 = 7050
        assert abs(outputs['K'] - 7050.0) < 1.0
        
        # P = K - (K*L) - (K*M) - (K*N) = 7050 - 352.5 = 6697.5
        assert abs(outputs['P'] - 6697.5) < 1.0
        
        # markup = (K - cost) / cost = (7050 - 8000) / 8000 = -0.11875
        assert abs(outputs['markup'] - (-0.11875)) < 0.01
        
        # rentabilidad = (P - cost) / P = (6697.5 - 8000) / 6697.5 = -0.194
        assert abs(outputs['rentabilidad'] - (-0.194)) < 0.01
    
    def test_moura_bateria_pesada(self):
        """Test para batería pesada Moura (con IVA reducido)"""
        # Datos de ejemplo: Batería pesada 200Ah
        item_data = {
            'sku': 'MOU-200AH-PESADA',
            'marca': 'Moura',
            'linea': 'Pesada',
            'base_price': 45000.0,
            'cost': 25000.0
        }
        
        result = self.engine.calculate_pricing(item_data)
        
        # Verificar que no hay errores
        assert 'error' not in result
        
        outputs = result['outputs']
        breakdown = result['breakdown']
        
        # Verificar que se aplicó el override de IVA reducido
        assert breakdown['IVA'] == 0.105  # IVA reducido para línea Pesada
        
        # Verificar cálculos con IVA reducido
        # precio_publico_bruto = K * (1 + IVA) = 21150 * 1.105 = 23370.75
        assert abs(breakdown['precio_publico_bruto'] - 23370.75) < 1.0
        
        # precio_publico debe ser redondeado a múltiplos de 50
        assert outputs['precio_publico'] % 50 == 0
    
    def test_moura_bateria_motocicleta(self):
        """Test para batería de motocicleta Moura"""
        # Datos de ejemplo: Batería motocicleta 7Ah
        item_data = {
            'sku': 'MOU-7AH-MOTO',
            'marca': 'Moura',
            'linea': 'Motocicleta',
            'base_price': 8000.0,
            'cost': 4000.0
        }
        
        result = self.engine.calculate_pricing(item_data)
        
        # Verificar que no hay errores
        assert 'error' not in result
        
        outputs = result['outputs']
        breakdown = result['breakdown']
        
        # Verificar variables intermedias
        assert breakdown['precio_lista'] == 8000.0
        assert breakdown['desc1'] == 0.50
        assert breakdown['neto1'] == 4000.0  # 8000 * 0.5
        assert breakdown['desc_contado'] == 0.06
        
        # Verificar K
        expected_k = 4000.0 * (1 - 0.06)  # 3760
        assert abs(outputs['K'] - expected_k) < 1.0
        
        # Verificar que el precio público está redondeado
        assert outputs['precio_publico'] % 50 == 0
    
    def test_missing_required_variables(self):
        """Test para validar que faltan variables requeridas"""
        # Datos incompletos
        item_data = {
            'sku': 'MOU-TEST',
            'marca': 'Moura',
            'linea': 'Automotriz',
            # Faltan base_price y cost
        }
        
        result = self.engine.calculate_pricing(item_data)
        
        # Debe manejar graciosamente los valores faltantes
        assert 'error' not in result
        
        outputs = result['outputs']
        # Los valores deben ser 0 o valores por defecto
        assert outputs.get('K', 0) == 0
        assert outputs.get('P', 0) == 0
    
    def test_ruleset_validation(self):
        """Test para validar la estructura del ruleset"""
        # Ruleset válido
        errors = self.engine.validate_ruleset(MOURA_RULESET)
        assert len(errors) == 0
        
        # Ruleset inválido (sin steps)
        invalid_ruleset = {
            "name": "test",
            "version": "v1",
            "globals": {},
            "steps": []  # Vacío
        }
        errors = self.engine.validate_ruleset(invalid_ruleset)
        assert len(errors) > 0
        
        # Ruleset inválido (sin campos requeridos)
        invalid_ruleset2 = {
            "name": "test"
            # Faltan version y steps
        }
        errors = self.engine.validate_ruleset(invalid_ruleset2)
        assert len(errors) > 0
    
    def test_rounding_function(self):
        """Test para la función de redondeo"""
        # Test ceil50
        assert self.engine.evaluate_expression("rounding(1234, 'ceil50')", {}) == 1250
        assert self.engine.evaluate_expression("rounding(1200, 'ceil50')", {}) == 1200
        
        # Test round50
        assert self.engine.evaluate_expression("rounding(1225, 'round50')", {}) == 1200
        assert self.engine.evaluate_expression("rounding(1275, 'round50')", {}) == 1300
        
        # Test floor50
        assert self.engine.evaluate_expression("rounding(1234, 'floor50')", {}) == 1200
        assert self.engine.evaluate_expression("rounding(1200, 'floor50')", {}) == 1200
