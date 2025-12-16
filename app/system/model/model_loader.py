"""module to handle the loading of the models"""
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt
)
from ..utils.logger import logger
from .llm_switcher import LLMSwitcher
from ..utils.custom_exceptions import ModelLoadError


# until loaded, the model does not exist
model = None


# helper function to load the model
@retry(wait=wait_random_exponential(min=5, max=40),
       stop=stop_after_attempt(10))
def load_model():
    """
    loads the model using ollama
    Args:
    :params model_name: name of the model to be loaded
    :returns: None
    """
    global model
    model = LLMSwitcher().load_model()
    if model is None:
        logger.error('could not load the model: ')
        raise ModelLoadError('could not load model')
    return model


def get_model():
    """Return the currently loaded model (or None)."""
    return model
