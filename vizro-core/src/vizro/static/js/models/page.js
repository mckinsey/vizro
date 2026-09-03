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
      encodedMap.set(key, `b64_${encoded}`);
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
      } catch {
        console.warn("Failed to decode URL parameter:", key, val);
      }
    }
  }
  return decodedMap;
}

/*
Keeps controls in sync across pages through `vizro_controls_store` and mirrors show_in_url controls in the URL query
string. Runs for every control on the page (not only show_in_url ones) so that:
  - on page open, each control's selector is restored from the store's `currentValue`. This applies values that were
    set while on another page (a cross-page `set_control` target) and values that persisted from an earlier visit;
  - on control change, the store's `currentValue` is refreshed so the value is available to other pages and on the
    next visit;
  - show_in_url controls additionally have their value written into the URL query string.

`vizro_controls_store` is passed as a State and is the LAST argument (popped off here). The remaining args follow the
flexible-signature format, relying on control-id order matching selector value input/output order:
  [selector-1-value, ..., selector-N-value, control-1-id, ..., control-N-id, selector-1-id, ..., selector-N-id]
*/
function sync_url_query_params_and_controls(opl_triggered, ...values_ids) {
  const vizroControlsStore = values_ids.pop();

  if (values_ids.length % 3 !== 0) {
    throw new Error(
      `Invalid number of input parameters: received ${values_ids.length}.
Expected format (excluding the trailing vizro_controls_store): [selector-1-value, ..., control-1-id, ..., selector-1-id, ...]
Received input: ${JSON.stringify(values_ids)}`,
    );
  }

  const numberOfInputs = values_ids.length / 3;

  // Extract each segment
  const selectorValues = values_ids.slice(0, numberOfInputs);
  const controlIds = values_ids.slice(numberOfInputs, 2 * numberOfInputs);
  const selectorIds = values_ids.slice(2 * numberOfInputs);

  // Prepare output selector values, initially set to no_update.
  const outputSelectorValues = new Array(numberOfInputs).fill(
    dash_clientside.no_update,
  );

  // Map<controlId, selectorValue>
  const controlMap = new Map(
    controlIds.map((id, i) => [id, selectorValues[i]]),
  );

  const urlParams = new URLSearchParams(window.location.search);

  // Flag to check if the page is opened or a control has changed.
  const isPageOpened = opl_triggered === undefined;

  // Conditionally trigger the OPL action: return `null` to trigger it, or dash_clientside.no_update to skip.
  const triggerOPL = isPageOpened ? null : dash_clientside.no_update;

  if (isPageOpened) {
    console.debug("sync_url_query_params_and_controls: Page opened");

    // Restore from the store only the controls that are targets of a cross-page set_control (a synced control from
    // another page, or a drill-through target). Other controls keep their usual per-page behavior (they reset on
    // navigation) and are only restored from the URL below when they have show_in_url.
    controlIds.forEach((id, index) => {
      if (
        vizroControlsStore[id] !== undefined &&
        vizroControlsStore[id]["crossPageTarget"]
      ) {
        const value = vizroControlsStore[id]["currentValue"];
        controlMap.set(id, value);
        outputSelectorValues[index] = value;
      }
    });

    // When a page is opened the URL can be partially defined (e.g. a shared/bookmarked link or a drill-through). For
    // controls on this page, defined URL params take precedence over the stored value; others keep the stored value.
    const decodedParamMap = decodeUrlParams(urlParams, controlIds);
    decodedParamMap.forEach((value, id) => {
      const index = controlIds.indexOf(id);
      controlMap.set(id, value);
      outputSelectorValues[index] = value;
      if (vizroControlsStore[id] !== undefined) {
        vizroControlsStore[id]["currentValue"] = value;
      }
    });

    // Persist any URL-derived values back to the store so it stays the single source of truth across pages.
    if (decodedParamMap.size > 0) {
      dash_clientside.set_props("vizro_controls_store", {
        data: vizroControlsStore,
      });
    }
  } else {
    console.debug("sync_url_query_params_and_controls: Control changed");

    // A selector on this page changed. Refresh the store's currentValue for all controls on this page from their
    // current selector values (only the changed one actually differs), so synced/persisted state stays up to date.
    // Only current-page controls are in controlIds, so controls on other pages are left untouched.
    controlIds.forEach((id) => {
      if (vizroControlsStore[id] !== undefined) {
        vizroControlsStore[id]["currentValue"] = controlMap.get(id);
      }
    });
    dash_clientside.set_props("vizro_controls_store", {
      data: vizroControlsStore,
    });
  }

  // Encode this page's show_in_url controls into the URL query string.
  for (const [id, value] of encodeUrlParams(controlMap, controlIds)) {
    if (
      vizroControlsStore[id] !== undefined &&
      vizroControlsStore[id]["showInURL"] === true
    ) {
      urlParams.set(id, value);
    }
  }

  // Directly `replace` the URL instead of using a dcc.Location as a callback Output. Do it because the dcc.Location
  // uses history.pushState under the hood which causes destroying the history. With replaceState, we partially
  // maintain the history.
  const query = urlParams.toString();
  history.replaceState(
    null,
    "",
    query ? `${window.location.pathname}?${query}` : window.location.pathname,
  );

  // After this clientside callback, the "guard_action_chain" callback may run.
  // If the selector value is updated (from the store or the URL parameters),
  // set its value and the selector’s guard flag to **true**.
  // This ensures triggering the guard action chain callback
  // and prevents unnecessary actions from being triggered by the value change.
  selectorIds.forEach((selectorId, i) => {
    const selectorValue = outputSelectorValues[i];
    if (selectorValue !== dash_clientside.no_update) {
      dash_clientside.set_props(`${selectorId}_guard_actions_chain`, {
        data: true,
      });
      dash_clientside.set_props(selectorId, { value: selectorValue });
      // Update data property too for the range TimePicker case where dcc.Store
      // is used as a proxy to update both start and end values of the TimePicker.
      // There's no consequence in updating data property for other selectors as well,
      // as it's not used in that case.
      dash_clientside.set_props(selectorId, { data: selectorValue });
    }
  });
  return triggerOPL;
}

function reset_controls(_, vizroControlsStore, pageId) {
  console.debug("Reset controls on page:", pageId);

  // Get info for all controls on the current page.
  const pageControls = Object.values(vizroControlsStore).filter(
    (control) => control.pageId === pageId,
  );

  // For each control, prepare its original value
  const outputSelectorValues = pageControls.map(
    (control) => control.originalValue,
  );
  // For each control set all its guard to true to prevent triggering unnecessary actions.
  const outputSelectorGuards = pageControls.map(() => true);

  // Trigger the OPL after resetting all controls by returning `null` to the OPL component.
  return [null, ...outputSelectorValues, ...outputSelectorGuards];
}

window.encodeUrlParams = encodeUrlParams;
window.decodeUrlParams = decodeUrlParams;
window.dash_clientside = {
  ...window.dash_clientside,
  page: {
    sync_url_query_params_and_controls: sync_url_query_params_and_controls,
    reset_controls: reset_controls,
  },
};
