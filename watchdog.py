"""Free firewall deletion proof only. No provisioning or server support."""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request


class Stop(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class API:
    def __init__(self, token):
        if not re.fullmatch(r'[A-Za-z0-9]{64}', token):
            raise Stop('INVALID_CREDENTIAL_FORMAT')
        self.token = token
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect)

    def call(self, method, path):
        if method not in ('GET', 'DELETE') or not re.fullmatch(r'/firewalls(?:/[1-9][0-9]*|\?page=[1-9][0-9]*&per_page=50)?', path):
            raise Stop('FORBIDDEN_API_OPERATION')
        req = urllib.request.Request('https://api.hetzner.cloud/v1' + path,
                                     method=method, headers={'Authorization': 'Bearer ' + self.token})
        try:
            with self.opener.open(req, timeout=15) as response:
                raw = response.read(1048577)
                if len(raw) > 1048576:
                    raise Stop('OVERSIZED_API_RESPONSE')
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            # Never print bodies, headers, exceptions or credentials.
            if error.code == 404:
                return 404, {}
            raise Stop('API_HTTP_FAILURE') from None
        except (OSError, ValueError):
            raise Stop('API_TRANSPORT_OR_JSON_FAILURE') from None


def validate(obj, resource_id, run_id, now):
    try:
        created = dt.datetime.fromisoformat(obj['created'].replace('Z', '+00:00')).timestamp()
        owned = (obj['id'] == resource_id and obj['name'] == 'cleanup-proof-' + run_id
                 and obj['labels'] == {'cleanup-run': run_id}
                 and obj.get('applied_to') == [] and 0 <= now - created <= 900)
    except (KeyError, ValueError, TypeError, AttributeError):
        owned = False
    if not owned:
        raise Stop('OWNERSHIP_OR_FRESHNESS_MISMATCH')


def list_owned(api, resource_id, run_id):
    for page in range(1, 101):
        status, data = api.call('GET', f'/firewalls?page={page}&per_page=50')
        if status != 200 or not isinstance(data.get('firewalls'), list):
            raise Stop('LIST_UNVERIFIED')
        for obj in data['firewalls']:
            if obj.get('id') == resource_id or obj.get('labels', {}).get('cleanup-run') == run_id or obj.get('name') == 'cleanup-proof-' + run_id:
                return True
        pages = data.get('meta', {}).get('pagination', {})
        if pages.get('page') != page or 'next_page' not in pages:
            raise Stop('PAGINATION_UNVERIFIED')
        nxt = pages['next_page']
        if nxt is None:
            return False
        if nxt != page + 1:
            raise Stop('PAGINATION_UNVERIFIED')
    raise Stop('PAGINATION_BOUND_EXCEEDED')


def proof(api, resource_id, run_id, now=time.time, sleep=time.sleep, emit=print):
    if type(resource_id) is not int or resource_id <= 0 or not re.fullmatch(r'[a-f0-9]{32}', run_id):
        raise Stop('INVALID_BINDING')
    path = f'/firewalls/{resource_id}'
    status, data = api.call('GET', path)
    if status != 200:
        raise Stop('NO_OBSERVED_RESOURCE_NO_PROOF')
    validate(data.get('firewall'), resource_id, run_id, now())
    emit('BOUND_READY; FREE_FIREWALL_ONLY; DELETE_IN_60_SECONDS')
    sleep(60)  # Independent runner remains alive while local observer may disconnect.
    status, data = api.call('GET', path)
    if status != 200:
        raise Stop('RESOURCE_CHANGED_BEFORE_DELETE')
    validate(data.get('firewall'), resource_id, run_id, now())
    status, _ = api.call('DELETE', path)
    if status not in (200, 202, 204):
        raise Stop('DELETE_NOT_ACCEPTED')
    for _ in range(20):
        status, _ = api.call('GET', path)
        if status == 404:
            if list_owned(api, resource_id, run_id):
                raise Stop('OWNED_RESOURCES_REMAIN')
            emit('DELETE_CONFIRMED; KNOWN_ID_404; ALL_LIST_PAGES_ABSENT')
            return
        if status != 200:
            raise Stop('ABSENCE_UNVERIFIED')
        sleep(3)
    raise Stop('DELETE_ACCEPTED_BUT_ABSENCE_UNVERIFIED')


if __name__ == '__main__':
    try:
        proof(API(os.environ.get('HCLOUD_TOKEN', '')), int(os.environ.get('FIREWALL_ID', '0')),
              os.environ.get('CLEANUP_RUN', ''))
    except (Stop, ValueError) as error:
        # Stop messages are fixed constants; do not print arbitrary exceptions.
        print('STOP: ' + (str(error) if isinstance(error, Stop) else 'INVALID_INPUT'))
        sys.exit(1)
    except Exception:
        print('STOP: UNCLASSIFIED_FAILURE_NO_DELETION_PROOF')
        sys.exit(1)
