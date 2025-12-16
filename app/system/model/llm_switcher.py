"""module to handle switching of large language models providers"""
from .llms import OllamaClass
from ..utils.logger import logger
from ..utils.custom_exceptions import ModelLoadError


# swircher class
class LLMSwitcher:
    """
    Docstring for LLMSwitcher
    """

    # factory method to handle dynamic switching
    def _get_llm(self, provider: str = 'ollama'):
        """switches providers based on speed or presence of errors"""
        if provider.lower() == 'ollama':
            provider_instance = OllamaClass()
            if provider_instance.model is None:
                logger.error("Ollama model failed to load")
                raise ModelLoadError("Ollama model failed to load")
            return provider_instance.model
        raise ValueError(f"Unsupported provider: {provider}")

    def load_model(self):
        """
        utilizes the factory method _get_llm to dynamically switch bwtween
        providers
        """
        try:
            model = self._get_llm()
            return model
        except ModelLoadError:
            return None
