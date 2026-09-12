import sys, tempfile, threading, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from review_job_store import ReviewStore


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = ReviewStore(Path(self.tmp.name) / 'jobs.sqlite3')

    def test_active_update_is_coalesced_without_concurrent_execution(self):
        self.assertTrue(self.store.enqueue('pr:1', {'head': 'a'}, 'a'))
        key, generation, _ = self.store.claim()
        self.store.enqueue(key, {'head': 'b'}, 'b')
        self.store.enqueue(key, {'head': 'c'}, 'c')
        self.assertIsNone(self.store.claim())
        self.store.finish(key, generation)
        self.assertEqual(self.store.claim()[2], {'head': 'c'})

    def test_restart_recovers_running_and_pending_jobs(self):
        self.store.enqueue('pr:1', {'head': 'a'}, 'a')
        self.store.claim()
        other = ReviewStore(self.store.path)
        other.recover()
        self.assertEqual(other.claim()[2], {'head': 'a'})

    def test_deliveries_are_idempotent_across_restart(self):
        self.store.enqueue('pr:1', {}, 'delivery')
        self.assertFalse(ReviewStore(self.store.path).enqueue('pr:1', {}, 'delivery'))

    def test_failure_retries_then_records_failure_instead_of_success(self):
        self.store.enqueue('pr:1', {}, 'a')
        for attempt in range(5):
            key, generation, _ = self.store.claim()
            self.store.finish(key, generation, 'Synthetic outage')
            with self.store.connect() as db:
                db.execute('UPDATE jobs SET ready=0')
        self.assertIsNone(self.store.claim())
        self.assertEqual(self.store.health()['failed'], 1)
        self.assertEqual(self.store.health()['last_success'], 0)
        self.store.enqueue('pr:1', {'head': 'b'}, 'b')
        self.assertIsNotNone(self.store.claim())

    def test_last_success_survives_new_work_and_restart(self):
        self.store.enqueue('pr:1', {}, 'initial')
        key, generation, _ = self.store.claim()
        self.store.finish(key, generation)
        last_success = self.store.health()['last_success']
        self.assertGreater(last_success, 0)
        self.store.enqueue(key, {}, 'next')
        self.store.claim()
        self.assertEqual(ReviewStore(self.store.path).health()['last_success'], last_success)

    def test_terminal_redelivery_requeues_only_its_matching_generation(self):
        self.store.enqueue('pr:1', {'head': 'old'}, 'old-delivery')
        self.store.enqueue('pr:1', {'head': 'current'}, 'current-delivery')
        key, generation, _ = self.store.claim()
        with self.store.connect() as db:
            db.execute('UPDATE jobs SET attempts=4')
        self.store.finish(key, generation, 'Synthetic terminal failure')
        self.assertEqual(self.store.health()['failed'], 1)
        self.assertFalse(self.store.enqueue(key, {'head': 'old'}, 'old-delivery'))
        self.assertTrue(self.store.enqueue(key, {'head': 'current'}, 'current-delivery'))
        self.assertEqual(self.store.health()['failed'], 0)
        self.assertFalse(self.store.enqueue(key, {'head': 'current'}, 'current-delivery'))
        key, generation, payload = self.store.claim()
        self.assertEqual(payload['head'], 'current')
        self.assertFalse(self.store.enqueue(key, payload, 'current-delivery'))
        self.store.finish(key, generation)
        self.assertFalse(self.store.enqueue(key, payload, 'current-delivery'))

    def test_concurrent_first_start_creates_complete_schema(self):
        path = Path(self.tmp.name) / 'concurrent.sqlite3'
        barrier = threading.Barrier(8)
        errors = []
        def initialize(i):
            try:
                barrier.wait()
                ReviewStore(path).enqueue(f'pr:{i}', {}, f'delivery-{i}')
            except Exception as error:
                errors.append(error)
        threads = [threading.Thread(target=initialize, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(ReviewStore(path).health()['pending'], 8)

    def test_existing_delivery_schema_upgrades_without_losing_deduplication(self):
        import sqlite3
        path = Path(self.tmp.name) / 'legacy.sqlite3'
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE deliveries (id TEXT PRIMARY KEY, received REAL NOT NULL)')
            db.execute('INSERT INTO deliveries VALUES (?, ?)', ('legacy-event', 1))
        store = ReviewStore(path)
        self.assertFalse(store.enqueue('pr:1', {}, 'legacy-event'))
        self.assertTrue(store.enqueue('pr:1', {}, 'new-event'))
        self.assertEqual(store.claim()[2], {})

    def test_parallel_claims_do_not_duplicate_jobs(self):
        self.store.enqueue('pr:1', {}, 'a')
        claims = []
        threads = [threading.Thread(target=lambda: claims.append(self.store.claim())) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sum(c is not None for c in claims), 1)
