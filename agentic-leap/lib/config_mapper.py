from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class PathConfig:
    toolkit_home: str
    agentic_leap: str
    projects: str
    config: str
    logs: str
    lib: str
    services: str
    agents_dir: str
    tools_dir: str
    bin: str
    python: str
    pip: str

@dataclass
class ModelConfig:
    provider: str
    model_id: str
    region: Optional[str] = None
    host: Optional[str] = None
    env_key: Optional[str] = None
    extra_args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentConfig:
    name: str
    description: str
    model: ModelConfig
    tool_set: str
    system_prompt: str
    capabilities: List[str] = field(default_factory=list)

@dataclass
class ServerConfig:
    host: str
    base_port: int
    version: str
    agents: Dict[str, Dict[str, Any]]
    logging: Dict[str, Any]
    daemon: Dict[str, Any]

class ConfigMapper:
    def __init__(self, loader: 'ConfigLoader'):
        self._loader = loader
    
    def get_paths(self) -> PathConfig:
        p = self._loader.paths
        return PathConfig(
            toolkit_home=p.get('toolkit_home', ''),
            agentic_leap=p.get('agentic_leap', ''),
            projects=p.get('projects', ''),
            config=p.get('config', ''),
            logs=p.get('logs', ''),
            lib=p.get('lib', ''),
            services=p.get('services', ''),
            agents_dir=p.get('agents_dir', ''),
            tools_dir=p.get('tools_dir', ''),
            bin=p.get('bin', ''),
            python=p.get('python', ''),
            pip=p.get('pip', ''),
        )
    
    def get_model_config(self, provider: str, model_key: str) -> Optional[ModelConfig]:
        providers = self._loader.models.get('providers', {})
        if provider not in providers:
            return None
        provider_config = providers[provider]
        if not provider_config.get('enabled', True):
            return None
        models = provider_config.get('models', {})
        if model_key not in models:
            return None
        model_data = models[model_key]
        return ModelConfig(
            provider=provider,
            model_id=model_data.get('model_id', ''),
            region=model_data.get('region'),
            host=provider_config.get('host'),
            env_key=provider_config.get('env_key'),
            extra_args=model_data.get('extra_args', {}),
        )
    
    def get_default_model(self) -> Optional[ModelConfig]:
        default_provider = self._loader.models.get('default_provider', 'bedrock')
        providers = self._loader.models.get('providers', {})
        if default_provider not in providers:
            return None
        provider_config = providers[default_provider]
        for model_key, model_data in provider_config.get('models', {}).items():
            if model_data.get('default', False):
                return self.get_model_config(default_provider, model_key)
        return None
    
    def get_tool_set(self, set_name: str) -> List[str]:
        tool_sets = self._loader.tools.get('tool_sets', {})
        if set_name not in tool_sets:
            return []
        return tool_sets[set_name].get('tools', [])
    
    def get_agent_config(self, agent_key: str) -> Optional[AgentConfig]:
        agents = self._loader.agents.get('agents', {})
        if agent_key not in agents:
            return None
        agent_data = agents[agent_key]
        model_info = agent_data.get('model', {})
        model_config = self.get_model_config(
            model_info.get('provider', 'bedrock'),
            model_info.get('model_key', 'claude-sonnet')
        )
        if not model_config:
            model_config = self.get_default_model()
        prompt_template = agent_data.get('system_prompt_template', '')
        system_prompts = self._loader.agents.get('system_prompts', {})
        system_prompt = system_prompts.get(prompt_template, '')
        return AgentConfig(
            name=agent_data.get('name', agent_key),
            description=agent_data.get('description', ''),
            model=model_config,
            tool_set=agent_data.get('tool_set', 'core'),
            system_prompt=system_prompt,
            capabilities=agent_data.get('capabilities', []),
        )
    
    def get_all_agent_configs(self) -> Dict[str, AgentConfig]:
        agents = self._loader.agents.get('agents', {})
        return {
            key: self.get_agent_config(key)
            for key in agents.keys()
            if self.get_agent_config(key) is not None
        }
    
    def get_server_config(self) -> ServerConfig:
        a2a = self._loader.servers.get('a2a', {})
        return ServerConfig(
            host=a2a.get('host', '0.0.0.0'),
            base_port=a2a.get('base_port', 47391),
            version=a2a.get('version', '0.1.0'),
            agents=a2a.get('agents', {}),
            logging=self._loader.servers.get('logging', {}),
            daemon=self._loader.servers.get('daemon', {}),
        )
    
    def get_enabled_server_agents(self) -> List[str]:
        server_config = self.get_server_config()
        return [
            agent_key
            for agent_key, agent_info in server_config.agents.items()
            if agent_info.get('enabled', True)
        ]
    
    def get_agent_port(self, agent_key: str) -> int:
        server_config = self.get_server_config()
        agent_info = server_config.agents.get(agent_key, {})
        offset = agent_info.get('port_offset', 0)
        return server_config.base_port + offset
