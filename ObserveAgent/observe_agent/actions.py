"""Policy-constrained action planning and execution for the incident graph."""

from __future__ import annotations

import hashlib
import ipaddress
import smtplib
from email.message import EmailMessage
from typing import Any
from urllib.parse import urlparse

import httpx

from .config import Settings
from .knowledge import SQLiteKnowledgeStore
from .models import (
    ActionMode,
    ActionRequest,
    ActionResult,
    ActionStatus,
    ActionType,
    Incident,
    TriageReport,
)


class ActionPolicy:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, action: ActionRequest) -> None:
        if action.action_type.value not in self.settings.action_allowlist:
            raise ValueError(f"action type {action.action_type.value!r} is not allowlisted")
        if action.action_type == ActionType.HTTP_GET:
            self._validate_http_url(action.parameters.get("url", ""))
        elif action.action_type == ActionType.GITHUB_PULL_REQUEST:
            repository = action.parameters.get("repository", "")
            if repository not in self.settings.github_allowed_repositories:
                raise ValueError(f"GitHub repository {repository!r} is not allowlisted")
        elif action.action_type == ActionType.EMAIL:
            recipient = action.parameters.get("to", "")
            if recipient not in self.settings.email_allowed_recipients:
                raise ValueError(f"email recipient {recipient!r} is not allowlisted")

    def _validate_http_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("diagnostic URL must be HTTPS with no embedded credentials")
        if parsed.hostname not in self.settings.http_allowed_hosts:
            raise ValueError(f"HTTP host {parsed.hostname!r} is not allowlisted")
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            return
        if not address.is_global:
            raise ValueError("private, loopback, and link-local HTTP targets are forbidden")


class ActionPlanner:
    """Maps trusted operator-supplied targets to tools after diagnosis."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def plan(self, incident: Incident, report: TriageReport) -> list[ActionRequest]:
        if (
            not report.hypotheses
            or report.hypotheses[0].confidence < self.settings.action_min_confidence
        ):
            return []
        context = incident.action_context
        candidates: list[tuple[ActionType, str, dict[str, str], str]] = []
        if context.get("diagnostic_url"):
            candidates.append(
                (
                    ActionType.HTTP_GET,
                    "Collect read-only diagnostic information",
                    {"url": context["diagnostic_url"]},
                    "low",
                )
            )
        if all(context.get(key) for key in ("github_repository", "github_head")):
            candidates.append(
                (
                    ActionType.GITHUB_PULL_REQUEST,
                    "Open a pull request for an already prepared remediation branch",
                    {
                        "repository": context["github_repository"],
                        "head": context["github_head"],
                        "base": context.get("github_base", "master"),
                        "title": context.get("github_title", f"Remediate {incident.id}"),
                        "body": context.get("github_body", report.summary),
                    },
                    "medium",
                )
            )
        if context.get("notify_email"):
            candidates.append(
                (
                    ActionType.EMAIL,
                    "Notify the approved incident recipient",
                    {
                        "to": context["notify_email"],
                        "subject": context.get("email_subject", f"Incident {incident.id} triage"),
                        "body": context.get("email_body", report.summary),
                    },
                    "medium",
                )
            )

        actions: list[ActionRequest] = []
        for action_type, description, parameters, risk in candidates:
            if action_type.value not in self.settings.action_allowlist:
                continue
            digest = hashlib.sha256(
                f"{incident.id}:{action_type.value}:{sorted(parameters.items())}".encode()
            ).hexdigest()[:20]
            actions.append(
                ActionRequest(
                    id=f"action-{digest}",
                    incident_id=incident.id,
                    action_type=action_type,
                    description=description,
                    parameters=parameters,
                    risk=risk,
                )
            )
        return actions


class ActionExecutor:
    def __init__(self, settings: Settings, store: SQLiteKnowledgeStore) -> None:
        self.settings = settings
        self.store = store
        self.policy = ActionPolicy(settings)

    def execute(self, action: ActionRequest) -> ActionResult:
        existing = self.store.get_action_result(action.id)
        if existing is not None:
            return existing
        try:
            self.policy.validate(action)
            if self.settings.action_mode == ActionMode.DRY_RUN:
                result = ActionResult(
                    action_id=action.id,
                    status=ActionStatus.DRY_RUN,
                    message="Validated only; ACTION_MODE=dry_run prevented the external call.",
                    output={"parameters": _redacted_parameters(action)},
                )
            else:
                result = self._execute_live(action)
        except (ValueError, httpx.HTTPError, OSError, smtplib.SMTPException) as error:
            result = ActionResult(
                action_id=action.id,
                status=ActionStatus.FAILED,
                message=str(error),
            )
        self.store.save_action_result(result)
        return result

    def _execute_live(self, action: ActionRequest) -> ActionResult:
        if action.action_type == ActionType.HTTP_GET:
            return self._http_get(action)
        if action.action_type == ActionType.GITHUB_PULL_REQUEST:
            return self._github_pull_request(action)
        return self._send_email(action)

    def _http_get(self, action: ActionRequest) -> ActionResult:
        with httpx.Client(timeout=5, follow_redirects=False, trust_env=False) as client:
            response = client.get(action.parameters["url"], headers={"Accept": "application/json"})
            response.raise_for_status()
        body = response.text[:16_000]
        return ActionResult(
            action_id=action.id,
            status=ActionStatus.SUCCEEDED,
            message="Diagnostic API call completed.",
            output={"status_code": response.status_code, "body": body},
        )

    def _github_pull_request(self, action: ActionRequest) -> ActionResult:
        if not self.settings.github_token:
            raise ValueError("GITHUB_TOKEN is required in execute mode")
        repository = action.parameters["repository"]
        with httpx.Client(timeout=10, follow_redirects=False, trust_env=False) as client:
            response = client.post(
                f"https://api.github.com/repos/{repository}/pulls",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.settings.github_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "head": action.parameters["head"],
                    "base": action.parameters["base"],
                    "title": action.parameters["title"],
                    "body": action.parameters["body"],
                },
            )
            response.raise_for_status()
        payload = response.json()
        return ActionResult(
            action_id=action.id,
            status=ActionStatus.SUCCEEDED,
            message="GitHub pull request opened.",
            output={"number": payload.get("number"), "url": payload.get("html_url")},
        )

    def _send_email(self, action: ActionRequest) -> ActionResult:
        if not self.settings.smtp_host or not self.settings.smtp_from:
            raise ValueError("SMTP_HOST and SMTP_FROM are required in execute mode")
        message = EmailMessage()
        message["From"] = self.settings.smtp_from
        message["To"] = action.parameters["to"]
        message["Subject"] = action.parameters["subject"]
        message.set_content(action.parameters["body"])
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)
        return ActionResult(
            action_id=action.id,
            status=ActionStatus.SUCCEEDED,
            message="Email sent.",
            output={"to": action.parameters["to"]},
        )


def _redacted_parameters(action: ActionRequest) -> dict[str, Any]:
    return {key: value for key, value in action.parameters.items() if "token" not in key.lower()}
