from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class RulesetStep(BaseModel):
    var: str = Field(..., description="Nombre de la variable")
    from_var: Optional[str] = Field(None, alias="from", description="Variable de origen")
    value: Optional[Union[float, int, str]] = Field(None, description="Valor fijo")
    expr: Optional[str] = Field(None, description="Expresión matemática")
    type: str = Field(default="var", description="Tipo de paso")

    @validator('*', pre=True)
    def check_step_fields(cls, v, field):
        if field.name == 'var':
            return v
        return v

    @validator('from_var', 'value', 'expr')
    def validate_step_has_one_source(cls, v, values):
        if 'var' not in values:
            return v
        
        sources = [v, values.get('value'), values.get('expr')]
        sources = [s for s in sources if s is not None]
        
        if len(sources) != 1:
            raise ValueError("Step debe tener exactamente una fuente: 'from', 'value' o 'expr'")
        
        return v

class RulesetOverride(BaseModel):
    when: Dict[str, Any] = Field(..., description="Condiciones para aplicar override")
    set: Dict[str, Any] = Field(..., description="Valores a establecer")

class RulesetConfig(BaseModel):
    name: str = Field(..., description="Nombre del ruleset")
    version: str = Field(..., description="Versión del ruleset")
    appliesTo: Dict[str, Any] = Field(default_factory=dict, description="Criterios de aplicación")
    globals: Dict[str, Any] = Field(default_factory=dict, description="Variables globales")
    steps: List[RulesetStep] = Field(..., description="Pasos de cálculo")
    overrides: List[RulesetOverride] = Field(default_factory=list, description="Overrides condicionales")

    @validator('steps')
    def validate_steps_not_empty(cls, v):
        if not v:
            raise ValueError("Steps no puede estar vacío")
        return v

class RulesetBase(BaseModel):
    nombre: str = Field(..., description="Nombre del ruleset")
    version: str = Field(..., description="Versión del ruleset")
    config: RulesetConfig = Field(..., description="Configuración del ruleset")
    is_active: bool = Field(default=True, description="Si el ruleset está activo")

class RulesetCreate(RulesetBase):
    tenant_id: str = Field(..., description="ID del tenant")

class RulesetUpdate(BaseModel):
    nombre: Optional[str] = None
    config: Optional[RulesetConfig] = None
    is_active: Optional[bool] = None

class RulesetResponse(RulesetBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
