from __future__ import annotations

# Tokens below are deliberately fake; these tests never connect to PSN.
# ruff: noqa: S105, PLR2004
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from pyrate_limiter import Duration, Rate

from psnawp_api import PSNAWP
from psnawp_api.core import PSNAWPAuthenticationError
from psnawp_api.core.authenticator import Authenticator

if TYPE_CHECKING:
    from collections.abc import Iterator

    from psnawp_api.core.authenticator import TokenResponse
    from psnawp_api.core.request_builder import RequestBuilderHeaders

NOW = 1800000000.0
TOKEN: TokenResponse = {
    "access_token": "test-access",
    "refresh_token": "test-refresh",
    "access_token_expires_at": NOW + 3600,
    "refresh_token_expires_at": NOW + 5184000,
    "expires_in": 3600,
    "refresh_token_expires_in": 5184000,
    "id_token": "test-id",
    "scope": "psn:mobile.v2.core psn:clientapp",
    "token_type": "bearer",
}
HEADERS: RequestBuilderHeaders = {"User-Agent": "test", "Accept-Language": "en", "Country": "US"}
URL = "https://example.invalid/resource"


@pytest.fixture(autouse=True)
def request_builder() -> Iterator[MagicMock]:
    # Keep token lifecycle tests independent of network requests and the rate-limit database.
    with patch("psnawp_api.core.authenticator.RequestBuilder", autospec=True) as builder:
        with patch("psnawp_api.core.authenticator.time.time", return_value=NOW):
            yield builder.return_value


@pytest.mark.unit
def test_constructor_copies_tokens_and_preserves_expiration(request_builder: MagicMock) -> None:
    saved = TOKEN.copy()
    client = PSNAWP("unused-npsso", token_response=saved)
    assert client.authenticator.token_response == TOKEN
    assert client.authenticator.token_response is not saved
    assert client.authenticator.access_token_expiration_time == TOKEN["access_token_expires_at"]
    assert client.authenticator.refresh_token_expiration_time == TOKEN["refresh_token_expires_at"]
    saved["access_token"] = "caller-changed"
    assert client.authenticator.token_response["access_token"] == "test-access"
    client.authenticator.token_response["refresh_token"] = "client-changed"
    assert saved["refresh_token"] == "test-refresh"
    assert request_builder.mock_calls == []


@pytest.mark.unit
def test_authenticator_accepts_tokens_directly() -> None:
    auth = Authenticator("unused-npsso", HEADERS, Rate(1, Duration.SECOND), token_response=TOKEN)
    assert auth.token_response == TOKEN
    assert auth.token_response is not TOKEN


@pytest.mark.unit
def test_existing_positional_arguments_remain_supported(request_builder: MagicMock) -> None:
    rate = Rate(1, Duration.SECOND)
    client = PSNAWP("npsso", HEADERS, rate)
    assert client.authenticator.token_response is None
    assert client.authenticator.npsso_cookie == "npsso"
    assert client.authenticator.common_headers == HEADERS
    assert request_builder.mock_calls == []


@pytest.mark.unit
@pytest.mark.parametrize("method", ["get", "post", "patch", "delete", "put"])
def test_valid_token_skips_npsso_and_refresh(request_builder: MagicMock, method: str) -> None:
    auth = PSNAWP("expired-npsso", token_response=TOKEN).authenticator
    request = getattr(request_builder, method)
    assert getattr(auth, method)(url=URL) is request.return_value
    assert len(request_builder.mock_calls) == 1
    request.assert_called_once_with(url=URL, headers={"Authorization": "Bearer test-access"})


@pytest.mark.unit
@pytest.mark.parametrize("expiry", [NOW - 1, NOW])
def test_expired_access_token_refreshes_without_npsso(request_builder: MagicMock, expiry: float) -> None:
    saved = TOKEN.copy()
    saved["access_token_expires_at"] = expiry
    refreshed = TOKEN.copy()
    refreshed["access_token"] = "rotated-access"
    refreshed["refresh_token"] = "rotated-refresh"
    del refreshed["access_token_expires_at"]
    del refreshed["refresh_token_expires_at"]
    request_builder.post.return_value.json.return_value = refreshed
    auth = PSNAWP("expired-npsso", token_response=saved).authenticator

    auth.get(url=URL)

    request_builder.post.assert_called_once()
    assert request_builder.post.call_args.kwargs["data"]["refresh_token"] == "test-refresh"
    assert request_builder.post.call_args.kwargs["data"]["grant_type"] == "refresh_token"
    request_builder.get.assert_called_once_with(url=URL, headers={"Authorization": "Bearer rotated-access"})
    assert auth.token_response is not None
    assert auth.token_response["access_token_expires_at"] == NOW + 3600
    assert auth.token_response["refresh_token"] == "rotated-refresh"
    assert saved["access_token_expires_at"] == expiry
    assert saved["refresh_token"] == "test-refresh"


@pytest.mark.unit
def test_missing_access_expiration_refreshes_instead_of_extending_it(request_builder: MagicMock) -> None:
    saved = TOKEN.copy()
    del saved["access_token_expires_at"]
    request_builder.post.return_value.json.return_value = TOKEN.copy()
    auth = PSNAWP("expired-npsso", token_response=saved).authenticator
    auth.get(url=URL)
    request_builder.post.assert_called_once()
    assert "access_token_expires_at" not in saved


@pytest.mark.unit
def test_rejected_refresh_propagates_without_retrying_npsso(request_builder: MagicMock) -> None:
    saved = TOKEN.copy()
    saved["access_token_expires_at"] = NOW - 1
    request_builder.post.side_effect = PSNAWPAuthenticationError("revoked")
    auth = PSNAWP("expired-npsso", token_response=saved).authenticator
    with pytest.raises(PSNAWPAuthenticationError, match="revoked"):
        auth.get(url=URL)
    request_builder.post.assert_called_once()
    request_builder.get.assert_not_called()
    assert auth.token_response == saved


@pytest.mark.unit
def test_no_tokens_retains_npsso_bootstrap(request_builder: MagicMock) -> None:
    request_builder.get.return_value.headers = {"location": "https://example.invalid/callback?code=test-code"}
    request_builder.post.return_value.json.return_value = TOKEN.copy()
    auth = PSNAWP("test-npsso").authenticator
    auth.get(url=URL)
    assert request_builder.get.call_count == 2
    assert request_builder.get.call_args_list[0].kwargs["headers"]["Cookie"] == "npsso=test-npsso"
    request_builder.post.assert_called_once()
    assert request_builder.post.call_args.kwargs["data"]["grant_type"] == "authorization_code"
    assert request_builder.post.call_args.kwargs["data"]["code"] == "test-code"
