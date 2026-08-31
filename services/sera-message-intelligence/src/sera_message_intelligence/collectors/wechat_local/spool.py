from __future__ import annotations
import sqlite3, threading
from pathlib import Path
from ...schemas import MessageEventV1

class SqliteSpool:
    """Durable local outbox on Server Win. Messages survive API/network restarts."""
    def __init__(self, path: str | Path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock=threading.Lock()
        self._conn=sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute("""CREATE TABLE IF NOT EXISTS outbox(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL UNIQUE,
            payload TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_error TEXT
        )""")
        self._conn.execute("""CREATE TABLE IF NOT EXISTS state(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        self._conn.commit()

    def enqueue(self,event:MessageEventV1)->bool:
        payload=event.model_dump_json()
        with self._lock:
            cur=self._conn.execute("INSERT OR IGNORE INTO outbox(fingerprint,payload) VALUES(?,?)",(event.fingerprint,payload))
            self._conn.commit()
            return cur.rowcount==1

    def peek(self,limit:int=100)->list[tuple[int,MessageEventV1]]:
        with self._lock:
            rows=self._conn.execute("SELECT id,payload FROM outbox ORDER BY id LIMIT ?",(limit,)).fetchall()
        return [(i,MessageEventV1.model_validate_json(payload)) for i,payload in rows]

    def ack(self,row_id:int)->None:
        with self._lock:
            self._conn.execute("DELETE FROM outbox WHERE id=?",(row_id,)); self._conn.commit()

    def fail(self,row_id:int,error:str)->None:
        with self._lock:
            self._conn.execute("UPDATE outbox SET attempts=attempts+1,last_error=? WHERE id=?",(error[:1000],row_id)); self._conn.commit()

    def count(self)->int:
        with self._lock:
            return int(self._conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0])

    def get_checkpoint(self)->str|None:
        with self._lock:
            row=self._conn.execute("SELECT value FROM state WHERE key='checkpoint'").fetchone()
        return row[0] if row else None

    def set_checkpoint(self,value:str|None)->None:
        if value is None:return
        with self._lock:
            self._conn.execute("INSERT INTO state(key,value) VALUES('checkpoint',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(value,))
            self._conn.commit()

    def close(self)->None:
        self._conn.close()
