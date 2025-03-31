"""Database configuration and connection management."""
from typing import Optional, Dict, Any, ClassVar
from pydantic import (
    Field, 
    ConfigDict, 
    BaseModel,
    field_validator,
    computed_field,
    ValidationInfo
)
from src.note_gen.core.constants import DATABASE, COLLECTION_NAMES
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.validation.validation_manager import ValidationManager
from src.note_gen.validation.base_validation import ValidationResult

class DatabaseConfig(BaseModel):
    """Database configuration model with connection management."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
    
    # Class-level validation settings
    validation_level: ClassVar[ValidationLevel] = ValidationLevel.NORMAL
    
    # Fields
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(default=DATABASE["name"], min_length=1)
    collection: str = Field(..., min_length=1)
    username: Optional[str] = None
    password: Optional[str] = None
    timeout_ms: int = Field(default=DATABASE["timeout_ms"], ge=100)
    max_pool_size: int = Field(default=DATABASE["pool"]["max_size"], ge=1)
    min_pool_size: int = Field(default=DATABASE["pool"]["min_size"], ge=1)
    ssl_enabled: bool = Field(default=False)
    ssl_ca_file: Optional[str] = None

    def validate_config(self) -> ValidationResult:
        """Validate the configuration."""
        validation_manager = ValidationManager()
        return validation_manager.validate(self)
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate and normalize host."""
        v = v.strip().lower()
        if not v:
            raise ValueError("Host cannot be empty")
        return v
    
    @field_validator('database', 'collection')
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Validate database and collection names."""
        v = v.strip()
        if not v:
            raise ValueError("Database and collection names cannot be empty")
        if not v.isalnum() and not all(c in '_-' for c in v if not c.isalnum()):
            raise ValueError("Names can only contain alphanumeric characters, underscores, and hyphens")
        return v
    
    @field_validator('min_pool_size', 'max_pool_size')
    @classmethod
    def validate_pool_sizes(cls, v: int, info: ValidationInfo) -> int:
        """Validate pool size constraints."""
        data = info.data
        if 'min_pool_size' in data and 'max_pool_size' in data:
            if data['min_pool_size'] > data['max_pool_size']:
                raise ValueError("min_pool_size cannot be greater than max_pool_size")
        return v

    @computed_field
    def connection_url(self) -> str:
        """Generate MongoDB connection URL."""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
            
        ssl = "?ssl=true" if self.ssl_enabled else ""
        if self.ssl_enabled and self.ssl_ca_file:
            ssl += f"&ssl_ca_file={self.ssl_ca_file}"
            
        return f"mongodb://{auth}{self.host}:{self.port}/{ssl}"
    
    def get_collection_config(self, collection_key: str) -> 'DatabaseConfig':
        """Create new config instance for specific collection."""
        if collection_key not in COLLECTION_NAMES:
            raise ValueError(f"Invalid collection key: {collection_key}")
            
        return self.model_copy(
            update={'collection': COLLECTION_NAMES[collection_key]}
        )
    
    def to_client_settings(self) -> Dict[str, Any]:
        """Convert config to MongoDB client settings."""
        return {
            "host": self.host,
            "port": self.port,
            "serverSelectionTimeoutMS": self.timeout_ms,
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "ssl": self.ssl_enabled,
            **({"ssl_ca_file": self.ssl_ca_file} if self.ssl_enabled and self.ssl_ca_file else {})
        }
