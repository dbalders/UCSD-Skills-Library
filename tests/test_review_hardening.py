from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import public_pr_review_service as service
import public_skill_validator as validator


class ReviewHardeningTests(unittest.TestCase):
    def test_buffered_completion_is_consumed_without_another_write(self):
        child = '''import json, sys
for line in sys.stdin:
    m = json.loads(line)
    if 'id' not in m:
        continue
    result = {'thread': {'id': 'fixture'}} if m['method'] == 'thread/start' else {}
    messages = [{'id': m['id'], 'result': result}]
    if m['method'] == 'turn/start':
        messages += [
            {'method': 'item/completed', 'params': {'item': {'type': 'agentMessage', 'text': 'Completed fixture review'}}},
            {'method': 'turn/completed', 'params': {'turn': {'status': 'completed'}}},
        ]
    sys.stdout.write(''.join(json.dumps(x) + '\\n' for x in messages))
    sys.stdout.flush()
'''
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / 'fixture.py'
            script.write_text(child)
            result = service.run_codex_app_server([sys.executable, str(script)],
                NS(codex_timeout=2, codex_model='fixture', codex_effort='low'), Path(tmp), 'fixture')
            self.assertEqual(result, 'Completed fixture review')

    def test_symlinked_skill_and_ancestor_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            folder = root / 'community' / 'fixture'
            folder.mkdir(parents=True)
            outside = Path(tmp) / 'outside.md'
            outside.write_text('---\nname: fixture\ndescription: fixture\nmaintainer: fixture\n---\n')
            (folder / 'SKILL.md').symlink_to(outside)
            self.assertFalse(validator.validate_public_skill_format(root).ok)
            self.assertFalse(validator.validate_changed_file_leaks(root, [Path('community/fixture/SKILL.md')]).ok)
            (folder / 'SKILL.md').unlink()
            folder.rmdir()
            folder.symlink_to(outside.parent, target_is_directory=True)
            self.assertFalse(validator.safe_repository_file(root, folder / 'outside.md'))

    def test_prepare_checks_out_captured_sha(self):
        commands = []
        with tempfile.TemporaryDirectory() as tmp, patch.object(service, 'run_or_raise', side_effect=lambda cmd, *a: commands.append(cmd)):
            service.prepare_worktree('origin', 'owner', 'repo', 1, 'main', Path(tmp), None, 'a' * 40, 'b' * 40)
        self.assertEqual(commands[-1][-1], 'a' * 40)
        self.assertIn('b' * 40, commands[0])

    def test_failed_review_is_retried_without_posting_or_recording_success(self):
        pr = {'number': 1, 'title': 'Fixture', 'state': 'open', 'head': {'sha': 'a' * 40}, 'base': {'sha': 'b' * 40}}
        from threading import Lock
        comments = []
        context = NS(client=NS(get_pull=lambda *a: pr, create_review_comment=lambda *a: comments.append(a)),
                     args=NS(skip_drafts=False, force=False, dry_run=False), state={}, state_lock=Lock(),
                     state_dir=Path('/unused'), token=None)
        with patch.object(service, 'review_pull', return_value=('failure', False)):
            with self.assertRaises(RuntimeError):
                service.process_job(context, service.ReviewJob('owner', 'repo', 1, 'a' * 40, 'opened', 'fixture'))
        self.assertEqual(comments, [])
        self.assertEqual(context.state, {})

    def test_stale_head_is_not_published(self):
        pr = {'number': 1, 'state': 'open', 'head': {'sha': 'a' * 40}, 'base': {'sha': 'b' * 40}}
        current = dict(pr, head={'sha': 'c' * 40})
        from threading import Lock
        values = iter([pr, current])
        context = NS(client=NS(get_pull=lambda *a: next(values)), args=NS(skip_drafts=False, force=False),
                     state={}, state_lock=Lock(), state_dir=Path('/unused'), token=None)
        with patch.object(service, 'review_pull', return_value=('completed review', True)):
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                service.process_job(context, service.ReviewJob('owner', 'repo', 1, 'a' * 40, 'opened', 'fixture'))

    def test_installation_identity_and_forced_publication(self):
        client = service.GitHubClient('fixture-installation-token', login='review-app[bot]')
        marker = '<!-- public-review:abcdef -->'
        existing = {'id': 7, 'user': {'login': 'review-app[bot]'}, 'body': marker + ' old result'}
        calls = []
        def request(method, path, payload=None):
            calls.append((method, path, payload))
            self.assertNotEqual(path, '/user')
            return {'id': 8}
        with patch.object(client, 'request', side_effect=request), patch.object(client, 'list_issue_comments', return_value=[existing]):
            self.assertEqual(client.create_review_comment('owner', 'repo', 1, marker + ' new result'), 7)
            self.assertEqual(calls, [])
            self.assertEqual(client.create_review_comment('owner', 'repo', 1, marker + ' new result', force=True), 7)
            self.assertEqual(calls, [('PATCH', '/repos/owner/repo/issues/comments/7', {'body': marker + ' new result'})])
        calls.clear()
        existing['user']['login'] = 'someone-else'
        with patch.object(client, 'request', side_effect=request), patch.object(client, 'list_issue_comments', return_value=[existing]):
            self.assertEqual(client.create_review_comment('owner', 'repo', 1, marker + ' new result', force=True), 8)
            self.assertEqual(calls[0][0], 'POST')

    def test_manual_request_queues_even_while_daemon_owns_state(self):
        import os
        from review_job_store import ReviewStore
        with tempfile.TemporaryDirectory() as tmp:
            lock = service.acquire_service_lock(Path(tmp))
            try:
                argv = ['service', '--review-pr', '12', '--force', '--repo', 'owner/repo', '--state-dir', tmp]
                with patch.object(sys, 'argv', argv), patch.dict(os.environ, {'PR_REVIEW_GITHUB_TOKEN': 'FIXTURE_TOKEN'}, clear=True), \
                     patch.object(service, 'process_job') as process:
                    self.assertEqual(service.main(), 0)
                    process.assert_not_called()
                key, _, payload = ReviewStore(Path(tmp) / 'review-jobs.sqlite3').claim()
                self.assertEqual(key, 'pull_request:owner/repo#12')
                self.assertTrue(payload['force'])
                with patch.object(sys, 'argv', argv + ['--dry-run']), patch.object(service, 'process_job') as process:
                    with self.assertRaisesRegex(RuntimeError, 'separate --state-dir'):
                        service.main()
                    process.assert_not_called()
            finally:
                lock.close()

    def test_issue_edits_labels_and_closure_prevent_stale_publication(self):
        from threading import Lock
        from unittest.mock import Mock
        issue = {'number': 12, 'state': 'open', 'title': 'Fixture', 'body': 'Initial scope', 'labels': [], 'updated_at': 'first'}
        for update in [{'body': 'Changed scope'}, {'labels': [{'name': 'new-scope'}]}, {'state': 'closed'}]:
            with self.subTest(update=update):
                client = NS(get_issue=Mock(side_effect=[issue, dict(issue, **update)]), create_review_comment=Mock())
                context = NS(client=client, args=NS(force=False, dry_run=False), state={}, state_lock=Lock())
                with patch.object(service, 'review_issue', return_value=('Fixture review', True)):
                    with self.assertRaisesRegex(RuntimeError, 'changed or closed'):
                        service.process_issue_job(context, service.ReviewJob('owner', 'repo', 12, '', 'edited', 'event', 'issue'))
                client.create_review_comment.assert_not_called()
                self.assertEqual(context.state, {})

    def test_diff_budget_reduces_context_and_refuses_remaining_oversize(self):
        large = service.CommandResult('PR diff', [], 0, 'x' * 80001)
        compact = service.CommandResult('PR diff', [], 0, 'complete changed lines')
        with patch.object(service, 'run_command', side_effect=[large, compact]) as run:
            self.assertIs(service.review_diff(Path('/unused'), 'a' * 40), compact)
            self.assertIn('--unified=3', run.call_args[0][1])
        with patch.object(service, 'run_command', return_value=large):
            with self.assertRaisesRegex(RuntimeError, 'No partial verdict'):
                service.review_diff(Path('/unused'), 'a' * 40)

    def test_api_mode_has_no_model_tools(self):
        output = {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps({'review_body': 'Fixture result'})}]}]}
        import io
        requests = []
        def fake(request, **kwargs):
            requests.append(json.loads(request.data))
            return io.BytesIO(json.dumps(output).encode())
        with patch.object(service.urllib.request, 'urlopen', side_effect=fake):
            result = service.run_review_api(NS(review_api_url='http://127.0.0.1:1234/responses', codex_model='fixture', codex_effort='low', codex_timeout=10), 'fixture')
        self.assertEqual(result, 'Fixture result')
        self.assertNotIn('tools', requests[0])


if __name__ == '__main__':
    unittest.main()
