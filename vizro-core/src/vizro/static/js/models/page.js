// Equivalent to the following Python code:
// def encode_to_base64(ids, values):
//    result = []
//    for id, value in zip(ids, values):
//        json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
//        b64_bytes = base64.urlsafe_b64encode(json_bytes)
//        result.append((id, f"b64_{b64_bytes.decode('utf-8').rstrip('=')}"))
//    return result
//
// Example inputs: ['asd', 'qwe'], ['123', 234]
// Example outputs: [('asd', 'b64_IjEyMyI'), ('qwe', 'b64_MjM0')]
function encodeUrlParams(ids, values) {
  return ids.map((id, i) => [
    id,
    "b64_" +
      btoa(
        String.fromCharCode(
          ...new TextEncoder().encode(JSON.stringify(values[i])),
        ),
      )
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, ""),
  ]);
}

// Equivalent to the following Python code:
//    def decode_url_params(params):
//        ids, values = [], []
//        for k, v in params.items():
//            ids.append(k)
//            if isinstance(v, str) and v.startswith("b64_"):
//                b64 = v[4:].replace('-', '+').replace('_', '/')
//                b64 += '=' * (-len(b64) % 4)
//                v = json.loads(base64.b64decode(b64).decode())
//            values.append(v)
//        return {'ids': ids, 'values': values}
// Example inputs: {'asd': 'b64_IjEyMyI', 'qwe': 'b64_MjM0'}
// Example outputs: {'ids': ['asd', 'qwe'], 'values': ['123', 234]}
function decodeUrlParams(params) {
  function decodeParam(encoded) {
    let base64 = encoded.slice(4).replace(/-/g, "+").replace(/_/g, "/");
    while (base64.length % 4 !== 0) {
      base64 += "=";
    }
    const str = atob(base64);
    const bytes = Uint8Array.from(str, (c) => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  const ids = [];
  const values = [];

  for (const [key, val] of params.entries()) {
    ids.push(key);
    // Decode only if the value starts with "b64_". Otherwise, we assume they are external query parameters.
    if (val.startsWith("b64_")) {
      values.push(decodeParam(val));
    } else {
      values.push(val);
    }
  }

  return { ids, values };
}

function sync_url_query_params_and_controls(...values_ids) {
  // Control IDs are required due to Dash's limitations on clientside callback flexible signatures, so that we can:
  //   1. Map url query parameters to control selector value outputs properly.
  //   2. Map control selector value input to url query parameters properly.
  // The solution relies on the fact that the order of control IDs matches the order of the
  // control selector value inputs and their corresponding outputs.

  // Split control inputs and selector values that are in format:
  // [selector-1-value, selector-2-value, selector-N-value, ..., control-1-id, control-2-id, control-N-id, ...]
  const count = values_ids.length / 2;
  let controlValues = values_ids.slice(0, count);
  const controlIds = values_ids.slice(count);

  const urlParams = new URLSearchParams(window.location.search);

  const isPageOpened =
    dash_clientside.callback_context.triggered_id === undefined;

  // Conditionally trigger the OPL action: return `null` to trigger it, or dash_clientside.no_update to skip.
  const triggerOPL = isPageOpened ? null : dash_clientside.no_update;

  // Prepare default selector values outputs
  const outputSelectorValues = controlIds.map(() => dash_clientside.no_update);

  if (isPageOpened) {
    console.log("CS:CB Page opened (url -> controls -> url)");

    const { ids: decodedParamIds, values: decodedParamValues } =
      decodeUrlParams(urlParams);

    // Overwrite control selector input and output values with the values from the URL.
    controlIds.forEach((controlId, i) => {
      const index = decodedParamIds.indexOf(controlId);
      // Update only if the control ID is found in the URL parameters.
      if (index !== -1) {
        controlValues[i] = decodedParamValues[index];
        outputSelectorValues[i] = decodedParamValues[index];
      }
    });
  } else {
    console.log("CS:CB Control is changed (controls -> url)");
  }

  // Update urlParams with updated control values
  const encodedControlsIdsValues = encodeUrlParams(controlIds, controlValues);
  encodedControlsIdsValues.forEach(([id, value]) => urlParams.set(id, value));

  // Directly `replace` the URL instead of using a dcc.Location as a callback Output. Do it because the dcc.Location
  // uses history.pushState under the hood which causes destroying the history. With replaceState, we partially
  // maintain the history.
  const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
  history.replaceState(null, "", newUrl);

  console.log("CS:CB Returns:", [triggerOPL, ...outputSelectorValues]);
  return [triggerOPL, ...outputSelectorValues];
}

window.dash_clientside = {
  ...window.dash_clientside,
  page: {
    sync_url_query_params_and_controls: sync_url_query_params_and_controls,
  },
};
