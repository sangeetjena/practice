"""Executable design-time governance. Run in CI before deployment."""
from api_interview_lab.platform.app import create_app
from api_interview_lab.platform.config import Settings


def validate(spec):
    errors = []
    for path, methods in spec['paths'].items():
        if not path.startswith('/api/'):
            continue
        if not path.startswith('/api/v1/'):
            errors.append(f'{path}: missing version prefix')
        for method, operation in methods.items():
            for field in ['security', 'summary', 'tags', 'operationId']:
                if not operation.get(field):
                    errors.append(f'{method} {path}: missing {field}')
            if method == 'post' and not any(
                p.get('name') == 'idempotency-key' for p in operation.get('parameters', [])):
                errors.append(f'{path}: missing idempotency contract')
    return errors


if __name__ == '__main__':
    errors = []
    for service in ['orders', 'customers', 'products']:
        cfg = Settings(service=service, jwt_secret='test-only-' * 5,
                       cursor_secret='cursor-only-' * 5)
        app = create_app(cfg)
        errors.extend(validate(app.openapi()))
        app.state.store.engine.dispose()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Governance passed: versioning, auth, ownership tags, summaries, idempotency.')
