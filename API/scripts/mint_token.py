"""Local development issuer, not a production login/OAuth server."""
import argparse
import json
import time
from pathlib import Path

import jwt

parser = argparse.ArgumentParser()
parser.add_argument('--tenant', choices=['acme', 'globex'], default='acme')
args = parser.parse_args()
values = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines() if '=' in line)
users = json.loads(values['CREDENTIALS_JSON'].strip("'"))
print(jwt.encode({'sub': args.tenant, 'tenant': args.tenant, 'scopes': users[args.tenant]['scopes'],
                  'iss': 'api-interview-lab', 'aud': 'commerce-api',
                  'iat': int(time.time()), 'exp': int(time.time()) + 900},
                 values['JWT_SECRET'], algorithm='HS256'))
