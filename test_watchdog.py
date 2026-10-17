import copy
import unittest
from unittest.mock import patch
import watchdog as w

RUN = 'a' * 32
OBJ = {'id': 7, 'name': 'cleanup-proof-' + RUN, 'labels': {'cleanup-run': RUN},
       'created': '2026-01-01T00:00:00Z', 'applied_to': []}
NOW = 1767225600 + 30


class Fake:
    def __init__(self, obj=None, gone=True, extra=False):
        self.obj = copy.deepcopy(OBJ if obj is None else obj)
        self.gone, self.extra = gone, extra
        self.calls = []
        self.deleted = False

    def call(self, method, path):
        self.calls.append((method, path))
        if '?page=' in path:
            page = int(path.split('page=')[1].split('&')[0])
            return 200, {'firewalls': [self.obj] if self.extra and page == 2 else [],
                         'meta': {'pagination': {'page': page, 'next_page': 2 if page == 1 else None}}}
        if method == 'DELETE':
            self.deleted = True
            return 202, {}
        return (404, {}) if self.deleted and self.gone else (200, {'firewall': self.obj})


class ProofTests(unittest.TestCase):
    def execute(self, api, sleep=lambda _: None):
        out = []
        w.proof(api, 7, RUN, now=lambda: NOW, sleep=sleep, emit=out.append)
        return out

    def test_success_requires_observation_delete_404_and_all_pages(self):
        api = Fake()
        self.assertIn('DELETE_CONFIRMED', self.execute(api)[-1])
        self.assertIn(('GET', '/firewalls?page=2&per_page=50'), api.calls)
        self.assertEqual(sum(m == 'DELETE' for m, _ in api.calls), 1)

    def test_wrong_ownership_fields_never_delete(self):
        for key, value in [('id', 8), ('name', 'other'), ('labels', {}), ('applied_to', [{}]), ('created', '2020-01-01T00:00:00Z')]:
            with self.subTest(key=key):
                api = Fake(dict(OBJ, **{key: value}))
                with self.assertRaises(w.Stop): self.execute(api)
                self.assertFalse(api.deleted)

    def test_future_timestamp_rejected(self):
        with self.assertRaises(w.Stop): self.execute(Fake(dict(OBJ, created='2030-01-01T00:00:00Z')))

    def test_malformed_object_rejected(self):
        with self.assertRaises(w.Stop): self.execute(Fake({}))

    def test_revalidate_after_wait(self):
        api = Fake()
        def change(_): api.obj['labels'] = {}
        with self.assertRaises(w.Stop): self.execute(api, change)
        self.assertFalse(api.deleted)

    def test_no_delete_before_delay(self):
        api = Fake()
        def wait(seconds):
            self.assertEqual(seconds, 60)
            self.assertFalse(api.deleted)
        self.execute(api, wait)

    def test_accepted_is_not_absence(self):
        api = Fake(gone=False)
        with self.assertRaisesRegex(w.Stop, 'ABSENCE_UNVERIFIED'): self.execute(api)
        self.assertEqual(sum(m == 'DELETE' for m, _ in api.calls), 1)

    def test_second_page_remaining_resource_blocks_success(self):
        with self.assertRaisesRegex(w.Stop, 'RESOURCES_REMAIN'): self.execute(Fake(extra=True))

    def test_initial_404_is_not_deletion_proof(self):
        api = Fake(); api.deleted = True
        with self.assertRaisesRegex(w.Stop, 'NO_OBSERVED'): self.execute(api)
        self.assertFalse(any(m == 'DELETE' for m, _ in api.calls))

    def test_invalid_bindings_no_calls(self):
        api = Fake()
        for rid, run in [(0, RUN), (True, RUN), (7, 'bad;echo')]:
            with self.assertRaises(w.Stop): w.proof(api, rid, run)
        self.assertEqual(api.calls, [])

    def test_failed_transport_not_absence(self):
        api = Fake()
        def fail(*_): raise w.Stop('API_HTTP_FAILURE')
        api.call = fail
        with self.assertRaisesRegex(w.Stop, 'API_HTTP_FAILURE'): self.execute(api)

    def test_no_redirect_and_only_fixed_api_operations(self):
        self.assertIsNone(w.NoRedirect().redirect_request(None, None, None, None, None, None))
        api = w.API('a' * 64)
        for method, path in [('POST', '/servers'), ('DELETE', '/servers/7'), ('GET', '//evil.invalid')]:
            with self.assertRaises(w.Stop): api.call(method, path)

    def test_auth_failure_is_sanitized(self):
        api = w.API('a' * 64)
        import urllib.error
        with patch.object(api.opener, 'open', side_effect=urllib.error.HTTPError('url', 401, 'sensitive', {}, None)):
            with self.assertRaisesRegex(w.Stop, '^API_HTTP_FAILURE$'): api.call('GET', '/firewalls/7')


if __name__ == '__main__': unittest.main()
