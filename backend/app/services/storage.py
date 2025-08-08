import os
import uuid
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """Servicio para manejo de archivos en MinIO/S3"""
    
    def __init__(self):
        self.client = Minio(
            settings.S3_ENDPOINT,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            secure=settings.S3_SECURE
        )
        self.bucket_name = settings.S3_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Asegura que el bucket existe"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} creado")
        except S3Error as e:
            logger.error(f"Error creando bucket: {e}")
            raise
    
    def upload_file(self, file_data: BinaryIO, filename: str, content_type: str = "application/octet-stream") -> str:
        """
        Sube un archivo a MinIO/S3
        
        Args:
            file_data: Datos del archivo
            filename: Nombre del archivo
            content_type: Tipo de contenido
            
        Returns:
            URL del archivo subido
        """
        try:
            # Generar nombre único
            file_id = str(uuid.uuid4())
            object_name = f"{file_id}/{filename}"
            
            # Subir archivo
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=-1,
                part_size=10*1024*1024,  # 10MB chunks
                content_type=content_type
            )
            
            # Generar URL
            url = f"https://{settings.S3_ENDPOINT}/{self.bucket_name}/{object_name}"
            if not settings.S3_SECURE:
                url = f"http://{settings.S3_ENDPOINT}/{self.bucket_name}/{object_name}"
            
            logger.info(f"Archivo subido: {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"Error subiendo archivo: {e}")
            raise
    
    def download_file(self, object_name: str) -> Optional[BinaryIO]:
        """
        Descarga un archivo de MinIO/S3
        
        Args:
            object_name: Nombre del objeto
            
        Returns:
            Datos del archivo o None si no existe
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response
        except S3Error as e:
            logger.error(f"Error descargando archivo: {e}")
            return None
    
    def delete_file(self, object_name: str) -> bool:
        """
        Elimina un archivo de MinIO/S3
        
        Args:
            object_name: Nombre del objeto
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Archivo eliminado: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error eliminando archivo: {e}")
            return False
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Genera una URL temporal para descargar un archivo
        
        Args:
            object_name: Nombre del objeto
            expires: Tiempo de expiración en segundos
            
        Returns:
            URL temporal
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generando URL: {e}")
            raise

# Instancia global del servicio
storage_service = StorageService()
