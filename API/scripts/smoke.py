"""Live Compose acceptance checks. Start the stack first; exits nonzero on failure."""
import json
import time
from pathlib import Path

import httpx

values = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines() if '=' in line)
users = json.loads(values['CREDENTIALS_JSON'].strip("'"))
headers = {'X-API-Key': users['acme']['api_key']}
with httpx.Client(base_url='http://localhost:8080', timeout=10, trust_env=False) as client:
    for service in ['orders', 'customers', 'products']:
        response = client.get(f'/{service}/api/v1/{service}', headers=headers)
        response.raise_for_status()
        assert len(response.json()['items']) == 5
        assert response.json()['next_cursor']
        assert client.get(f'/{service}/openapi.json').status_code == 200
        assert client.get(f'/{service}/metrics').status_code == 404
    response = client.get('/orders/api/v1/orders/orders-001/customer', headers=headers)
    response.raise_for_status()
    assert response.json()['name'].startswith('acme')
    payload = {'orders': [{'name': 'smoke', 'customer_id': 'customers-001',
                           'product_id': 'products-001', 'quantity': 1, 'unit_price': 10}]}
    response = client.post('/orders/api/v1/import-jobs', json=payload,
                           headers={**headers, 'Idempotency-Key': 'smoke-import'})
    assert response.status_code == 202, response.text
    job_id = response.json()['id']
    for _ in range(30):
        response = client.get('/orders/api/v1/jobs/' + job_id, headers=headers)
        response.raise_for_status()
        if response.json()['state'] == 'succeeded':
            break
        time.sleep(1)
    else:
        raise AssertionError('Import did not complete in 30s')

# The SDK exports every 5s, Collector batches for up to 1s, and Prometheus scrapes every 10s.
with httpx.Client(base_url='http://localhost:9090', timeout=10, trust_env=False) as prometheus:
    for _ in range(30):
        response = prometheus.get('/api/v1/query', params={'query': 'api_requests_total'})
        response.raise_for_status()
        series = response.json()['data']['result']
        services = {item['metric'].get('service') for item in series}
        if {'orders', 'customers', 'products'} <= services:
            break
        time.sleep(1)
    else:
        raise AssertionError('Unified OTLP metrics did not reach Prometheus in 30s')
print('Gateway, services, worker and unified OpenTelemetry metrics passed.')
