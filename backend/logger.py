import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

class ErrorLogger:
    def __init__(self, log_file_path: str = "D:/DEVFULLAPP/appPHAV3/ErrorLogspha.log"):
        self.log_file_path = Path(log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar el logger
        self.logger = logging.getLogger('hannariskpro')
        self.logger.setLevel(logging.ERROR)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Crear handler para archivo
            file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.ERROR)
            
            # Crear formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            # Añadir handler al logger
            self.logger.addHandler(file_handler)
            
            # También añadir handler para consola durante desarrollo
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.ERROR)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def log_error(self, error: Exception, context: str = "", additional_info: dict = None):
        """Registrar un error con su traceback y contexto"""
        try:
            # Obtener el traceback completo
            tb = traceback.format_exc()
            
            # Crear mensaje de error
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_type = type(error).__name__
            error_message = str(error)
            
            # Construir el registro completo
            log_entry = f"\n\n==============================***=====================\n"
            log_entry += f"Timestamp: {timestamp}\n"
            log_entry += f"Contexto: {context}\n"
            log_entry += f"Tipo de Error: {error_type}\n"
            log_entry += f"Mensaje: {error_message}\n"
            
            if additional_info:
                log_entry += f"Información Adicional:\n"
                for key, value in additional_info.items():
                    log_entry += f"  {key}: {value}\n"
            
            log_entry += f"Traceback:\n{tb}\n"
            log_entry += f"==============================***=====================\n"
            
            # Escribir en el archivo
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # También registrar con el logger
            self.logger.error(f"Error en {context}: {error_type} - {error_message}")
            
        except Exception as logging_error:
            # Si falla el logging, al menos imprimir en consola
            print(f"FALLÓ EL SISTEMA DE LOGGING: {logging_error}")
            print(f"Error original: {error}")
    
    def log_validation_error(self, field_name: str, error_message: str, value: any = None):
        """Registrar errores de validación específicos"""
        context = f"Validación de campo: {field_name}"
        additional_info = {
            "campo": field_name,
            "mensaje_error": error_message,
            "valor_recibido": str(value)
        }
        
        # Crear una excepción de validación para logging
        from pydantic import ValidationError
        validation_error = ValidationError([{"loc": (field_name,), "msg": error_message}])
        self.log_error(validation_error, context, additional_info)
    
    def log_database_error(self, operation: str, table: str, error: Exception, query: str = None):
        """Registrar errores de base de datos específicos"""
        context = f"Operación de base de datos: {operation} en tabla {table}"
        additional_info = {
            "operacion": operation,
            "tabla": table,
            "query": query
        }
        self.log_error(error, context, additional_info)
    
    def log_api_error(self, endpoint: str, method: str, status_code: int, error: Exception, request_data: dict = None):
        """Registrar errores de API específicos"""
        context = f"Endpoint: {endpoint} ({method}) - Status: {status_code}"
        additional_info = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "request_data": request_data
        }
        self.log_error(error, context, additional_info)

# Crear instancia global del logger
error_logger = ErrorLogger()

def log_error(error: Exception, context: str = "", additional_info: dict = None):
    """Función conveniente para logging de errores"""
    error_logger.log_error(error, context, additional_info)

def log_validation_error(field_name: str, error_message: str, value: any = None):
    """Función conveniente para logging de errores de validación"""
    error_logger.log_validation_error(field_name, error_message, value)

def log_database_error(operation: str, table: str, error: Exception, query: str = None):
    """Función conveniente para logging de errores de base de datos"""
    error_logger.log_database_error(operation, table, error, query)

def log_api_error(endpoint: str, method: str, status_code: int, error: Exception, request_data: dict = None):
    """Función conveniente para logging de errores de API"""
    error_logger.log_api_error(endpoint, method, status_code, error, request_data)