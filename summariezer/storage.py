from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import closing
from pathlib import Path

from .models import Message


class MessageStore:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        source TEXT NOT NULL,
                        message_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        author TEXT NOT NULL,
                        text TEXT NOT NULL,
                        url TEXT,
                        reply_to TEXT,
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (source, message_id)
                    )
                    """
                )
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS idx_messages_source_date ON messages (source, date)"
                )

    def upsert_messages(self, messages: Iterable[Message]) -> int:
        rows = [
            (
                message.source,
                message.message_id,
                message.date,
                message.author,
                message.text,
                message.url,
                message.reply_to,
                json.dumps(message.metadata, sort_keys=True),
            )
            for message in messages
        ]
        if not rows:
            return 0

        with closing(self._connect()) as connection:
            with connection:
                connection.executemany(
                    """
                    INSERT INTO messages (
                        source, message_id, date, author, text, url, reply_to, metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, message_id) DO UPDATE SET
                        date = excluded.date,
                        author = excluded.author,
                        text = excluded.text,
                        url = excluded.url,
                        reply_to = excluded.reply_to,
                        metadata_json = excluded.metadata_json,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    rows,
                )
        return len(rows)

    def fetch_messages(self, source: str, start: str, end: str) -> list[Message]:
        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                SELECT source, message_id, date, author, text, url, reply_to, metadata_json
                FROM messages
                WHERE source = ? AND date >= ? AND date < ?
                ORDER BY date ASC, CAST(message_id AS INTEGER) ASC, message_id ASC
                """,
                (source, start, end),
            )
            return [self._row_to_message(row) for row in cursor.fetchall()]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_message(row: sqlite3.Row) -> Message:
        return Message(
            source=row["source"],
            message_id=row["message_id"],
            date=row["date"],
            author=row["author"],
            text=row["text"],
            url=row["url"],
            reply_to=row["reply_to"],
            metadata=json.loads(row["metadata_json"] or "{}"),
        )
