from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    is_active: bool = True
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('El usuario debe tener al menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('El usuario no puede tener más de 50 caracteres')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('El usuario solo puede contener letras, números y guiones bajos')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v and len(v) > 100:
            raise ValueError('El nombre completo no puede tener más de 100 caracteres')
        return v

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class StudyBase(BaseModel):
    name: str
    description: Optional[str] = None
    company_id: int
    methodology_id: int
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('El nombre del estudio debe tener al menos 3 caracteres')
        if len(v) > 200:
            raise ValueError('El nombre del estudio no puede tener más de 200 caracteres')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'completed', 'cancelled', 'draft']
        if v not in valid_statuses:
            raise ValueError(f'El estado debe ser uno de: {", ".join(valid_statuses)}')
        return v

class StudyCreate(StudyBase):
    pass

class StudyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    company_id: Optional[int] = None
    methodology_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class NodeBase(BaseModel):
    name: str
    description: Optional[str] = None
    study_id: int
    node_type: str
    parent_id: Optional[int] = None
    position_x: float = 0.0
    position_y: float = 0.0
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del nodo no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre del nodo no puede tener más de 100 caracteres')
        return v
    
    @validator('node_type')
    def validate_node_type(cls, v):
        valid_types = ['input', 'process', 'output', 'decision', 'analysis']
        if v not in valid_types:
            raise ValueError(f'El tipo de nodo debe ser uno de: {", ".join(valid_types)}')
        return v

class NodeCreate(NodeBase):
    pass

class NodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    node_type: Optional[str] = None
    parent_id: Optional[int] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None

class AnalysisBase(BaseModel):
    name: str
    description: Optional[str] = None
    node_id: int
    analysis_type: str
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del análisis no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre del análisis no puede tener más de 100 caracteres')
        return v
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        valid_types = ['quantitative', 'qualitative', 'whatif', 'sensitivity', 'montecarlo']
        if v not in valid_types:
            raise ValueError(f'El tipo de análisis debe ser uno de: {", ".join(valid_types)}')
        return v

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    analysis_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class RecommendationBase(BaseModel):
    title: str
    description: str
    priority: str
    analysis_id: int
    status: str = "pending"
    implementation_date: Optional[datetime] = None
    cost_estimate: Optional[float] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1:
            raise ValueError('El título de la recomendación no puede estar vacío')
        if len(v) > 200:
            raise ValueError('El título no puede tener más de 200 caracteres')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'La prioridad debe ser una de: {", ".join(valid_priorities)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f'El estado debe ser uno de: {", ".join(valid_statuses)}')
        return v
    
    @validator('cost_estimate')
    def validate_cost_estimate(cls, v):
        if v is not None and v < 0:
            raise ValueError('El costo estimado no puede ser negativo')
        return v

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    implementation_date: Optional[datetime] = None
    cost_estimate: Optional[float] = None

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre de la empresa no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre de la empresa no puede tener más de 100 caracteres')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[\d\s\-\+\(\)]+$', v):
            raise ValueError('El teléfono solo puede contener números, espacios, guiones, paréntesis y el signo +')
        return v

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    content: Dict[str, Any]
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre de la plantilla no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre de la plantilla no puede tener más de 100 caracteres')
        return v
    
    @validator('template_type')
    def validate_template_type(cls, v):
        valid_types = ['study', 'node', 'analysis', 'recommendation', 'risk_matrix']
        if v not in valid_types:
            raise ValueError(f'El tipo de plantilla debe ser uno de: {", ".join(valid_types)}')
        return v

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ParameterBase(BaseModel):
    name: str
    value: str
    description: Optional[str] = None
    parameter_type: str = "string"
    is_required: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del parámetro no puede estar vacío')
        if len(v) > 50:
            raise ValueError('El nombre del parámetro no puede tener más de 50 caracteres')
        return v
    
    @validator('parameter_type')
    def validate_parameter_type(cls, v):
        valid_types = ['string', 'number', 'boolean', 'date', 'json']
        if v not in valid_types:
            raise ValueError(f'El tipo de parámetro debe ser uno de: {", ".join(valid_types)}')
        return v

class ParameterCreate(ParameterBase):
    pass

class ParameterUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    parameter_type: Optional[str] = None
    is_required: Optional[bool] = None

class DeviationBase(BaseModel):
    title: str
    description: str
    severity: str
    detected_date: datetime
    expected_resolution_date: Optional[datetime] = None
    status: str = "open"
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1:
            raise ValueError('El título de la desviación no puede estar vacío')
        if len(v) > 200:
            raise ValueError('El título no puede tener más de 200 caracteres')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'La severidad debe ser una de: {", ".join(valid_severities)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if v not in valid_statuses:
            raise ValueError(f'El estado debe ser uno de: {", ".join(valid_statuses)}')
        return v

class DeviationCreate(DeviationBase):
    pass

class DeviationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    detected_date: Optional[datetime] = None
    expected_resolution_date: Optional[datetime] = None
    status: Optional[str] = None

class ChecklistItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_required: bool = True
    order: int = 0
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1:
            raise ValueError('El título del ítem no puede estar vacío')
        if len(v) > 200:
            raise ValueError('El título no puede tener más de 200 caracteres')
        return v

class ChecklistItemCreate(ChecklistItemBase):
    pass

class ChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    order: Optional[int] = None

class SafeguardBase(BaseModel):
    name: str
    description: str
    effectiveness: str
    implementation_date: datetime
    review_date: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre de la salvaguarda no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre no puede tener más de 100 caracteres')
        return v
    
    @validator('effectiveness')
    def validate_effectiveness(cls, v):
        valid_levels = ['low', 'medium', 'high', 'very_high']
        if v not in valid_levels:
            raise ValueError(f'La efectividad debe ser una de: {", ".join(valid_levels)}')
        return v

class SafeguardCreate(SafeguardBase):
    pass

class SafeguardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    effectiveness: Optional[str] = None
    implementation_date: Optional[datetime] = None
    review_date: Optional[datetime] = None

class MethodologyBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: str
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre de la metodología no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre no puede tener más de 100 caracteres')
        return v
    
    @validator('version')
    def validate_version(cls, v):
        if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
            raise ValueError('La versión debe seguir el formato X.Y o X.Y.Z')
        return v

class MethodologyCreate(MethodologyBase):
    pass

class MethodologyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del rol no puede estar vacío')
        if len(v) > 50:
            raise ValueError('El nombre no puede tener más de 50 caracteres')
        return v

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RiskMatrixBase(BaseModel):
    name: str
    description: Optional[str] = None
    matrix_type: str
    dimensions: Dict[str, Any]
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre de la matriz no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre no puede tener más de 100 caracteres')
        return v
    
    @validator('matrix_type')
    def validate_matrix_type(cls, v):
        valid_types = ['probability_impact', 'likelihood_consequence', 'custom']
        if v not in valid_types:
            raise ValueError(f'El tipo de matriz debe ser uno de: {", ".join(valid_types)}')
        return v

class RiskMatrixCreate(RiskMatrixBase):
    pass

class RiskMatrixUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    matrix_type: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class SessionBase(BaseModel):
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', v):
            raise ValueError('La dirección IP no tiene un formato válido')
        return v

class SessionCreate(SessionBase):
    pass

class AuditLogBase(BaseModel):
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    
    @validator('action')
    def validate_action(cls, v):
        if len(v) < 1:
            raise ValueError('La acción no puede estar vacía')
        if len(v) > 100:
            raise ValueError('La acción no puede tener más de 100 caracteres')
        return v
    
    @validator('resource_type')
    def validate_resource_type(cls, v):
        if len(v) < 1:
            raise ValueError('El tipo de recurso no puede estar vacío')
        if len(v) > 50:
            raise ValueError('El tipo de recurso no puede tener más de 50 caracteres')
        return v

class AuditLogCreate(AuditLogBase):
    pass

class CauseBase(BaseModel):
    description: str
    category: str
    probability: str
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) < 1:
            raise ValueError('La descripción no puede estar vacía')
        if len(v) > 500:
            raise ValueError('La descripción no puede tener más de 500 caracteres')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if len(v) < 1:
            raise ValueError('La categoría no puede estar vacía')
        if len(v) > 50:
            raise ValueError('La categoría no puede tener más de 50 caracteres')
        return v
    
    @validator('probability')
    def validate_probability(cls, v):
        valid_levels = ['very_low', 'low', 'medium', 'high', 'very_high']
        if v not in valid_levels:
            raise ValueError(f'La probabilidad debe ser una de: {", ".join(valid_levels)}')
        return v

class CauseCreate(CauseBase):
    pass

class CauseUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    probability: Optional[str] = None

class ConsequenceBase(BaseModel):
    description: str
    category: str
    impact: str
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) < 1:
            raise ValueError('La descripción no puede estar vacía')
        if len(v) > 500:
            raise ValueError('La descripción no puede tener más de 500 caracteres')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if len(v) < 1:
            raise ValueError('La categoría no puede estar vacía')
        if len(v) > 50:
            raise ValueError('La categoría no puede tener más de 50 caracteres')
        return v
    
    @validator('impact')
    def validate_impact(cls, v):
        valid_levels = ['very_low', 'low', 'medium', 'high', 'very_high', 'catastrophic']
        if v not in valid_levels:
            raise ValueError(f'El impacto debe ser uno de: {", ".join(valid_levels)}')
        return v

class ConsequenceCreate(ConsequenceBase):
    pass

class ConsequenceUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    impact: Optional[str] = None

class WhatIfQuestionBase(BaseModel):
    question: str
    category: str
    priority: str
    
    @validator('question')
    def validate_question(cls, v):
        if len(v) < 1:
            raise ValueError('La pregunta no puede estar vacía')
        if len(v) > 500:
            raise ValueError('La pregunta no puede tener más de 500 caracteres')
        return v
    
    @validator('category')
    def validate_category(cls, v):
        if len(v) < 1:
            raise ValueError('La categoría no puede estar vacía')
        if len(v) > 50:
            raise ValueError('La categoría no puede tener más de 50 caracteres')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if v not in valid_priorities:
            raise ValueError(f'La prioridad debe ser una de: {", ".join(valid_priorities)}')
        return v

class WhatIfQuestionCreate(WhatIfQuestionBase):
    pass

class WhatIfQuestionUpdate(BaseModel):
    question: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

class SubsystemBase(BaseModel):
    name: str
    description: Optional[str] = None
    study_id: int
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del subsistema no puede estar vacío')
        if len(v) > 100:
            raise ValueError('El nombre no puede tener más de 100 caracteres')
        return v

class SubsystemCreate(SubsystemBase):
    pass

class SubsystemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    study_id: Optional[int] = None

class AttachmentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    description: Optional[str] = None
    
    @validator('filename')
    def validate_filename(cls, v):
        if len(v) < 1:
            raise ValueError('El nombre del archivo no puede estar vacío')
        if len(v) > 255:
            raise ValueError('El nombre del archivo no puede tener más de 255 caracteres')
        return v
    
    @validator('file_type')
    def validate_file_type(cls, v):
        valid_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'txt', 'csv']
        if v.lower() not in valid_types:
            raise ValueError(f'El tipo de archivo debe ser uno de: {", ".join(valid_types)}')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('El tamaño del archivo debe ser mayor que 0')
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError('El tamaño del archivo no puede exceder 100MB')
        return v

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentUpdate(BaseModel):
    filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    description: Optional[str] = None


class RiskMatrixCellCreate(BaseModel):
    matrix_id: int
    fila: int
    columna: int
    nivel: Optional[str] = None
    codigo: Optional[str] = None
    
    @validator('fila')
    def validate_fila(cls, v):
        if v < 1 or v > 5:
            raise ValueError('La fila debe estar entre 1 y 5')
        return v
    
    @validator('columna')
    def validate_columna(cls, v):
        if v < 1 or v > 5:
            raise ValueError('La columna debe estar entre 1 y 5')
        return v
    
    @validator('nivel')
    def validate_nivel(cls, v):
        if v and v not in ['Bajo', 'Medio', 'Alto', 'Crítico']:
            raise ValueError('El nivel debe ser uno de: Bajo, Medio, Alto, Crítico')
        return v


class HistoryRecCreate(BaseModel):
    recomendacion_id: int
    cambio: str
    usuario_id: int
    
    @validator('cambio')
    def validate_cambio(cls, v):
        if len(v) < 1:
            raise ValueError('El cambio no puede estar vacío')
        if len(v) > 500:
            raise ValueError('El cambio no puede tener más de 500 caracteres')
        return v