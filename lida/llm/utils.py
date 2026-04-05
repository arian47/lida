import hashlib
import json
import logging
import os
import platform
from dataclasses import asdict
from typing import Any, Dict, Union

import tiktoken
from diskcache import Cache

logger = logging.getLogger("lida")


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        if not isinstance(message, dict):
            message = asdict(message)

        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n

        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def cache_request(cache: Cache, params: dict, values: Union[Dict, None] = None) -> Any:
    """Cache a request or retrieve a cached response."""
    key = hashlib.md5(json.dumps(params, sort_keys=True).encode("utf-8")).hexdigest()

    if key in cache and values is None:
        return cache[key]

    if values:
        cache[key] = values
    return values


def get_user_cache_dir(app_name: str) -> str:
    """Get platform-specific user cache directory."""
    system = platform.system()
    if system == "Windows":
        cache_path = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), app_name, "Cache")
    elif system == "Darwin":
        cache_path = os.path.join(os.path.expanduser("~/Library/Caches"), app_name)
    else:
        cache_path = os.path.join(
            os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), app_name
        )
    os.makedirs(cache_path, exist_ok=True)
    return cache_path


def get_models_maxtoken_dict(models_list):
    """Build a dict mapping model name -> max tokens from a provider config."""
    if not models_list:
        return {}

    models_dict = {}
    for model in models_list:
        if "model" in model and "parameters" in model["model"]:
            details = model["model"]["parameters"]
            models_dict[details["model"]] = model["max_tokens"]
    return models_dict
