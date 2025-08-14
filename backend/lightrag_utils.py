"""
Utility functions to handle LightRAG compatibility issues
"""
import os
from typing import Optional

def get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable value with fallback"""
    return os.environ.get(key, default)

# Patch lightrag.utils if needed
try:
    import lightrag.utils
    if not hasattr(lightrag.utils, 'get_env_value'):
        lightrag.utils.get_env_value = get_env_value
except ImportError:
    pass
