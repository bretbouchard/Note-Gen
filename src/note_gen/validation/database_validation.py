"""Database validation module."""
from typing import Dict, Any, Optional
from note_gen.validation.base_validation import ValidationResult
from note_gen.core.constants import DATABASE

class DatabaseValidation:
    """Database validation class."""
    
    @staticmethod
    def validate_connection_params(params: Dict[str, Any]) -> ValidationResult:
        """Validate database connection parameters."""
        result = ValidationResult(is_valid=True)
        
        # Validate host
        if "host" not in params:
            result.add_error("host", "Host parameter is required")
        elif not isinstance(params["host"], str):
            result.add_error("host", "Host must be a string")
            
        # Validate port
        if "port" not in params:
            result.add_error("port", "Port parameter is required")
        elif not isinstance(params["port"], int) or not (1 <= params["port"] <= 65535):
            result.add_error("port", "Port must be an integer between 1 and 65535")
            
        # Validate database name
        if "database" not in params:
            result.add_error("database", "Database name is required")
        elif not isinstance(params["database"], str):
            result.add_error("database", "Database name must be a string")
            
        # Validate timeout
        if "timeout_ms" in params:
            if not isinstance(params["timeout_ms"], int) or params["timeout_ms"] < 0:
                result.add_error("timeout_ms", "Timeout must be a positive integer")
            elif params["timeout_ms"] < 1000:
                result.add_warning("Timeout value is less than 1 second")
                
        # Validate pool size
        if "max_pool_size" in params:
            if not isinstance(params["max_pool_size"], int) or params["max_pool_size"] < 1:
                result.add_error("max_pool_size", "Max pool size must be a positive integer")
                
        # Validate SSL configuration
        if params.get("ssl_enabled", False):
            if "ssl_ca_file" not in params:
                result.add_error("ssl_ca_file", "SSL CA file is required when SSL is enabled")
            elif not isinstance(params["ssl_ca_file"], str):
                result.add_error("ssl_ca_file", "SSL CA file path must be a string")
                
        # Check for unknown parameters
        known_params = {
            "host", "port", "database", "username", "password",
            "timeout_ms", "max_pool_size", "min_pool_size",
            "ssl_enabled", "ssl_ca_file"
        }
        
        unknown_params = set(params.keys()) - known_params
        if unknown_params:
            for param in unknown_params:
                result.add_error(
                    param,
                    f"Unknown parameter: {param}"
                )
        
        return result
