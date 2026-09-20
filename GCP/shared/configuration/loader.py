import hashlib
import json
from copy import deepcopy
from pathlib import Path

import yaml

from shared.configuration.models import PlatformConfig


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject ambiguous YAML rather than silently accepting a duplicate key."""


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def read_yaml(path: Path) -> dict:
    result = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    if not isinstance(result, dict):
        raise ValueError(f"{path}: expected a mapping")
    return result


def merge(base: dict, overlay: dict) -> dict:
    """Mappings merge recursively; lists/scalars replace. Null never deletes a key."""
    result = deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load(root: Path, environment: str) -> PlatformConfig:
    if environment not in {"dev", "preprod", "prod"}:
        raise ValueError("Unknown environment")
    config = PlatformConfig.model_validate(
        merge(
            read_yaml(root / "config/defaults.yaml"),
            read_yaml(root / f"config/environments/{environment}.yaml"),
        )
    )
    if config.environment != environment:
        raise ValueError("Environment file and environment field do not match")
    return config


def fingerprint(config: PlatformConfig) -> str:
    return hashlib.sha256(json.dumps(config.model_dump(), sort_keys=True).encode()).hexdigest()
