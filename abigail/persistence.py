"""
Handles all file operations for conversations and trash.
"""

import os
import json
import glob
import logging
from uuid import uuid4
from datetime import datetime
from typing import List, Tuple, Optional  # noqa: F401

logger = logging.getLogger(__name__)


class HistoryRepository:
    def __init__(self, base_dir: str = "history", trash_dir: str = "trash") -> None:
        self.base_dir = base_dir
        self.trash_dir = trash_dir
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for d in (self.base_dir, self.trash_dir):
            try:
                os.makedirs(d, exist_ok=True)
            except Exception as e:
                logger.error(f"Could not create {d}: {e}")

    def _move(self, src: str, dst_dir: str) -> Tuple[bool, str]:
        try:
            os.makedirs(dst_dir, exist_ok=True)
            os.rename(src, os.path.join(dst_dir, os.path.basename(src)))
            return True, ""
        except Exception as e:
            return False, str(e)

    # --- Current session ---
    def save_current(self, history: List[Tuple[str, str]]) -> Tuple[bool, str]:
        path = os.path.join(self.base_dir, "current_session.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True, ""
        except Exception as e:
            return False, str(e)

    def load_current(self) -> Tuple[List[Tuple[str, str]], str]:
        path = os.path.join(self.base_dir, "current_session.json")
        if not os.path.exists(path):
            return [], ""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f), ""
        except Exception as e:
            return [], str(e)

    # --- Snapshots ---
    def save_snapshot(self, history: List[Tuple[str, str]]) -> Tuple[Optional[str], str]:
        if not history:
            return None, "Empty history"
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        uid = uuid4().hex[:6]
        fname = f"conversation_{ts}_{uid}.json"
        path = os.path.join(self.base_dir, fname)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return fname, ""
        except Exception as e:
            return None, str(e)

    def list_snapshots(self) -> List[str]:
        pattern = os.path.join(self.base_dir, "conversation_*.json")
        try:
            return sorted([os.path.basename(f) for f in glob.glob(pattern)], reverse=True)
        except Exception:
            return []

    def load_snapshot(self, filename: str) -> Tuple[List[Tuple[str, str]], str]:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return [], "File not found"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f), ""
        except Exception as e:
            return [], str(e)

    def delete_snapshot(self, filename: str) -> Tuple[bool, str]:
        src = os.path.join(self.base_dir, filename)
        if not os.path.exists(src):
            return False, "File not found"
        return self._move(src, self.trash_dir)

    def delete_all_snapshots(self) -> Tuple[int, str]:
        files = glob.glob(os.path.join(self.base_dir, "conversation_*.json"))
        count, errors = 0, []
        for f in files:
            ok, err = self._move(f, self.trash_dir)
            if ok:
                count += 1
            else:
                errors.append(err)
        if errors:
            return count, f"Partial errors: {', '.join(errors)}"
        return count, ""

    def list_trash(self) -> List[str]:
        pattern = os.path.join(self.trash_dir, "conversation_*.json")
        try:
            return sorted([os.path.basename(f) for f in glob.glob(pattern)], reverse=True)
        except Exception:
            return []

    def restore_from_trash(self, filename: str) -> Tuple[bool, str]:
        src = os.path.join(self.trash_dir, filename)
        if not os.path.exists(src):
            return False, "File not found in trash"
        return self._move(src, self.base_dir)

    def empty_trash(self) -> Tuple[int, str]:
        files = glob.glob(os.path.join(self.trash_dir, "conversation_*.json"))
        count, errors = 0, []
        for f in files:
            try:
                os.remove(f)
                count += 1
            except Exception as e:
                errors.append(str(e))
        if errors:
            return count, f"Partial errors: {', '.join(errors)}"
        return count, ""