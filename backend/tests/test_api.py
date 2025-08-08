import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import json

from app.main import app
from app.db.base import get_db
from app.services.storage import storage_service

client = TestClient(app)

# Mock para la base de datos
def override_get_db():
    try:
        db = MagicMock()
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

class TestAPI:
    """Tests para los endpoints de la API"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        self.api_key = "acubat_test_key_123"
        self.tenant_id = "test-tenant-id"
        self.headers = {"x-api-key": self.api_key}
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    @patch('app.services.storage.storage_service.upload_file')
    @patch('app.services.parser.excel_parser.parse_excel_file')
    def test_upload_excel(self, mock_parse, mock_upload):
        """Test del endpoint de upload"""
        # Mock responses
        mock_upload.return_value = "https://s3.example.com/file.xlsx"
        mock_parse.return_value = [
            MagicMock(sku="BAT001", marca="Moura", linea="Automotriz", base_price=1000, cost=800)
        ]
        
        # Crear archivo Excel simulado
        file_content = b"fake excel content"
        files = {"file": ("test.xlsx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        data = {"tenant_id": self.tenant_id}
        
        response = client.post("/api/v1/upload", files=files, data=data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["normalized_items_count"] == 1
    
    def test_simulate_pricing(self):
        """Test del endpoint de simulación"""
        request_data = {
            "tenant_id": self.tenant_id,
            "list_id": "test-list-id",
            "ruleset_id": "test-ruleset-id"
        }
        
        with patch('app.services.simulator.pricing_simulator.run_simulation') as mock_simulate:
            mock_run = MagicMock()
            mock_run.id = "test-run-id"
            mock_run.status = "completed"
            mock_simulate.return_value = mock_run
            
            response = client.post("/api/v1/simulate", json=request_data, headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["run_id"] == "test-run-id"
            assert data["status"] == "completed"
    
    def test_get_run_details(self):
        """Test del endpoint para obtener detalles de run"""
        run_id = "test-run-id"
        
        with patch('app.services.simulator.pricing_simulator.get_run_summary') as mock_summary:
            mock_summary.return_value = MagicMock(
                total_items=10,
                cambio_promedio=0.05,
                skus_afectados=5,
                skus_bloqueados_por_gate=1,
                margen_promedio=0.15,
                rentabilidad_promedio=0.12
            )
            
            response = client.get(f"/api/v1/runs/{run_id}", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "price_items" in data
    
    def test_publish_results(self):
        """Test del endpoint de publicación"""
        request_data = {
            "tenant_id": self.tenant_id,
            "run_id": "test-run-id",
            "channel": "minorista",
            "changelog": "Test publication"
        }
        
        with patch('app.services.publisher.publisher.publish_results') as mock_publish:
            mock_publish_obj = MagicMock()
            mock_publish_obj.id = "test-publish-id"
            mock_publish_obj.export_url = "https://s3.example.com/export.csv"
            mock_publish.return_value = mock_publish_obj
            
            response = client.post("/api/v1/publish", json=request_data, headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["publish_id"] == "test-publish-id"
            assert data["export_url"] == "https://s3.example.com/export.csv"
    
    def test_download_csv(self):
        """Test del endpoint de descarga CSV"""
        publish_id = "test-publish-id"
        
        with patch('app.services.storage.storage_service.download_file') as mock_download:
            mock_download.return_value = io.BytesIO(b"SKU,Marca,Linea,K,P,Markup,Rentabilidad\nBAT001,Moura,Automotriz,7050,6697,-0.119,0.05")
            
            response = client.get(f"/api/v1/export.csv?publish_id={publish_id}", headers=self.headers)
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/csv"
            assert "BAT001" in response.text
    
    def test_missing_api_key(self):
        """Test de error cuando falta API key"""
        response = client.get("/health")
        # Health check no requiere API key
        assert response.status_code == 200
        
        response = client.post("/api/v1/upload", files={}, data={})
        assert response.status_code == 401
    
    def test_invalid_file_type(self):
        """Test de error con tipo de archivo inválido"""
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        data = {"tenant_id": self.tenant_id}
        
        response = client.post("/api/v1/upload", files=files, data=data, headers=self.headers)
        assert response.status_code == 400
    
    def test_missing_required_fields(self):
        """Test de error con campos requeridos faltantes"""
        request_data = {
            "tenant_id": self.tenant_id
            # Falta list_id y ruleset_id
        }
        
        response = client.post("/api/v1/simulate", json=request_data, headers=self.headers)
        assert response.status_code == 422
