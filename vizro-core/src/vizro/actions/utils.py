# TODO NOW: is vizro.actions.utils the right place for this? Could be used by apps outside vizro to deeplink into Vizro.
import base64
import json


# TODO NOW: think about exactly what function to expose here - a single value encoding or multiple? Compare to Python
# built-in urlparse stuff.
# def encode_url_params(decoded_map, apply_on_keys):
# ...
# TODO NOW: check again this matches JS encoding, add tests.


def b64_encode_value(value) -> str:
    json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
    b64_bytes = base64.urlsafe_b64encode(json_bytes)
    return f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"
