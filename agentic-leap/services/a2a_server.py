#!/usr/bin/env python3
import asyncio
import os
import sys
import signal
import logging
from pathlib import Path

TOOLKIT_HOME = Path(os.environ.get('TOOLKIT_HOME', Path.home() / 'projects' / 'toolkit'))
sys.path.insert(0, str(TOOLKIT_HOME / 'agentic-leap'))

from lib import ConfigLoader, ConfigMapper, AgentFactory, ToolFactory, get_config

config = get_config(TOOLKIT_HOME / 'config')
paths = config.paths
servers_config = config.servers

log_file = Path(paths.get('logs', TOOLKIT_HOME / 'agentic-leap' / 'logs')) / 'a2a_server.log'
log_level = getattr(logging, servers_config.get('logging', {}).get('level', 'INFO'))
log_format = servers_config.get('logging', {}).get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('agentic-leap')

from strands import Agent
from strands.multiagent.a2a.server import A2AServer

shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

class A2AServerManager:
    def __init__(self):
        self.config = config
        self.mapper = ConfigMapper(config)
        self.agent_factory = AgentFactory(config)
        self.servers = []
        
    def _create_agent(self, agent_key: str) -> Agent:
        agent_cfg = self.config.agents.get('agents', {}).get(agent_key, {})
        system_prompts = self.config.agents.get('system_prompts', {})
        
        prompt_template = agent_cfg.get('system_prompt_template', agent_key)
        system_prompt = system_prompts.get(prompt_template, '')
        system_prompt = system_prompt.replace('${paths.projects}', paths.get('projects', ''))
        system_prompt = system_prompt.replace('${paths.agentic_leap}', paths.get('agentic_leap', ''))
        
        tool_set_name = agent_cfg.get('tool_set', 'core')
        tools = ToolFactory.get_tool_set(self.config, tool_set_name)
        
        return Agent(
            name=agent_cfg.get('name', agent_key.title()),
            description=agent_cfg.get('description', ''),
            system_prompt=system_prompt,
            tools=tools,
        )
    
    def setup_servers(self):
        a2a_config = self.config.servers.get('a2a', {})
        host = a2a_config.get('host', '0.0.0.0')
        base_port = a2a_config.get('base_port', 47391)
        version = a2a_config.get('version', '0.1.0')
        agents_server_config = a2a_config.get('agents', {})
        
        for agent_key, agent_srv_cfg in agents_server_config.items():
            if not agent_srv_cfg.get('enabled', True):
                logger.info(f"Agent '{agent_key}' is disabled, skipping...")
                continue
                
            port_offset = agent_srv_cfg.get('port_offset', 0)
            port = base_port + port_offset
            
            agent = self._create_agent(agent_key)
            
            server = A2AServer(
                agent=agent,
                host=host,
                port=port,
                http_url=f"http://localhost:{port}",
                version=version,
            )
            
            self.servers.append({
                'name': agent_key,
                'server': server,
                'port': port,
                'agent': agent,
            })
            logger.info(f"Registered agent '{agent_key}' on port {port}")
        
        return self.servers
    
    def get_endpoints(self):
        return {s['name']: f"http://localhost:{s['port']}" for s in self.servers}

async def main():
    logger.info("Starting agentic-leap A2A multi-agent server...")
    logger.info(f"Using config from: {TOOLKIT_HOME / 'config'}")
    
    manager = A2AServerManager()
    servers = manager.setup_servers()
    
    logger.info(f"agentic-leap swarm ready with {len(servers)} agents")
    
    endpoints = manager.get_endpoints()
    for name, url in endpoints.items():
        logger.info(f"{name.title()}: {url}")
    
    for srv in servers:
        logger.info(f"Starting {srv['name']} server on port {srv['port']}...")
    
    await shutdown_event.wait()
    logger.info("Shutdown complete")

if __name__ == '__main__':
    asyncio.run(main())
