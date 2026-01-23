import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

class ConfigLoader:
    _instance: Optional['ConfigLoader'] = None
    _config_cache: Dict[str, Any] = {}
    
    def __new__(cls, config_dir: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_dir: Optional[Path] = None):
        if self._initialized:
            return
        self._initialized = True
        self._config_dir = config_dir or Path(
            os.environ.get('TOOLKIT_CONFIG', 
            Path.home() / 'projects' / 'toolkit' / 'config')
        )
        self._resolved_configs: Dict[str, Any] = {}
        self._load_all()
    
    def _load_all(self) -> None:
        self._load_config('paths', 'paths.json')
        self._load_config('models', 'models.json')
        self._load_config('tools', 'tools.json')
        self._load_config('agents', 'agents.json')
        self._load_config('servers', 'servers.json')
        self._load_config('toolkit', 'toolkit.json')
        self._resolve_all_references()
    
    def _load_config(self, key: str, filename: str) -> Dict[str, Any]:
        filepath = self._config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        with open(filepath, 'r') as f:
            config = json.load(f)
        self._config_cache[key] = config
        return config
    
    def _resolve_string(self, s: str, local_context: Dict[str, Any], global_context: Dict[str, Any], max_iterations: int = 10) -> str:
        pattern = r'\$\{([^}]+)\}'
        for _ in range(max_iterations):
            matches = re.findall(pattern, s)
            if not matches:
                break
            for match in matches:
                value = local_context.get(match)
                if value is None:
                    value = self._get_nested_value(match, global_context)
                if value is not None:
                    s = s.replace(f'${{{match}}}', str(value))
        return s
    
    def _resolve_references(self, obj: Any, local_context: Dict[str, Any], global_context: Dict[str, Any]) -> Any:
        if isinstance(obj, str):
            return self._resolve_string(obj, local_context, global_context)
        elif isinstance(obj, dict):
            return {k: self._resolve_references(v, local_context, global_context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_references(item, local_context, global_context) for item in obj]
        return obj
    
    def _get_nested_value(self, path: str, context: Dict[str, Any]) -> Any:
        parts = path.split('.')
        current = context
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _resolve_paths(self) -> Dict[str, Any]:
        paths = self._config_cache.get('paths', {})
        resolved = {}
        for key, value in paths.items():
            if key.startswith('$') or key.startswith('_'):
                continue
            if isinstance(value, str):
                resolved[key] = self._resolve_string(value, resolved, {'paths': resolved})
            else:
                resolved[key] = value
        return resolved
    
    def _resolve_all_references(self) -> None:
        resolved_paths = self._resolve_paths()
        self._resolved_configs['paths'] = resolved_paths
        
        global_context = {
            'paths': resolved_paths,
            'models': {},
            'tools': {},
            'agents': {},
            'servers': {},
            'toolkit': {},
        }
        
        for config_key in ['models', 'tools', 'agents', 'servers', 'toolkit']:
            raw = self._config_cache.get(config_key, {})
            resolved = self._resolve_references(raw, {}, global_context)
            self._resolved_configs[config_key] = resolved
            global_context[config_key] = resolved
    
    @property
    def paths(self) -> Dict[str, Any]:
        return self._resolved_configs.get('paths', {})
    
    @property
    def models(self) -> Dict[str, Any]:
        return self._resolved_configs.get('models', {})
    
    @property
    def tools(self) -> Dict[str, Any]:
        return self._resolved_configs.get('tools', {})
    
    @property
    def agents(self) -> Dict[str, Any]:
        return self._resolved_configs.get('agents', {})
    
    @property
    def servers(self) -> Dict[str, Any]:
        return self._resolved_configs.get('servers', {})
    
    @property
    def toolkit(self) -> Dict[str, Any]:
        return self._resolved_configs.get('toolkit', {})
    
    def get(self, path: str, default: Any = None) -> Any:
        parts = path.split('.')
        current = self._resolved_configs
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def reload(self) -> None:
        self._config_cache.clear()
        self._resolved_configs.clear()
        ConfigLoader._instance = None
        self._initialized = False
        self.__init__(self._config_dir)

_loader: Optional[ConfigLoader] = None

def get_config(config_dir: Optional[Path] = None) -> ConfigLoader:
    global _loader
    if _loader is None or (config_dir and _loader._config_dir != config_dir):
        ConfigLoader._instance = None
        _loader = ConfigLoader(config_dir)
    return _loader

def reset_config() -> None:
    global _loader
    ConfigLoader._instance = None
    _loader = None
