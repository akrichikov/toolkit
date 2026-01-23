⏺ Bash(/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -c "
try:…)
⎿  ✗ LiteLLM - upstream bug: AttributeError

⏺ Strands Agents SDK Installation Complete

255 packages installed in system Python 3.13.11

Core Packages
┌────────────────────────┬─────────┐
│ Package │ Version │
├────────────────────────┼─────────┤
│ strands-agents │ 1.23.0 │
├────────────────────────┼─────────┤
│ strands-agents-tools │ 0.2.19 │
├────────────────────────┼─────────┤
│ strands-agents-builder │ 0.1.10 │
└────────────────────────┴─────────┘
Model Providers (9 Working)
┌────────────────┬────────────────────────────────┐
│ Provider │ Status │
├────────────────┼────────────────────────────────┤
│ Amazon Bedrock │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Anthropic │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ OpenAI │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Google Gemini │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Mistral │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Ollama │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ LlamaAPI │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Writer │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ Cohere │ ✓ Working │
├────────────────┼────────────────────────────────┤
│ LiteLLM │ ✗ Upstream bug (ARIZE_PHOENIX) │
└────────────────┴────────────────────────────────┘
Additional Capabilities

- 55+ community tools (calculator, file_read, file_write, shell, http_request, etc.)
- MCP (Model Context Protocol) - standardized tool integration
- Agent-to-Agent (A2A) - multi-agent coordination
- Playwright browsers - Chromium, Firefox, WebKit installed
- OpenTelemetry - observability/tracing
- Bidirectional streaming - real-time audio/voice support

Usage Example

from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands_tools import calculator

model = AnthropicModel(model_id="claude-sonnet-4-20250514")
agent = Agent(model=model, tools=[calculator])
result = agent("What is 25 \* 47?")

The only unresolved issue is an upstream bug in LiteLLM affecting the Arize Phoenix integration - this requires a fix from the LiteLLM maintainers.

⏺ Setup Complete

PATH Configuration
┌──────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Location │ Paths Added │
├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ~/.bash_profile │ $TOOLKIT_HOME, $TOOLKIT_HOME/agentic-leap/bin, $TOOLKIT_HOME/projects + auto-discovery for \*/bin │
├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ /etc/paths.d/toolkit │ System-wide: toolkit, agentic-leap, agentic-leap/bin, projects │
└──────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────┘
Shell Migration

- Default shell: bash (already set)
- Transferred from .zshrc: node path, antigravity path
- All zsh configs merged into ~/.bash_profile

agentic-leap Structure

~/projects/toolkit/
├── agentic-leap/
│ ├── bin/leap # CLI control script
│ ├── config/agents.yaml # Agent configuration
│ ├── logs/ # Server logs
│ ├── services/a2a_server.py # Multi-agent A2A server
│ ├── agents/ # Custom agents
│ └── tools/ # Custom tools
└── projects/ # Your product builds

Daemon Status: Running
┌──────────────┬──────┬───────────────────────┐
│ Agent │ Port │ URL │
├──────────────┼──────┼───────────────────────┤
│ Orchestrator │ 9000 │ http://localhost:9000 │
├──────────────┼──────┼───────────────────────┤
│ Builder │ 9001 │ http://localhost:9001 │
├──────────────┼──────┼───────────────────────┤
│ Coder │ 9002 │ http://localhost:9002 │
└──────────────┴──────┴───────────────────────┘
CLI Commands

leap start # Start daemon
leap stop # Stop daemon
leap restart # Restart daemon
leap status # Check status
leap logs # Tail logs
leap agents # List endpoints
leap dev # Foreground mode

The daemon auto-starts on reboot via launchd. Open a new terminal for PATH to take effect.

---

http://127.0.0.1:24282/dashboard/index.html
