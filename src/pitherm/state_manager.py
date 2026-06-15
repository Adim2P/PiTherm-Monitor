import json
import os
import threading
from src.pitherm.logger import logger

STATE_DIR = "data"
STATE_FILE = os.path.join(STATE_DIR, "runtime_state.json")

class StateManager:

    def __init__(self):
        os.makedirs(STATE_DIR, exist_ok=True)

        self._lock = threading.Lock()
        self._state = self._load()

    def _load(self):
        if not os.path.exists(STATE_FILE):
            logger.info("[STATE] No existing state file found.")
            return {}
        
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info("[STATE] Runtime state loaded.")

            return data

        except Exception as e:
            logger.error(
                f"[STATE] Failed loading state: {e}",
                exc_info=True
            )

            return {}
        
    def _save(self):
        tmp_file = f"{STATE_FILE}.tmp"

        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(
                    self._state,
                    f,
                    indent=4
                )
            
            os.replace(tmp_file, STATE_FILE)

            logger.info("[STATE] Runtime state saved.")

        except Exception as e:
            logger.error(
                f"[STATE] Failed saving state: {e}",
                exc_info=True
            )
    
    def get(self, key, default=None):
        with self._lock:
            return self._state.get(
                key,
                default
            )
        
    def set (self, key, value):
        with self._lock:
            current = self._state.get(key)
            if current == value:
                return
            
            self._state[key] = value

            logger.info(
                f"[STATE] Updated '{key}' = {value}"
            )

            self._save()

    def dump(self):
        with self._lock:
            return dict(self._state)
        
state = StateManager()