import os
from abc import ABC, abstractmethod
from typing import Union, List, Dict

from diskcache import Cache

from .datamodel import TextGenerationConfig, TextGenerationResponse
from .utils import get_user_cache_dir

APP_NAME = "lida"


class TextGenerator(ABC):
    """Abstract base class for text generators."""

    def __init__(self, provider: str = "openai", **kwargs):
        self.provider = provider
        self.model_name = kwargs.get("model_name", "gpt-4o-mini")

        cache_dir_default = get_user_cache_dir(APP_NAME)
        cache_dir_based_on_model = os.path.join(cache_dir_default, self.provider, self.model_name)
        self.cache_dir = kwargs.get("cache_dir", cache_dir_based_on_model)
        self.cache = Cache(self.cache_dir)

    @abstractmethod
    def generate(
            self, messages: Union[List[Dict], str],
            config: TextGenerationConfig = TextGenerationConfig(),
            **kwargs) -> TextGenerationResponse:
        pass

    @abstractmethod
    def count_tokens(self, text) -> int:
        pass
