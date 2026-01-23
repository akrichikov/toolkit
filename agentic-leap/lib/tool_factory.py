from typing import Any, List, Dict, Callable
from pathlib import Path
import importlib

class ToolFactory:
    _tool_cache: Dict[str, Callable] = {}
    
    STRANDS_TOOLS_MAP = {
        'file_read': 'strands_tools.file_read',
        'file_write': 'strands_tools.file_write',
        'shell': 'strands_tools.shell',
        'http_request': 'strands_tools.http_request',
        'calculator': 'strands_tools.calculator',
        'current_time': 'strands_tools.current_time',
        'python_repl': 'strands_tools.python_repl',
        'editor': 'strands_tools.editor',
        'retrieve': 'strands_tools.retrieve',
        'workflow': 'strands_tools.workflow',
        'journal': 'strands_tools.journal',
        'generate_image': 'strands_tools.generate_image',
        'nova_reels': 'strands_tools.nova_reels',
        'speak': 'strands_tools.speak',
        'swarm': 'strands_tools.swarm',
        'stop': 'strands_tools.stop',
        'slack': 'strands_tools.slack',
        'memory': 'strands_tools.memory',
        'codebase': 'strands_tools.codebase',
        'code_interpreter': 'strands_tools.code_interpreter',
    }
    
    @classmethod
    def get_tool(cls, tool_name: str) -> Callable:
        if tool_name in cls._tool_cache:
            return cls._tool_cache[tool_name]
        
        if tool_name in cls.STRANDS_TOOLS_MAP:
            module_path = cls.STRANDS_TOOLS_MAP[tool_name]
            module = importlib.import_module(module_path.rsplit('.', 1)[0])
            tool = getattr(module, tool_name)
            cls._tool_cache[tool_name] = tool
            return tool
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    @classmethod
    def get_tools(cls, tool_names: List[str]) -> List[Callable]:
        tools = []
        for name in tool_names:
            try:
                tools.append(cls.get_tool(name))
            except (ImportError, AttributeError, ValueError) as e:
                pass
        return tools
    
    @classmethod
    def get_tool_set(cls, loader: 'ConfigLoader', set_name: str) -> List[Callable]:
        from .config_mapper import ConfigMapper
        mapper = ConfigMapper(loader)
        tool_names = mapper.get_tool_set(set_name)
        return cls.get_tools(tool_names)
    
    @classmethod
    def load_custom_tools(cls, tools_dir: Path) -> List[Callable]:
        custom_tools = []
        if not tools_dir.exists():
            return custom_tools
        for tool_file in tools_dir.glob('*.py'):
            if tool_file.name.startswith('_'):
                continue
            try:
                import sys
                sys.path.insert(0, str(tools_dir))
                module_name = tool_file.stem
                module = importlib.import_module(module_name)
                if hasattr(module, 'TOOL_SPEC') and hasattr(module, module_name):
                    tool = getattr(module, module_name)
                    cls._tool_cache[module_name] = tool
                    custom_tools.append(tool)
                sys.path.remove(str(tools_dir))
            except Exception as e:
                pass
        return custom_tools
