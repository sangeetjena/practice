import time
from concurrent.futures import ThreadPoolExecutor

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from api_interview_lab.platform.app import create_app
from api_interview_lab.platform.config import Settings
from api_interview_lab.platform.store import Store


@pytest.fixture
def factory(tmp_path):
    def build(service='orders', transport=None, telemetry=False):
        cfg = Settings(service=service, database_url=f'sqlite:///{tmp_path / (service + ".db")}',
                       jwt_secret='j' * 40, cursor_secret='c' * 40,
                       credentials={t: {'tenant': t, 'password': 'pw-' + t,
                                        'api_key': 'key-' + t, 'scopes': ['read', 'write']}
                                    for t in ['acme', 'globex']}, telemetry=telemetry)
        db = Store(cfg.database_url)
        db.initialize(service)
        return TestClient(create_app(cfg, db, transport)), cfg, db
    return build


def auth(tenant='acme'):
    return {'X-API-Key': 'key-' + tenant}


@pytest.mark.parametrize('service', ['orders', 'customers', 'products'])
def test_pagination_tenants_and_validation(factory, service):
    client, _, _ = factory(service)
    path = '/api/v1/' + service
    assert client.get(path).status_code == 401
    assert client.get(path, headers=auth(), params={'limit': 101}).status_code == 422
    assert client.get(path, headers=auth(), params={'cursor': 'garbage'}).status_code == 400
    first = client.get(path, headers=auth(), params={'limit': 4}).json()
    cursor = first['next_cursor']
    assert client.get(path, headers=auth('globex'), params={'cursor': cursor}).status_code == 400
    items = first['items']
    while cursor:
        page = client.get(path, headers=auth(), params={'limit': 4, 'cursor': cursor}).json()
        items += page['items']
        cursor = page['next_cursor']
    assert len(items) == len({i['id'] for i in items}) == 15
    assert all(i['name'].startswith('acme') for i in items)
    assert client.get(path + '/missing', headers=auth()).status_code == 404
    assert client.get(path + '/' + items[0]['id'], headers=auth()).status_code == 200


def test_auth_methods_and_bad_tokens(factory):
    client, cfg, _ = factory()
    path = '/api/v1/orders'
    assert client.get(path, auth=('acme', 'pw-acme')).status_code == 200
    assert client.get(path, auth=('acme', 'wrong')).status_code == 401
    claims = {'tenant': 'acme', 'sub': 'test', 'scopes': ['read'], 'iat': int(time.time()),
              'exp': int(time.time()) + 100, 'iss': cfg.issuer, 'aud': cfg.audience}
    def header(c, secret=cfg.jwt_secret):
        return {'Authorization': 'Bearer ' + jwt.encode(c, secret, algorithm='HS256')}
    assert client.get(path, headers=header(claims)).status_code == 200
    for bad in [{**claims, 'exp': 1}, {**claims, 'aud': 'wrong'}, {**claims, 'iss': 'wrong'},
                {**claims, 'scopes': 'read'}, {**claims, 'scopes': None}]:
        assert client.get(path, headers=header(bad)).status_code == 401
    assert client.get(path, headers=header(claims, 'x' * 40)).status_code == 401
    assert client.get(path, headers={**header(claims), **auth()}).status_code == 401
    assert client.post(path, headers=header(claims), json={}).status_code == 403


BODY = {'name': 'new', 'customer_id': 'customers-001', 'product_id': 'products-001',
        'quantity': 2, 'unit_price': 10}


def test_idempotency_and_cross_tenant_read(factory):
    client, _, _ = factory()
    headers = {**auth(), 'Idempotency-Key': 'one'}
    path = '/api/v1/orders'
    first = client.post(path, headers=headers, json=BODY)
    assert first.status_code == 201
    assert client.post(path, headers=headers, json=BODY).json() == first.json()
    assert client.post(path, headers=headers, json={**BODY, 'quantity': 3}).status_code == 409
    assert client.get(path + '/' + first.json()['id'], headers=auth('globex')).status_code == 404
    assert client.post(path, headers=headers, json={**BODY, 'tenant': 'globex'}).status_code == 422
    assert client.post(path, headers=auth(), json=BODY).status_code == 422
    assert client.post(path, headers=headers, json={**BODY, 'quantity': 0}).status_code == 422


def test_concurrent_idempotency_and_restart(factory):
    _, cfg, db = factory()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: db.create_order('acme', 'race', BODY), range(8)))
    assert len({r['id'] for r in results}) == 1
    restarted = Store(cfg.database_url)
    assert restarted.create_order('acme', 'race', BODY) == results[0]


def test_dependency_success_failure_and_timeout(factory):
    def downstream(request):
        assert request.headers['x-api-key'] == 'key-acme'
        return httpx.Response(200, json={'id': 'customers-001', 'name': 'acme customer'})
    client, _, _ = factory(transport=httpx.MockTransport(downstream))
    path = '/api/v1/orders/orders-001/customer'
    assert client.get(path, headers=auth()).status_code == 200
    assert client.get(path).status_code == 401
    assert client.get('/api/v1/orders/missing/customer', headers=auth()).status_code == 404
    client, _, _ = factory(transport=httpx.MockTransport(lambda r: httpx.Response(503)))
    assert client.get(path, headers=auth()).status_code == 502
    def timeout(request):
        raise httpx.ReadTimeout('test', request=request)
    client, _, _ = factory(transport=httpx.MockTransport(timeout))
    assert client.get(path, headers=auth()).status_code == 504


def test_operations_catalog_and_governance(factory, monkeypatch):
    client, _, db = factory()
    metric_calls = []
    monkeypatch.setattr(
        client.app.state.request_counter,
        'add',
        lambda value, attributes: metric_calls.append((value, attributes)),
    )
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 200
    assert client.get('/api/v1/catalog').status_code == 401
    assert len(client.get('/api/v1/catalog', headers=auth()).json()['services']) == 3
    for i in range(20):
        client.get('/random-' + str(i))
    client.get('/api/v1/orders/orders-001', headers=auth())
    assert client.get('/metrics').status_code == 404
    routes = {attributes['route'] for _, attributes in metric_calls}
    assert 'unmatched' in routes
    assert '/api/v1/orders/{item_id}' in routes
    assert all('random-19' not in route for route in routes)
    spec = client.get('/openapi.json').json()
    assert set(spec['components']['securitySchemes']) == {'APIKeyHeader', 'HTTPBasic', 'HTTPBearer'}
    for path, methods in spec['paths'].items():
        if path.startswith('/api/'):
            for operation in methods.values():
                assert operation['security'] and operation['summary'] and operation['tags']
    with db.engine.begin() as conn:
        conn.execute(text('DROP TABLE records'))
    assert client.get('/health/ready').status_code == 503
    assert client.get('/health/live').status_code == 200


def test_trace_propagation_and_safe_logs(factory, monkeypatch, caplog):
    import logging

    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from api_interview_lab.platform import telemetry
    monkeypatch.setenv('OTEL_TRACES_SAMPLER', 'always_on')
    exporter = InMemorySpanExporter()
    monkeypatch.setattr(telemetry, 'OTLPSpanExporter', lambda **kw: exporter)
    seen = {}
    def downstream(request):
        seen['traceparent'] = request.headers.get('traceparent')
        return httpx.Response(200, json={'id': 'customers-001', 'name': 'customer'})
    client, _, _ = factory(transport=httpx.MockTransport(downstream), telemetry=True)
    with caplog.at_level(logging.INFO, logger='platform.requests'), client:
        response = client.get('/api/v1/orders/orders-001/customer', headers=auth())
        assert response.status_code == 200
        client.app.state.tracer_provider.force_flush()
        assert seen['traceparent']
        spans = exporter.get_finished_spans()
        assert len(spans) >= 2
        assert len({span.context.trace_id for span in spans}) == 1
    assert 'key-acme' not in caplog.text
    assert '00000000000000000000000000000000' not in caplog.text


def test_fault_controls(factory):
    client, cfg, _ = factory('customers')
    cfg.fault_fail = True
    assert client.get('/api/v1/customers', headers=auth()).status_code == 503
    cfg.fault_fail = False
    cfg.fault_delay_ms = 5
    assert client.get('/api/v1/customers', headers=auth()).status_code == 200


def test_durable_import_job_and_isolation(factory):
    from api_interview_lab.platform.worker import process_one
    client, cfg, db = factory()
    path = '/api/v1/import-jobs'
    headers = {**auth(), 'Idempotency-Key': 'import-one'}
    response = client.post(path, headers=headers, json={'orders': [BODY, BODY]})
    assert response.status_code == 202
    job_id = response.json()['id']
    assert client.post(path, headers=headers, json={'orders': [BODY, BODY]}).json()['id'] == job_id
    assert client.post(path, headers=headers, json={'orders': [BODY]}).status_code == 409
    assert client.post(path, headers=headers, json={'orders': []}).status_code == 422
    assert client.post(path, json={'orders': [BODY]}).status_code == 401
    assert client.get('/api/v1/jobs/' + job_id, headers=auth('globex')).status_code == 404
    assert client.get('/api/v1/jobs/' + job_id).status_code == 401
    restarted = Store(cfg.database_url)
    assert process_one(restarted)
    result = client.get('/api/v1/jobs/' + job_id, headers=auth()).json()
    assert result['state'] == 'succeeded'
    assert len(result['result']['created_ids']) == 2
    assert not process_one(db)


def test_import_lease_recovery(factory):
    from api_interview_lab.platform.store import jobs, submit_job
    from api_interview_lab.platform.worker import process_one
    _, _, db = factory()
    job = submit_job(db, 'acme', 'lease', [BODY])
    with db.engine.begin() as conn:
        conn.execute(jobs.update().values(state='processing', lease=1, claim='dead-worker'))
    # Simulate a crash after side effect commit but before job completion.
    first = db.create_order('acme', f"job:{job['id']}:0", BODY)
    assert process_one(db, now=100)
    from api_interview_lab.platform.store import read_job
    assert read_job(db, 'acme', job['id'])['result']['created_ids'] == [first['id']]
