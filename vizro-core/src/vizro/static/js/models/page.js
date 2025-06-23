// Python equivalent to the following JavaScript code:
// def encode_url_params(decoded_map):
//    encoded_map = {}
//    for id, value in decoded_map.items():
//        json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
//        b64_bytes = base64.urlsafe_b64encode(json_bytes)
//        b64_str = b64_bytes.decode("utf-8").rstrip("=")
//        encoded_map[id] = f"b64_{b64_str}"
//    return encoded_map
//
// Example inputs: {'foo': 123, 'bar': ['a', 'b']}
// Example output: {'foo': 'b64_IjEyMyI', 'bar': 'b64_WyJhIiwiYiJd'}
function encodeUrlParams(decodedMap) {
  const encodedMap = new Map();
  for (const [id, value] of decodedMap.entries()) {
    const json = JSON.stringify(value);
    const encoded = btoa(String.fromCharCode(...new TextEncoder().encode(json)))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
    encodedMap.set(id, "b64_" + encoded);
  }
  return encodedMap;
}

// Python equivalent to the following JavaScript code:
// def decode_url_params(encoded_map):
//    decoded_map = {}
//    for key, val in encoded_map.items():
//        if val.startswith("b64_"):
//            b64 = val[4:].replace("-", "+").replace("_", "/")
//            b64 += "=" * ((4 - len(b64) % 4) % 4)
//            decoded = json.loads(base64.b64decode(b64).decode("utf-8"))
//        else:
//            decoded = val
//        decoded_map[key] = decoded
//    return decoded_map
//
// Example inputs: {'foo': 'b64_IjEyMyI', 'bar': 'b64_WyJhIiwiYiJd', 'external': 'raw_value'}
// Example output: {'foo': '123', 'bar': ['a', 'b'], 'external': 'raw_value'}
function decodeUrlParams(encodedMap) {
  function decodeParam(encoded) {
    let base64 = encoded.slice(4).replace(/-/g, "+").replace(/_/g, "/");
    base64 += "=".repeat((4 - (base64.length % 4)) % 4);
    const binary = atob(base64);
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  const decodedMap = new Map();
  for (const [key, val] of encodedMap) {
    const decoded = val.startsWith("b64_") ? decodeParam(val) : val;
    decodedMap.set(key, decoded);
  }

  return decodedMap;
}

function sync_url_query_params_and_controls(...values_ids) {
  // Control IDs are required due to Dash's limitations on clientside callback flexible signatures, so that we can:
  //   1. Map url query parameters to control selector value outputs properly.
  //   2. Map control selector value input to url query parameters properly.
  // The solution relies on the fact that the order of control IDs matches the order of the
  // control selector value inputs and their corresponding outputs.

  // Split control inputs and selector values that are in format:
  // [selector-1-value, selector-2-value, selector-N-value, ..., control-1-id, control-2-id, control-N-id, ...]

  const half = values_ids.length / 2;
  const controlMap = new Map(
    values_ids.slice(half).map((id, i) => [id, values_ids[i]]),
  );

  const urlParams = new URLSearchParams(window.location.search);

  // Flag to check if the page is opened or a control has changed.
  const isPageOpened =
    dash_clientside.callback_context.triggered_id === undefined;
  // Conditionally trigger the OPL action: return `null` to trigger it, or dash_clientside.no_update to skip.
  const triggerOPL = isPageOpened ? null : dash_clientside.no_update;
  // Prepare default selector values outputs
  const outputSelectorValues = new Array(controlMap.size).fill(
    dash_clientside.no_update,
  );

  if (isPageOpened) {
    console.debug("sync_url_query_params_and_controls: Page opened");

    // Decoded URL parameters in format: Map<controlId, controlSelectorValue>
    const decodedParamMap = decodeUrlParams(urlParams);

    // Values from the URL take precedence if page is just opened.
    // Overwrite controlMap and prepare callback control outputs by setting the values from the URL.
    Array.from(controlMap.keys()).forEach((id, index) => {
      if (decodedParamMap.has(id)) {
        const value = decodedParamMap.get(id);
        controlMap.set(id, value);
        outputSelectorValues[index] = value;
      }
    });
  } else {
    console.debug("sync_url_query_params_and_controls: Control changed");
  }

  // Encode controlMap to URL parameters.
  encodeUrlParams(controlMap).forEach((value, id) => urlParams.set(id, value));

  // Directly `replace` the URL instead of using a dcc.Location as a callback Output. Do it because the dcc.Location
  // uses history.pushState under the hood which causes destroying the history. With replaceState, we partially
  // maintain the history.
  history.replaceState(
    null,
    "",
    `${window.location.pathname}?${urlParams.toString()}`,
  );

  return [triggerOPL, ...outputSelectorValues];
}

window.dash_clientside = {
  ...window.dash_clientside,
  page: {
    sync_url_query_params_and_controls: sync_url_query_params_and_controls,
  },
};
