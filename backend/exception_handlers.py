"""
Manejadores de excepciones globales para FastAPI
Define cómo se manejan las excepciones en toda la aplicación
"""

import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import (
    BaseAPIException,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ExternalServiceError,
    ConfigurationError,
    create_error_response,
    handle_mysql_database_error,
    handle_validation_error,
    handle_file_upload_error
)
from . import logger

def add_exception_handlers(app: FastAPI):
    """Añade todos los manejadores de excepciones a la aplicación FastAPI"""
    
    @app.exception_handler(BaseAPIException)
    async def api_exception_handler(request: Request, exc: BaseAPIException):
        """Manejador para excepciones de API personalizadas"""
        request_id = str(uuid.uuid4())
        
        # Log del error usando nuestro sistema de logging
        logger.log_api_error(
            endpoint=str(request.url),
            method=request.method,
            status_code=exc.status_code,
            error=exc,
            request_data={
                "request_id": request_id,
                "error_code": exc.error_code,
                "detail": exc.detail
            }
        )
        
        response_data = create_error_response(
            exception=exc,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
            headers=getattr(exc, 'headers', None)
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Manejador para errores de validación de FastAPI/Pydantic"""
        request_id = str(uuid.uuid4())
        
        # Convertir a ValidationError personalizado
        api_exc = handle_validation_error(exc)
        
        # Log del error usando nuestro sistema de logging
        body_str = ""
        try:
            # La excepción RequestValidationError contiene información sobre el cuerpo
            if hasattr(exc, 'body') and exc.body:
                if isinstance(exc.body, bytes):
                    body_str = exc.body.decode('utf-8')
                else:
                    body_str = str(exc.body)
        except Exception:
            body_str = "Error al leer el cuerpo desde la excepción."

        logger.log_api_error(
            endpoint=str(request.url),
            method=request.method,
            status_code=api_exc.status_code,
            error=api_exc,
            request_data={
                "request_id": request_id,
                "error_code": api_exc.error_code,
                "detail": api_exc.detail,
                "body": body_str[:500]  # Limitar el tamaño del body logueado
            }
        )
        
        response_data = create_error_response(
            exception=api_exc,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=api_exc.status_code,
            content=response_data
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Manejador para excepciones HTTP de Starlette"""
        request_id = str(uuid.uuid4())
        
        # Convertir a BaseAPIException para respuesta consistente
        api_exc = BaseAPIException(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        )
        
        # Log del error usando nuestro sistema de logging
        logger.log_api_error(
            endpoint=str(request.url),
            method=request.method,
            status_code=api_exc.status_code,
            error=api_exc,
            request_data={
                "request_id": request_id,
                "error_code": api_exc.error_code,
                "detail": api_exc.detail
            }
        )
        
        response_data = create_error_response(
            exception=api_exc,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
            headers=exc.headers
        )
    
    @app.exception_handler(FastAPIHTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
        """Manejador para excepciones HTTP de FastAPI"""
        request_id = str(uuid.uuid4())
        
        # Convertir a BaseAPIException para respuesta consistente
        api_exc = BaseAPIException(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=f"FASTAPI_{exc.status_code}"
        )
        
        # Log del error usando nuestro sistema de logging
        logger.log_api_error(
            endpoint=str(request.url),
            method=request.method,
            status_code=api_exc.status_code,
            error=api_exc,
            request_data={
                "request_id": request_id,
                "error_code": api_exc.error_code,
                "detail": api_exc.detail
            }
        )
        
        response_data = create_error_response(
            exception=api_exc,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
            headers=exc.headers
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejador para excepciones no controladas"""
        request_id = str(uuid.uuid4())
        
        # Log detallado del error usando nuestro sistema de logging
        logger.log_api_error(
            endpoint=str(request.url),
            method=request.method,
            status_code=500,
            error=exc,
            request_data={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "user_agent": request.headers.get('user-agent')
            }
        )
        
        # Crear excepción genérica
        api_exc = BaseAPIException(
            status_code=500,
            detail="Error interno del servidor",
            error_code="INTERNAL_ERROR"
        )
        
        # En desarrollo, mostrar más detalles
        import os
        if os.getenv('ENVIRONMENT', 'development') == 'development':
            api_exc.detail = f"Error interno: {str(exc)}"
        
        response_data = create_error_response(
            exception=api_exc,
            request_id=request_id,
            additional_data={
                "development": os.getenv('ENVIRONMENT', 'development') == 'development'
            }
        )
        
        return JSONResponse(
            status_code=500,
            content=response_data
        )

# Decorador para manejar errores específicos en funciones
def handle_database_errors(func):
    """Decorador para manejar errores de base de datos"""
    import functools
    import mysql.connector as mysql
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except mysql.Error as e:
            raise handle_mysql_database_error(e)
        except Exception as e:
            if "database" in str(e).lower() or "mysql" in str(e).lower():
                raise handle_mysql_database_error(e)
            raise
    return wrapper

def handle_validation_errors(func):
    """Decorador para manejar errores de validación"""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "validation" in str(e).lower() or "pydantic" in str(e).lower():
                raise handle_validation_error(e)
            raise
    return wrapper

def handle_file_errors(func):
    """Decorador para manejar errores de archivo"""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "file" in str(e).lower() or "upload" in str(e).lower():
                raise handle_file_upload_error(e)
            raise
    return wrapper