"""Small SQLite state index used to make resume explicit."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS episodes (episode_id TEXT PRIMARY KEY, status TEXT NOT NULL)"
            )

    def mark_completed(self, episode_id: str) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "INSERT INTO episodes(episode_id, status) VALUES(?, 'completed') "
                "ON CONFLICT(episode_id) DO UPDATE SET status='completed'",
                (episode_id,),
            )

    def completed_ids(self) -> set[str]:
        with sqlite3.connect(self.path) as connection:
            rows = connection.execute("SELECT episode_id FROM episodes WHERE status='completed'").fetchall()
        return {row[0] for row in rows}

