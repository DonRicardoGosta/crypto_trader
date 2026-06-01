from trading_platform.adapters.bitunix.signing import body_string, sign_request


def test_sign_request_headers():
    headers = sign_request("key", "secret", "", "")
    assert "api-key" in headers and "sign" in headers

def test_body_string_compact():
    assert body_string({"a": 1}) == '{"a":1}'
