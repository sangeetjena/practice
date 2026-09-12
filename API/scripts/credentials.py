"""Print one local demo credential for curl/Postman; never use in logs/CI."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--tenant', choices=['acme', 'globex'], default='acme')
p.add_argument('--kind', choices=['api_key', 'password'], default='api_key')
a = p.parse_args()
v = dict(line.split('=', 1) for line in Path('.env').read_text().splitlines() if '=' in line)
print(json.loads(v['CREDENTIALS_JSON'].strip("'"))[a.tenant][a.kind])
