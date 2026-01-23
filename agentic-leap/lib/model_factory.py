import os
from typing import Any, Optional
from .config_mapper import ModelConfig

class ModelFactory:
    _provider_classes = {}
    
    @classmethod
    def _get_provider_class(cls, provider: str):
        if provider in cls._provider_classes:
            return cls._provider_classes[provider]
        
        if provider == 'bedrock':
            from strands.models import BedrockModel
            cls._provider_classes[provider] = BedrockModel
        elif provider == 'anthropic':
            from strands.models.anthropic import AnthropicModel
            cls._provider_classes[provider] = AnthropicModel
        elif provider == 'openai':
            from strands.models.openai import OpenAIModel
            cls._provider_classes[provider] = OpenAIModel
        elif provider == 'gemini':
            from strands.models.gemini import GeminiModel
            cls._provider_classes[provider] = GeminiModel
        elif provider == 'mistral':
            from strands.models.mistral import MistralModel
            cls._provider_classes[provider] = MistralModel
        elif provider == 'ollama':
            from strands.models.ollama import OllamaModel
            cls._provider_classes[provider] = OllamaModel
        elif provider == 'llamaapi':
            from strands.models.llamaapi import LlamaAPIModel
            cls._provider_classes[provider] = LlamaAPIModel
        elif provider == 'writer':
            from strands.models.writer import WriterModel
            cls._provider_classes[provider] = WriterModel
        else:
            raise ValueError(f"Unknown model provider: {provider}")
        
        return cls._provider_classes[provider]
    
    @classmethod
    def create(cls, config: ModelConfig) -> Any:
        provider_class = cls._get_provider_class(config.provider)
        kwargs = {'model_id': config.model_id}
        
        if config.provider == 'bedrock':
            if config.region:
                kwargs['region_name'] = config.region
        
        elif config.provider == 'ollama':
            if config.host:
                kwargs['host'] = config.host
        
        elif config.provider in ('anthropic', 'openai', 'gemini', 'mistral'):
            if config.env_key:
                api_key = os.environ.get(config.env_key)
                if api_key:
                    kwargs['client_args'] = {'api_key': api_key}
        
        kwargs.update(config.extra_args)
        return provider_class(**kwargs)
    
    @classmethod
    def create_from_loader(cls, loader: 'ConfigLoader', provider: str, model_key: str) -> Any:
        from .config_mapper import ConfigMapper
        mapper = ConfigMapper(loader)
        config = mapper.get_model_config(provider, model_key)
        if not config:
            raise ValueError(f"Model config not found: {provider}/{model_key}")
        return cls.create(config)
    
    @classmethod
    def create_default(cls, loader: 'ConfigLoader') -> Any:
        from .config_mapper import ConfigMapper
        mapper = ConfigMapper(loader)
        config = mapper.get_default_model()
        if not config:
            raise ValueError("No default model configured")
        return cls.create(config)
