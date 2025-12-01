"""
Módulo de manejo de errores personalizado para Hanna RiskPro
Define excepciones específicas y manejadores de errores consistentes
"""

from fastapi import HTTPException
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAPIException(HTTPException):
    """Excepción base para errores de la API"""
    def __init__(self, status_code: int, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.timestamp = datetime.utcnow().isoformat()

class DatabaseError(BaseAPIException):
    """Errores relacionados con la base de datos"""
    def __init__(self, detail: str, error_code: str = "DB_ERROR"):
        super().__init__(
            status_code=500,
            detail=f"Error de base de datos: {detail}",
            error_code=error_code
        )
        logger.error(f"Database Error: {detail}")

class ValidationError(BaseAPIException):
    """Errores de validación de datos"""
    def __init__(self, detail: str, field: Optional[str] = None, error_code: str = "VALIDATION_ERROR"):
        if field:
            detail = f"Error en el campo '{field}': {detail}"
        super().__init__(
            status_code=422,
            detail=detail,
            error_code=error_code
        )
        logger.warning(f"Validation Error: {detail}")

class AuthenticationError(BaseAPIException):
    """Errores de autenticación"""
    def __init__(self, detail: str, error_code: str = "AUTH_ERROR"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code
        )
        logger.warning(f"Authentication Error: {detail}")

class AuthorizationError(BaseAPIException):
    """Errores de autorización"""
    def __init__(self, detail: str, error_code: str = "AUTHZ_ERROR"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code=error_code
        )
        logger.warning(f"Authorization Error: {detail}")

class NotFoundError(BaseAPIException):
    """Recursos no encontrados"""
    def __init__(self, resource: str, resource_id: Optional[str] = None, error_code: str = "NOT_FOUND"):
        if resource_id:
            detail = f"{resource} con ID '{resource_id}' no encontrado"
        else:
            detail = f"{resource} no encontrado"
        super().__init__(
            status_code=404,
            detail=detail,
            error_code=error_code
        )
        logger.warning(f"Not Found: {detail}")

class ConflictError(BaseAPIException):
    """Conflictos de datos (duplicados, etc.)"""
    def __init__(self, detail: str, error_code: str = "CONFLICT_ERROR"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code=error_code
        )
        logger.warning(f"Conflict Error: {detail}")

class RateLimitError(BaseAPIException):
    """Límite de excedido"""
    def __init__(self, detail: str, retry_after: Optional[int] = None, error_code: str = "RATE_LIMIT_ERROR"):
        headers = {}
        if retry_after:
            headers = {"Retry-After": str(retry_after)}
        super().__init__(
            status_code=429,
            detail=detail,
            error_code=error_code
        )
        self.headers = headers
        logger.warning(f"Rate Limit Error: {detail}")

class ExternalServiceError(BaseAPIException):
    """Errores de servicios externos"""
    def __init__(self, service: str, detail: str, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(
            status_code=502,
            detail=f"Error en servicio externo '{service}': {detail}",
            error_code=error_code
        )
        logger.error(f"External Service Error [{service}]: {detail}")

class ConfigurationError(BaseAPIException):
    """Errores de configuración"""
    def __init__(self, detail: str, error_code: str = "CONFIG_ERROR"):
        super().__init__(
            status_code=500,
            detail=f"Error de configuración: {detail}",
            error_code=error_code
        )
        logger.error(f"Configuration Error: {detail}")

def create_error_response(
    exception: BaseAPIException,
    request_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea una respuesta de error estandarizada
    
    Args:
        exception: La excepción de error
        request_id: ID de la solicitud para seguimiento
        additional_data: Datos adicionales para incluir en la respuesta
    
    Returns:
        Diccionario con la respuesta de error estandarizada
    """
    response = {
        "error": {
            "code": exception.error_code,
            "message": exception.detail,
            "timestamp": exception.timestamp
        }
    }
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    if additional_data:
        response["error"].update(additional_data)
    
    return response

# Manejadores de excepciones globales
def handle_mysql_database_error(error) -> BaseAPIException:
    """Convierte errores de MySQL a excepciones específicas"""
    import mysql.connector as mysql
    
    if isinstance(error, mysql.Error):
        error_code = error.errno
        
        # Errores de integridad (duplicados, constraints)
        if error_code in (1062, 1065, 1452, 1557):  # Duplicate entry, foreign key, etc.
            return ConflictError(str(error))
        
        # Errores de conexión
        elif error_code in (2002, 2003, 2006):  # Can't connect to MySQL server
            return DatabaseError(f"No se puede conectar a la base de datos: {str(error)}", "CONNECTION_ERROR")
        
        # Errores de permisos
        elif error_code in (1142, 1143, 1227):  # Access denied
            return AuthorizationError(f"Permisos insuficientes: {str(error)}", "PERMISSION_ERROR")
        
        # Errores de sintaxis o existencia
        elif error_code in (1054, 1146, # Unknown column, table doesn't exist
                          1064, 1065):  # Syntax error
            return DatabaseError(f"Error en la consulta: {str(error)}", "QUERY_ERROR")
        
        # Errores de timeout
        elif error_code in (1317, 4031):  # Query timeout, connection timeout
            return DatabaseError(f"Timeout en la operación: {str(error)}", "TIMEOUT_ERROR")
        
        # Otros errores de base de datos
        else:
            return DatabaseError(str(error), f"DB_ERROR_{error_code}")
    
    return DatabaseError(str(error))

def handle_validation_error(error) -> BaseAPIException:
    """Convierte errores de validación a excepciones específicas"""
    if hasattr(error, 'errors'):
        # Errores de Pydantic
        field = None
        message = "Error de validación"
        for err in error.errors():
            if 'loc' in err and err['loc']:
                field = '.'.join(str(loc) for loc in err['loc'])
            message = err.get('msg', message)
        return ValidationError(message, field)
    
    return ValidationError(str(error))

def handle_file_upload_error(error) -> BaseAPIException:
    """Maneja errores específicos de carga de archivos"""
    if isinstance(error, OSError):
        return ValidationError("Error al guardar el archivo", "file", "FILE_UPLOAD_ERROR")
    elif isinstance(error, ValueError):
        return ValidationError("Formato de archivo inválido", "file", "FILE_FORMAT_ERROR")
    else:
        return ValidationError("Error al procesar el archivo", "file", "FILE_PROCESS_ERROR")