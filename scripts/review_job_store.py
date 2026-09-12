"""Crash-recoverable latest-revision jobs and content-addressed review results."""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


class ReviewStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS service_status (name TEXT PRIMARY KEY, value REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS jobs (
                    key TEXT PRIMARY KEY, payload TEXT NOT NULL, generation INTEGER NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0, running INTEGER,
                    attempts INTEGER NOT NULL DEFAULT 0, ready REAL NOT NULL DEFAULT 0,
                    updated REAL NOT NULL, error TEXT, finished REAL, phase TEXT);
                CREATE TABLE IF NOT EXISTS deliveries (id TEXT PRIMARY KEY, received REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, payload TEXT NOT NULL, created REAL NOT NULL);
            ''')
            db.execute("INSERT INTO service_status VALUES ('last_success', (SELECT COALESCE(MAX(finished),0) FROM jobs WHERE phase='done')) ON CONFLICT(name) DO UPDATE SET value=MAX(service_status.value,excluded.value)")
        path.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA synchronous=FULL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def recover(self):
        # Called only after acquiring the service's exclusive process lock.
        with self.connect() as db:
            db.execute("UPDATE jobs SET running=NULL, ready=0, phase='recovered' WHERE running IS NOT NULL")
            db.execute('DELETE FROM deliveries WHERE received < ?', (time.time() - 30 * 86400,))

    def enqueue(self, key, payload, delivery):
        now = time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if delivery and delivery != 'manual':
                if db.execute('SELECT 1 FROM deliveries WHERE id=?', (delivery,)).fetchone():
                    return False
                db.execute('INSERT INTO deliveries VALUES (?,?)', (delivery, now))
            db.execute('''INSERT INTO jobs(key,payload,generation,updated) VALUES(?,?,1,?)
                ON CONFLICT(key) DO UPDATE SET payload=excluded.payload,generation=jobs.generation+1,
                attempts=0,ready=0,updated=excluded.updated,error=NULL''',
                (key, json.dumps(payload), now))
        return True

    def claim(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('''SELECT * FROM jobs WHERE generation>completed AND running IS NULL
                AND ready<=? ORDER BY updated LIMIT 1''', (time.time(),)).fetchone()
            if row is None:
                return None
            db.execute("UPDATE jobs SET running=generation,phase='processing' WHERE key=?", (row['key'],))
            return row['key'], row['generation'], json.loads(row['payload'])

    def finish(self, key, generation, error=None):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM jobs WHERE key=? AND running=?', (key, generation)).fetchone()
            if row is None:
                return
            if row['generation'] > generation:
                db.execute("UPDATE jobs SET running=NULL,completed=?,ready=0,phase='pending' WHERE key=?", (generation, key))
                outcome = 'pending'
            elif error and row['attempts'] < 4:
                db.execute("UPDATE jobs SET running=NULL,attempts=attempts+1,error=?,ready=?,phase='retry' WHERE key=?",
                           (str(error)[:500], time.time() + min(1800, 30 * 2 ** row['attempts']), key))
                outcome = 'retry'
            else:
                db.execute("UPDATE jobs SET running=NULL,completed=?,error=?,finished=?,phase=? WHERE key=?",
                           (generation, str(error)[:500] if error else None, time.time(), 'failed' if error else 'done', key))
                outcome = 'failed' if error else 'done'
            if outcome == 'done':
                db.execute("INSERT INTO service_status VALUES ('last_success', ?) ON CONFLICT(name) DO UPDATE SET value=excluded.value", (time.time(),))
        return outcome

    def get(self, key):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM cache WHERE key=?', (key,)).fetchone()
            return json.loads(row['payload']) if row else None

    def put(self, key, payload):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO cache VALUES (?,?,?)', (key, json.dumps(payload), time.time()))

    def health(self):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM jobs').fetchall()
            last_success = db.execute("SELECT value FROM service_status WHERE name='last_success'").fetchone()[0]
        pending = [r for r in rows if r['generation'] > r['completed']]
        return {
            'active': sum(r['running'] is not None for r in rows),
            'pending': len(pending),
            'retrying': sum(r['phase'] == 'retry' for r in pending),
            'failed': sum(r['phase'] == 'failed' for r in rows),
            'oldest_pending_seconds': int(time.time() - min(r['updated'] for r in pending)) if pending else 0,
            'last_success': last_success,
        }
