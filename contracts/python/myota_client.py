"""Dependency-light typed client for the preferred v1 resource APIs.

This file is intentionally checked in so scripts and service smoke tests can
use the contract without installing an OpenAPI generator.  The method names
mirror the canonical operationIds in ``contracts/openapi.yaml``; ``request``
remains available for operations which are not wrapped yet.
"""

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.request import Request, urlopen
import json
import uuid


@dataclass(frozen=True)
class ApiError(Exception):
    status: int
    body: dict[str, Any]


class MyOTAClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10,
        access_token: str | None = None,
    ) -> None:
        self.base_url, self.timeout, self.access_token = (
            base_url.rstrip("/"),
            timeout,
            access_token,
        )

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        query: Mapping[str, Any] | None = None,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        if query:
            from urllib.parse import urlencode

            path = f"{path}?{urlencode({key: value for key, value in query.items() if value is not None})}"
        payload = None if body is None else json.dumps(body).encode()
        headers = {
            "Accept": "application/json",
            "X-Request-ID": "client-generated",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if expected_version is not None:
            headers["If-Match"] = f'"{expected_version}"'
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        try:
            with urlopen(
                Request(
                    self.base_url + path,
                    data=payload,
                    headers=headers,
                    method=method,
                ),
                timeout=self.timeout,
            ) as response:
                return json.loads(response.read() or b"{}")
        except Exception as exc:
            if hasattr(exc, "read"):
                body_data = json.loads(exc.read() or b"{}")
                raise ApiError(exc.code, body_data) from exc
            raise

    def _write(
        self,
        method: str,
        path: str,
        body: dict[str, Any],
        *,
        idempotency_key: str | None = None,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        return self.request(
            method,
            path,
            body,
            idempotency_key or str(uuid.uuid4()),
            expected_version=expected_version,
        )

    def get_jetstream_status(self) -> dict[str, Any]:
        return self.request("GET", "/v1/operations/jetstream")

    def list_jetstream_snapshots(
        self, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        return self.request(
            "GET",
            "/v1/operations/jetstream/snapshots",
            query={"page": page, "pageSize": page_size},
        )

    # Programme resources
    def patch_programme(
        self, slug: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write("PATCH", f"/v1/programmes/{slug}", body)

    def assign_programme_entity_category(
        self, slug: str, category_code: str
    ) -> dict[str, Any]:
        return self._write(
            "PUT", f"/v1/programmes/{slug}/entity-types/{category_code}", {}
        )

    def unassign_programme_entity_category(
        self, slug: str, category_code: str
    ) -> dict[str, Any]:
        return self._write(
            "DELETE", f"/v1/programmes/{slug}/entity-types/{category_code}", {}
        )

    def patch_programme_content(
        self, slug: str, content_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write(
            "PATCH", f"/v1/programmes/{slug}/content/{content_id}", body
        )

    def patch_programme_policy_draft(
        self, slug: str, draft_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write(
            "PATCH", f"/v1/programmes/{slug}/policy-drafts/{draft_id}", body
        )

    # Identity and geodata resources
    def patch_identity_account(
        self, account_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write(
            "PATCH", f"/v1/identity/accounts/{account_id}", body
        )

    def create_identity_role(self, body: dict[str, Any]) -> dict[str, Any]:
        return self._write("POST", "/v1/identity/roles", body)

    def patch_identity_role(
        self, role_code: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write("PATCH", f"/v1/identity/roles/{role_code}", body)

    def patch_geodata_entity_metadata(
        self,
        entity_id: str,
        body: dict[str, Any],
        *,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        return self._write(
            "PATCH",
            f"/v1/geodata/entities/{entity_id}",
            body,
            expected_version=expected_version,
        )

    def put_geodata_entity_geometry(
        self,
        entity_id: str,
        body: dict[str, Any],
        *,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        return self._write(
            "PUT",
            f"/v1/geodata/entities/{entity_id}/geometry",
            body,
            expected_version=expected_version,
        )

    def put_geodata_entity_categories(
        self,
        entity_id: str,
        body: dict[str, Any],
        *,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        return self._write(
            "PUT",
            f"/v1/geodata/entities/{entity_id}/categories",
            body,
            expected_version=expected_version,
        )

    def post_geodata_entity_review(
        self,
        entity_id: str,
        body: dict[str, Any],
        *,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        return self._write(
            "POST",
            f"/v1/geodata/entities/{entity_id}/reviews",
            body,
            expected_version=expected_version,
        )

    def post_geodata_proposal(self, body: dict[str, Any]) -> dict[str, Any]:
        return self._write("POST", "/v1/geodata/proposals", body)

    def create_geodata_entity_deletion_job(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write("POST", "/v1/geodata/entity-deletion-jobs", body)

    def confirm_geodata_entity_deletion_job(
        self, job_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write(
            "POST", f"/v1/geodata/entity-deletion-jobs/{job_id}/confirm", body
        )

    def patch_award(
        self, award_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return self._write("PATCH", f"/v1/awards/{award_id}", body)
