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

    def test_parallel_claims_do_not_duplicate_jobs(self):
        self.store.enqueue('pr:1', {}, 'a')
        claims = []
        threads = [threading.Thread(target=lambda: claims.append(self.store.claim())) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sum(c is not None for c in claims), 1)
