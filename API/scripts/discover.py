"""Discover declared endpoints from a fixed trusted catalog, then probe readiness.
Not a network scanner: never accept arbitrary hosts from untrusted API responses.
"""
import asyncio
import os

import httpx


async def main():
    async with httpx.AsyncClient(base_url='http://localhost:8080', timeout=3,
                                headers={'X-API-Key': os.environ['DEMO_API_KEY']}) as client:
        response = await client.get('/orders/api/v1/catalog')
        response.raise_for_status()
        for entry in response.json()['services']:
            name = entry['name']
            if name not in {'orders', 'customers', 'products'}:
                raise ValueError('Untrusted catalog service')
            spec = await client.get(f'/{name}/openapi.json')
            spec.raise_for_status()
            ready = await client.get(f'/{name}/health/ready')
            print({'service': name, 'ready': ready.status_code == 200,
                   'declared_endpoints': sorted(spec.json()['paths'])})


if __name__ == '__main__':
    asyncio.run(main())
