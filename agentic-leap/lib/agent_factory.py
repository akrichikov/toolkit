from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
from strands import Agent
from .config_loader import ConfigLoader, get_config
from .config_mapper import ConfigMapper, AgentConfig
from .model_factory import ModelFactory
from .tool_factory import ToolFactory

class AgentFactory:
    def __init__(self, loader: Optional[ConfigLoader] = None):
        self._loader = loader or get_config()
        self._mapper = ConfigMapper(self._loader)
        self._agent_cache: Dict[str, Agent] = {}
    
    def create_agent(self, agent_key: str, use_cache: bool = True) -> Agent:
        if use_cache and agent_key in self._agent_cache:
            return self._agent_cache[agent_key]
        
        agent_config = self._mapper.get_agent_config(agent_key)
        if not agent_config:
            raise ValueError(f"Agent config not found: {agent_key}")
        
        model = ModelFactory.create(agent_config.model)
        tools = ToolFactory.get_tool_set(self._loader, agent_config.tool_set)
        paths = self._mapper.get_paths()
        custom_tools_dir = Path(paths.tools_dir)
        if custom_tools_dir.exists():
            tools.extend(ToolFactory.load_custom_tools(custom_tools_dir))
        
        agent = Agent(
            name=agent_config.name,
            description=agent_config.description,
            system_prompt=agent_config.system_prompt,
            tools=tools,
            model=model,
        )
        
        if use_cache:
            self._agent_cache[agent_key] = agent
        
        return agent
    
    def create_all_agents(self, use_cache: bool = True) -> Dict[str, Agent]:
        agent_configs = self._mapper.get_all_agent_configs()
        return {
            key: self.create_agent(key, use_cache=use_cache)
            for key in agent_configs.keys()
        }
    
    def create_server_agents(self, use_cache: bool = True) -> Dict[str, Agent]:
        enabled_agents = self._mapper.get_enabled_server_agents()
        return {
            key: self.create_agent(key, use_cache=use_cache)
            for key in enabled_agents
        }
    
    def get_agent(self, agent_key: str) -> Optional[Agent]:
        return self._agent_cache.get(agent_key)
    
    def clear_cache(self) -> None:
        self._agent_cache.clear()
    
    def reload_agent(self, agent_key: str) -> Agent:
        if agent_key in self._agent_cache:
            del self._agent_cache[agent_key]
        return self.create_agent(agent_key, use_cache=True)

def create_agent(agent_key: str, config_dir: Optional[Path] = None) -> Agent:
    loader = get_config(config_dir)
    factory = AgentFactory(loader)
    return factory.create_agent(agent_key)

def create_all_agents(config_dir: Optional[Path] = None) -> Dict[str, Agent]:
    loader = get_config(config_dir)
    factory = AgentFactory(loader)
    return factory.create_all_agents()
