"""
Configuration management with hierarchy:
defaults -> config.json -> environment variables.
"""

import os
import json
import logging
import shutil
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Config:
    DEFAULTS: Dict[str, Any] = {
        "personality": "tsundere",
        "response_language": "English",
        "interface_language": "English",
        "chat_height": 400,
        "font_family": "sans-serif",
        "font_size": "medium",
        "max_history": 500,
        "context_messages": 10,
        # "theme" removido
    }

    def __init__(self, config_file: str = "config.json") -> None:
        self.config_file = config_file
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        data = self.DEFAULTS.copy()
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    if not isinstance(loaded, dict):
                        raise ValueError("Config file is not a dictionary")
                    # Remove any leftover "theme" key from old configs
                    loaded.pop("theme", None)
                    data.update(loaded)
            except Exception as e:
                logger.warning(f"Config load error: {e}. Using defaults.")
                corrupted = f"{self.config_file}.corrupted"
                if os.path.exists(self.config_file):
                    os.rename(self.config_file, corrupted)
                    logger.info(f"Renamed corrupted config to {corrupted}")
        # Environment overrides
        for key in data:
            env_val = os.getenv(key.upper())
            if env_val is not None:
                try:
                    if key in ("chat_height", "max_history", "context_messages"):
                        data[key] = int(env_val)
                    elif key in ("personality", "response_language", "interface_language"):
                        data[key] = env_val
                except (ValueError, TypeError):
                    pass
        return data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        self._data[key] = value
        return self._save()

    def _save(self) -> bool:
        backup = None
        if os.path.exists(self.config_file):
            backup = f"{self.config_file}.bak"
            try:
                shutil.copy2(self.config_file, backup)
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        try:
            # Remove any "theme" key before saving
            data_to_save = self._data.copy()
            data_to_save.pop("theme", None)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Config save error: {e}")
            if backup and os.path.exists(backup):
                try:
                    shutil.copy2(backup, self.config_file)
                    logger.info("Restored from backup")
                except Exception as e2:
                    logger.error(f"Could not restore backup: {e2}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()