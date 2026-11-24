from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class Ledger:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, text TEXT NOT NULL, trust_mode TEXT NOT NULL, plan TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS actions (id TEXT PRIMARY KEY, event_id TEXT NOT NULL, tool TEXT NOT NULL, tier TEXT NOT NULL, status TEXT NOT NULL, input_json TEXT NOT NULL, result_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, event_id TEXT NOT NULL, source TEXT NOT NULL, title TEXT NOT NULL, snippet TEXT NOT NULL, url TEXT, trusted INTEGER NOT NULL);
        """)
        self.db.commit()

    def save_event(self, event_id: str, text: str, trust_mode: str, plan: dict[str, Any]) -> None:
        self.db.execute("INSERT OR REPLACE INTO events(id,text,trust_mode,plan) VALUES(?,?,?,?)", (event_id, text, trust_mode, json.dumps(plan)))
        self.db.commit()

    def save_action(self, event_id: str, action_id: str, tool: str, tier: str, status: str, args: dict[str, Any], result: Any = None) -> None:
        self.db.execute("INSERT OR REPLACE INTO actions(id,event_id,tool,tier,status,input_json,result_json) VALUES(?,?,?,?,?,?,?)", (action_id, event_id, tool, tier, status, json.dumps(args), json.dumps(result) if result is not None else None))
        self.db.commit()

    def list_actions(self, event_id: str) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.execute("SELECT * FROM actions WHERE event_id=? ORDER BY created_at", (event_id,))]

    def receipts(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.execute("SELECT * FROM actions ORDER BY created_at DESC LIMIT 100")]

    def action(self, action_id: str) -> dict[str, Any] | None:
        row = self.db.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        return dict(row) if row else None
