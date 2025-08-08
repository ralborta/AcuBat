import os
import sys
import pytest
from unittest.mock import patch
from app.core.config import Settings, create_settings

class TestConfig:
    
    def test_port_handling_valid(self):
        """Test que verifica el manejo correcto de puertos válidos"""
        settings = Settings()
        
        # Test puerto válido
        settings.PORT = "8080"
        assert settings.get_port() == 8080
        
        # Test puerto por defecto
        settings.PORT = "8000"
        assert settings.get_port() == 8000
    
    def test_port_handling_invalid(self):
        """Test que verifica el manejo de puertos inválidos"""
        settings = Settings()
        
        # Test puerto no numérico
        settings.PORT = "XXXX"
        assert settings.get_port() == 8000
        
        # Test puerto vacío
        settings.PORT = ""
        assert settings.get_port() == 8000
        
        # Test puerto None
        settings.PORT = None
        assert settings.get_port() == 8000
        
        # Test puerto fuera de rango
        settings.PORT = "70000"
        assert settings.get_port() == 8000
        
        # Test puerto 0
        settings.PORT = "0"
        assert settings.get_port() == 8000
    
    def test_debug_handling(self):
        """Test que verifica el manejo de valores booleanos"""
        settings = Settings()
        
        # Test valores True
        for value in ["true", "True", "TRUE", "1", "yes", "on"]:
            settings.DEBUG = value
            assert settings.get_debug() == True
        
        # Test valores False
        for value in ["false", "False", "FALSE", "0", "no", "off", "invalid"]:
            settings.DEBUG = value
            assert settings.get_debug() == False
    
    def test_numeric_conversions(self):
        """Test que verifica las conversiones numéricas seguras"""
        settings = Settings()
        
        # Test MAX_FILE_SIZE
        settings.MAX_FILE_SIZE = "10485760"  # 10MB
        assert settings.get_max_file_size() == 10485760
        
        settings.MAX_FILE_SIZE = "invalid"
        assert settings.get_max_file_size() == 50 * 1024 * 1024  # 50MB default
        
        # Test MAX_UPLOAD_FILES
        settings.MAX_UPLOAD_FILES = "5"
        assert settings.get_max_upload_files() == 5
        
        settings.MAX_UPLOAD_FILES = "invalid"
        assert settings.get_max_upload_files() == 10  # default
    
    def test_float_conversions(self):
        """Test que verifica las conversiones de float"""
        settings = Settings()
        
        # Test QA thresholds
        settings.QA_GLOBAL_THRESHOLD = "0.10"
        assert settings.get_qa_global_threshold() == 0.10
        
        settings.QA_GLOBAL_THRESHOLD = "invalid"
        assert settings.get_qa_global_threshold() == 0.08  # default
        
        settings.QA_SKU_THRESHOLD = "0.20"
        assert settings.get_qa_sku_threshold() == 0.20
        
        settings.QA_SKU_THRESHOLD = "invalid"
        assert settings.get_qa_sku_threshold() == 0.15  # default
    
    @patch('os.getenv')
    def test_port_from_env_xxxx(self, mock_getenv):
        """Test específico para PORT='XXXX' - debe usar 8000 por defecto"""
        # Simular PORT='XXXX' en variables de entorno
        mock_getenv.return_value = "XXXX"
        
        # Crear settings con PORT='XXXX'
        with patch.dict(os.environ, {'PORT': 'XXXX'}):
            settings = Settings()
            assert settings.get_port() == 8000
    
    @patch('os.getenv')
    def test_port_from_env_valid(self, mock_getenv):
        """Test para PORT válido desde variables de entorno"""
        # Simular PORT=3000 en variables de entorno
        with patch.dict(os.environ, {'PORT': '3000'}):
            settings = Settings()
            assert settings.get_port() == 3000
    
    def test_validation_missing_vars(self):
        """Test que verifica la validación de variables requeridas"""
        settings = Settings()
        
        # Configurar valores por defecto (que indican que faltan)
        settings.DATABASE_URL = "postgresql://user:password@localhost/acubat_pricing"
        settings.SECRET_KEY = "your-secret-key-here"
        settings.API_SECRET = "your-secret-key-here"
        
        # Debe fallar la validación
        with pytest.raises(SystemExit):
            settings.validate_required_env_vars()
    
    def test_validation_valid_vars(self):
        """Test que verifica la validación con variables válidas"""
        settings = Settings()
        
        # Configurar valores válidos
        settings.DATABASE_URL = "postgresql://real_user:real_pass@localhost/real_db"
        settings.SECRET_KEY = "real-secret-key-123"
        settings.API_SECRET = "real-api-secret-456"
        
        # No debe fallar
        try:
            settings.validate_required_env_vars()
        except SystemExit:
            pytest.fail("validate_required_env_vars() should not raise SystemExit with valid vars")
    
    def test_configuration_summary_logging(self, caplog):
        """Test que verifica el logging del resumen de configuración"""
        settings = Settings()
        settings.log_configuration_summary()
        
        # Verificar que se logueó el resumen
        assert "=== RESUMEN DE CONFIGURACIÓN ===" in caplog.text
        assert "Entorno:" in caplog.text
        assert "Puerto:" in caplog.text
        assert "CORS Origins:" in caplog.text
        assert "S3 Bucket:" in caplog.text

if __name__ == "__main__":
    # Test manual para PORT='XXXX'
    print("Testing PORT='XXXX' scenario...")
    
    # Simular PORT='XXXX'
    os.environ['PORT'] = 'XXXX'
    
    try:
        settings = Settings()
        port = settings.get_port()
        print(f"PORT='XXXX' -> get_port() = {port}")
        assert port == 8000, f"Expected 8000, got {port}"
        print("✅ Test PASSED: PORT='XXXX' correctly defaults to 8000")
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        sys.exit(1)
