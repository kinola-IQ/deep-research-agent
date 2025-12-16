"""module to configure the large language model provider switcher logic"""
from abc import ABC, abstractmethod
import time

# model providers to iterate through
from langchain_community.llms import Ollama

# modules
from ..utils.logger import logger


# enforcing every model provider class to be defined the same way
class LLM(ABC):
    """interface guilding model class creation"""
    @abstractmethod
    def _load_model(self):
        """
        DocString for load_model
        """


# Ollama
class OllamaClass(LLM):
    """
    Docstring for OllamaClass which uses ollama to load models
    """
    def __init__(self) -> None:
        """
        Docstring for __init__
        :param self: Description
        :param model_list: Description
        :type model_list: list[str]
        """
        self.model_name  = None
        self.model_list: list[str] = ['qwen3:4b', 'gemma3:4b']
        self.model  = self._load_model()

    def _load_model(self):
        """
        Generator that loads models from self.model_list one by one.
        """
        for model_name in self.model_list:
            try:
                model = Ollama(model=model_name)
                self.model_name = model_name
                logger.info(f"Selected model: {model_name}")
                return model
            except Exception as err:
                logger.error(f"Failed to init {model_name}: {err}")
        raise RuntimeError("No Ollama models could be initialized")