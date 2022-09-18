import json

import vcr
from contextlib import suppress


def filter_response_information(response):
    """Filters response information from the given data. This is useful for logging communication with the API.

    :param response: The data to redact.

    :returns: data with sensitive information redacted.

    """
    hide_params = ["access_token", "id_token", "refresh_token"]
    # vcr throws error if multipart form data is received as binary https://github.com/kevin1024/vcrpy/issues/521
    with suppress(UnicodeDecodeError):
        if isinstance(response, dict):
            response_body = response.get("body").get("string")
            if response_body:
                response_body = json.loads(response_body)
                for param in hide_params:
                    if response_body.get(param, None):
                        response_body[param] = "REDACTED"
                response["body"]["string"] = json.dumps(response_body).encode("utf-8")
    return response


def filter_request_information(request):
    """Filters request information from the given data. This is useful for logging communication with the API.

    :param request: The data to redact.

    :returns: data with sensitive information redacted.

    """
    if "refresh_token=" in request.body:
        return None
    return request


my_vcr = vcr.VCR(
    serializer="yaml",
    cassette_library_dir="tests/unit_tests/cassettes",
    record_mode="once",
    match_on=["uri", "method"],
    filter_headers=["Authorization", "Cookie"],
    filter_post_data_parameters=["refresh_token", "code"],
    before_record_response=filter_response_information,
)
