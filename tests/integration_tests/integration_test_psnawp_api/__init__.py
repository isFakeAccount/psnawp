import json
from contextlib import suppress

import vcr
from requests import Response
from vcr.record_mode import RecordMode


def filter_response_information(response: Response) -> Response:
    """Filters response information from the given data. This is useful for logging communication with the API.

    :param response: The data to redact.

    :returns: data with sensitive information redacted.

    """
    hide_params = ["access_token", "id_token", "refresh_token"]
    # vcr throws error if multipart form data is received as binary https://github.com/kevin1024/vcrpy/issues/521
    with suppress(UnicodeDecodeError):
        if not isinstance(response, dict):
            return response

        response["headers"]["Set-Cookie"] = "REDACTED"

        response_body = response.get("body").get("string")
        if not response_body:
            return response

        response_body = json.loads(response_body)
        if isinstance(response_body, dict):
            for param in hide_params:
                if response_body.get(param, None):
                    response_body[param] = "REDACTED"
        response["body"]["string"] = json.dumps(response_body).encode("utf-8")

    return response


my_vcr = vcr.VCR(
    serializer="yaml",
    cassette_library_dir="tests/integration_tests/integration_test_psnawp_api/cassettes",
    record_mode=RecordMode.ONCE,
    match_on=["uri", "method"],
    filter_headers=["Authorization", "Cookie", "Set-Cookie"],
    filter_post_data_parameters=["refresh_token", "code"],
    before_record_response=filter_response_information,
)
