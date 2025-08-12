/*
Python equivalent to the following JavaScript code:
def encode_url_params(decoded_map, apply_on_keys=None):
    encoded_map = {}
    for key, value in decoded_map.items():
        if key in apply_on_keys:
            # This manual base64 encoding could be simplified with base64.urlsafe_b64encode.
            # It's kept here to match the javascript implementation.
            json_str = json.dumps(value, separators=(',', ':'))
            encoded_bytes = base64.b64encode(json_str.encode("utf-8"))
            encoded_str = encoded_bytes.decode("utf-8") \
                .replace("+", "-") \
                .replace("/", "_") \
                .rstrip("=")
            encoded_map[key] = "b64_" + encoded_str
    return encoded_map

Example inputs:
  {'vizro_1': 123, 'foo': ['a', 'b']},
  ['vizro_1']
Example output:
  {'foo': 'b64_IjEyMyI', 'bar': ['a', 'b']}
*/
function encodeUrlParams(decodedMap, applyOnKeys) {
  const encodedMap = new Map();
  for (const [key, value] of decodedMap.entries()) {
    if (applyOnKeys.includes(key)) {
      const json = JSON.stringify(value);
      const encoded = btoa(
        String.fromCharCode(...new TextEncoder().encode(json)),
      )
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
      encodedMap.set(key, "b64_" + encoded);
    }
  }
  return encodedMap;
}

/*
Python equivalent to the following JavaScript code:
def decode_url_params(encoded_map, apply_on_keys=None):
    decoded_map = {}
    for key, val in encoded_map.items():
        if val.startswith("b64_") and key in apply_on_keys:
            try:
                # This manual base64 decoding could be simplified with base64.urlsafe_b64decode.
                # It's kept here to match the javascript implementation.
                base64_str = val[4:].replace("-", "+").replace("_", "/")
                base64_str += "=" * ((4 - len(base64_str) % 4) % 4)
                binary_data = base64.b64decode(base64_str)
                json_str = binary_data.decode("utf-8")
                decoded_map[key] = json.loads(json_str)
            except Exception as e:
                print(f"Failed to decode URL parameter: {key}, {val} - {e}")
    return decoded_map

Example inputs:
  {'vizro_1': 'raw_value', 'vizro_2': 'b64_IjEyMyI', 'foo': 'raw_value', 'bar': 'b64_IjEyMyI', 'baz': 'b64_invalid'},
  ['vizro_1', 'vizro_2']
Example output (only vizro_2 is decoded):
  {'vizro_1': 'raw_value', 'vizro_2': '123', 'foo': 'raw_value', 'bar': 'b64_IjEyMyI', 'baz': 'b64_invalid'}
*/
function decodeUrlParams(encodedMap, applyOnKeys) {
  const decodedMap = new Map();
  for (const [key, val] of encodedMap.entries()) {
    if (val.startsWith("b64_") && applyOnKeys.includes(key)) {
      try {
        let base64 = val.slice(4).replace(/-/g, "+").replace(/_/g, "/");
        base64 += "=".repeat((4 - (base64.length % 4)) % 4);
        const binary = atob(base64);
        const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
        const json = new TextDecoder().decode(bytes);
        decodedMap.set(key, JSON.parse(json));
      } catch (e) {
        console.warn("Failed to decode URL parameter:", key, val);
      }
    }
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

  // controlMap is in format: Map<controlId, controlSelectorValue>
  const controlMap = new Map(
    values_ids.slice(half).map((id, i) => [id, values_ids[i]]),
  );

  const relevantControlIds = Array.from(controlMap.keys());

  const urlParams = new URLSearchParams(window.location.search);

  // Flag to check if the page is opened or a control has changed.
  const isPageOpened =
    dash_clientside.callback_context.triggered_id === undefined;

  // Conditionally trigger the OPL action: return `null` to trigger it, or dash_clientside.no_update to skip.
  const triggerOPL = isPageOpened ? null : dash_clientside.no_update;

  // Prepare default selector values outputs
  //  const outputSelectorValuesAllNoUpdate = new Array(controlMap.size).fill(
  //    dash_clientside.no_update,
  //  );
  const outputSelectorValues = new Array(controlMap.size).fill(
    dash_clientside.no_update,
  );

  if (isPageOpened) {
    console.debug("sync_url_query_params_and_controls: Page opened");

    // When page is just opened, the URL can be partially defined (like the drill-through use case). In that case, only
    // defined URL params take the precedence over the controlMap values, and for others the controlMap values are used.

    // Decoded URL parameters in format: Map<controlId, controlSelectorValue>
    const decodedParamMap = decodeUrlParams(
      urlParams,
      relevantControlIds, // Apply decoding only to control IDs
    );

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
  encodeUrlParams(controlMap, relevantControlIds).forEach((value, id) =>
    urlParams.set(id, value),
  );

  // Directly `replace` the URL instead of using a dcc.Location as a callback Output. Do it because the dcc.Location
  // uses history.pushState under the hood which causes destroying the history. With replaceState, we partially
  // maintain the history.
  history.replaceState(
    null,
    "",
    `${window.location.pathname}?${urlParams.toString()}`,
  );

  // After this clientside callback, the "guard_action_chain" callback may run.
  // For each selector, set the guard component to true or false based on the trigger:
  // 1. User control change:
  //    - Returned value is dash_clientside.no_update
  //    - "guard_action_chain" runs after this
  //    - Guard data already false (overwritten with false again)
  //
  // 2. URL parameters:
  //    - Returned value is NOT dash_clientside.no_update
  //    - "guard_action_chain" runs after this
  //    - Guard data set to true to block the actions chain
  //
  // 3. Object recreated by another action (e.g. DFP):
  //    - Returned value is dash_clientside.no_update
  //    - "guard_action_chain" is SKIPPED -> (it's skipped as object is recreated and no_update is returned by this clientside callback)
  //    - Guard data set to false so future changes trigger filter action
  const outputSelectorIds = dash_clientside.callback_context.outputs_list;
  for (let i = 1; i < outputSelectorIds.length; i++) {
    const selectorId = outputSelectorIds[i]["id"];
    const selectorValue = outputSelectorValues[i - 1];
    const isFromUrl = selectorValue !== dash_clientside.no_update;

    dash_clientside.set_props(`${selectorId}_guard_actions_chain`, {
      data: isFromUrl,
    });
  }

  return [triggerOPL, ...outputSelectorValues];
}

window.encodeUrlParams = encodeUrlParams;
window.decodeUrlParams = decodeUrlParams;
window.dash_clientside = {
  ...window.dash_clientside,
  page: {
    sync_url_query_params_and_controls: sync_url_query_params_and_controls,
  },
};
