function update_dashboard_theme(theme_selector_checked) {
  const theme = theme_selector_checked ? "light" : "dark";

  // Update theme attributes for Bootstrap and Mantine
  document.documentElement.setAttribute("data-bs-theme", theme);
  document.documentElement.setAttribute("data-mantine-color-scheme", theme);

  return window.dash_clientside.no_update;
}

function update_ag_grid_theme(theme_selector_checked) {
  return theme_selector_checked
    ? "ag-theme-quartz ag-theme-vizro"
    : "ag-theme-quartz-dark ag-theme-vizro";
}

function update_graph_theme(figure, theme_selector_checked, vizro_themes) {
  const theme_to_apply = theme_selector_checked ? "vizro_light" : "vizro_dark";

  const updated_figure = {
    ...figure,
    layout: {
      ...figure.layout,
      template: vizro_themes[theme_to_apply],
    },
  };

  // {} resets the figure.style to undo the {"visibility": "hidden"} from set_props in Graph.__call__.
  return [updated_figure, {}];
}

function collapse_nav_panel(n_clicks, is_open) {
  if (!n_clicks) {
    /* Automatically collapses left-side if xs, s and m-devices are detected*/
    if (window.innerWidth < 68 || window.innerHeight < 68) {
      return [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
          marginLeft: "8px",
        },
        "Show Menu",
      ];
    }
    throw dash_clientside.PreventUpdate;
  }
  if (is_open) {
    return [
      false,
      {
        transform: "rotate(180deg)",
        transition: "transform 0.35s ease-in-out",
        marginLeft: "8px",
      },
      "Show Menu",
    ];
  } else {
    return [
      true,
      {
        transform: "rotate(0deg)",
        transition: "transform 0.35s ease-in-out",
      },
      "Hide Menu",
    ];
  }
}

function encodeUrlParams(ids, values) {
    return ids.map((id, i) => [
        id,
        btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(values[i]))))
          .replace(/\+/g, '-')
          .replace(/\//g, '_')
          .replace(/=+$/, '')
    ]);
}

function decodeUrlParams(params) {
  function decodeParam(encoded) {
    let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4 !== 0) {
      base64 += '=';
    }
    const str = atob(base64);
    const bytes = Uint8Array.from(str, c => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  const ids = [];
  const values = [];

  for (const [key, val] of params.entries()) {
    ids.push(key);
    // TODO-NOW: Is it smart to silent the error here?
    // Silent the error if the value cannot be decoded. It's added for external query parameters.
    try {
      values.push(decodeParam(val));
    } catch {
      values.push(val);
    }
  }

  return { ids, values };
}

// TODO-NOW: Remove unnecessary console logs here and from "gateway".
function sync_url_query_params_and_controls(...values_ids) {
    // Control IDs are required due to Dash's limitations on clientside callback flexible signatures, so that we can:
    //   1. Map control selector value input to url query parameters properly.
    //   2. Map url query parameters to control selector value outputs properly.
    // The Solution relies on the fact that the order of control IDs matches the order of the
    // control selector value inputs and their corresponding outputs.

    // TODO-NOW: Think about replacing the controlIds inputs with the dcc.Store that would map of control IDs to
    //  selector IDs. In this case, we could solve the problem by using the store, ctx.inputs_list, ctx.outputs_list.

    // Split control inputs and selector values that are in format:
    // [selector-1-value, selector-2-value, selector-N-value, ..., control-1-id, control-2-id, control-N-id, ...]
    const count = values_ids.length / 2;
    const inputValues = values_ids.slice(0, count);
    const controlIds = values_ids.slice(count);

    const currentParams = new URLSearchParams(window.location.search);
    const encodedControlsIdsValues = encodeUrlParams(controlIds, inputValues);

    // Find under which circumstances the callback is triggered:
    const trigger_id = dash_clientside.callback_context.triggered_id;

    const isPageOpenedWithParams = trigger_id === undefined && currentParams.size !== 0;
    if (isPageOpenedWithParams) {
        console.log("CS:CB Page with URL PARAMS (url -> controls + controls -> url)");
    }
    const isPageOpenedNoParams = trigger_id === undefined && currentParams.size === 0;
    if (isPageOpenedNoParams) {
        console.log("CS:CB Page with NO URL PARAMS (controls -> url)");
    }
    const isControlChanged = trigger_id !== undefined;
    if (isControlChanged) {
        console.log("CS:CB Control is changed (controls -> url)");
    }

    // Crafting outputs:
    // 1. Conditionally trigger the OPL action: return `null` to trigger it, or dash_clientside.no_update to skip.
    const triggerOPL = isControlChanged ? dash_clientside.no_update : null;

    // 2. Updated URL query string.
    for (const [encodedControlId, encodedControlValue] of encodedControlsIdsValues) {
      if (isControlChanged || isPageOpenedNoParams) {
        // If the control is changed, we need to update the URL param.
        // If the page is opened with no URL params, we need to set the initial values.
        currentParams.set(encodedControlId, encodedControlValue);
      }

      if (isPageOpenedWithParams && !currentParams.has(encodedControlId)) {
        // If the page is opened with params, we need to add the new value only if it doesn't exist.
        // This prevents overwriting existing values in the URL.
        currentParams.set(encodedControlId, encodedControlValue);
      }
    }

    const newQueryString = '?' + currentParams.toString();  // Now currentParams contains all the updated parameters.

    // 3. Updated control selector values.
    const { ids: decodedParamIds, values: decodedParamValues } = decodeUrlParams(currentParams);

    // Update only control selector values that are present in the URL query params if the page is opened with params.
    const newSelectorValues = controlIds.map(id => {
      const index = decodedParamIds.indexOf(id);
      return isPageOpenedWithParams && index !== -1 ? decodedParamValues[index] : dash_clientside.no_update;
    });

    // Directly `replace` the URL instead of using a dcc.Location as a callback Output. Do it because the dcc.Location
    // uses history.pushState under the hood which causes destroying the history. With replaceState, we partially
    // maintain the history.
    const newUrl = `${window.location.pathname}?${currentParams.toString()}`
    history.replaceState(null, '', newUrl);

    console.log("CS:CB Returns:", [triggerOPL, ...newSelectorValues]);
    return [triggerOPL, ...newSelectorValues];
}


window.dash_clientside = {
  ...window.dash_clientside,
  dashboard: {
    update_dashboard_theme: update_dashboard_theme,
    update_ag_grid_theme: update_ag_grid_theme,
    update_graph_theme: update_graph_theme,
    collapse_nav_panel: collapse_nav_panel,
    sync_url_query_params_and_controls: sync_url_query_params_and_controls
  },
};
