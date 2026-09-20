import re


def read_secret(version_name: str) -> str:
    """Fetch using the attached runtime identity. Never serialize this result in a job graph."""
    if not re.fullmatch(r"projects/[^/]+/secrets/[^/]+/versions/[1-9][0-9]*", version_name):
        raise ValueError("Expected a fully qualified, numeric Secret Manager version")
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": version_name})
    return response.payload.data.decode("utf-8")
