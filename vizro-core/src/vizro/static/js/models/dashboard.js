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

//function sync_url_query_params_and_controls(...args) {
//  console.log("sync_url_params_with_controls");
//  if (!args.length || args.every(x => x === undefined || x === null)) {
//    // Nothing to update
//    return window.location.search;
//  }
//
//  const count = args.length / 2;
//  const values = args.slice(0, count);
//  const ids = args.slice(count);
//
//  const entries = ids.map((id, i) => [
//    id,
//    btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(values[i]))))
//      .replace(/\+/g, '-')
//      .replace(/\//g, '_')
//      .replace(/=+$/, '')
//  ]);
//
//  const currentParams = new URLSearchParams(window.location.search); // Could come from Dash State
//  for (const [k, v] of entries) {
//    currentParams.set(k, v);  // Merge new/updated value
//  }
//
//  const new_query_string = '?' + currentParams.toString();
//
//  const links = document.querySelectorAll("a[href^='/']");
//  links.forEach(link => {
//    const href = link.getAttribute("href");
//    const base = href.split('?')[0];
//    link.setAttribute("href", base + new_query_string);
//  });
//
//  return new_query_string;
//}

function encodeUrlParams(ids, values) {
    return ids.map((id, i) => [
        id,
        btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(values[i]))))
          .replace(/\+/g, '-')
          .replace(/\//g, '_')
          .replace(/=+$/, '')
    ]);
}


function decodeUrlParams(queryString) {
  // Decode each encoded value
  function decodeParam(encoded) {
    let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4 !== 0) {
      base64 += '=';
    }
    const str = atob(base64);
    const bytes = Uint8Array.from(str, c => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  const params = new URLSearchParams(queryString);
  const ids = [];
  const values = [];

  for (const [key, val] of params.entries()) {
    ids.push(key);
    values.push(decodeParam(val));
  }

  return { ids, values };
}


//function sync_url_query_params_and_controls(...values_ids) {
//    // Control IDs are required due to Dash's limitations on clientside callback flexible signatures, so that we can:
//    //   1. Map control selector value input to url query parameters properly.
//    //   2. Map url query parameters to control selector value outputs properly.
//    // The Solution relies on the fact that the order of control IDs matches the order of the
//    // control selector value inputs and their corresponding outputs.
//
//    // TODO-NOW: Think about replacing the controlIds with the dcc.Store that would hold the mapping of control IDs to
//    //  selector IDs. In this case, we could solve it using the store, ctx.inputs_list, ctx.outputs_list.
//
//    // Split control inputs and selector values that are in format:
//    // [selector-1-value, selector-2-value, ..., control-1-id, control-2-id, ...]
//    const count = values_ids.length / 2;
//    const inputSelectorValues = values_ids.slice(0, count);
//    const controlIds = values_ids.slice(count);
//
//    //
//    const entries = encodeUrlParams(ids, values);
//    const currentParams = new URLSearchParams(window.location.search); // Could come from Dash State
//
//}


// TODO: Rename and Clean
function testtest(...values_ids) {
//    Sleep for n_sec seconds to prove that OPL won't be triggered before the end of the operation.
//    const n_sec = 1;
//    const end = Date.now() + n_sec * 1000;
//    while (Date.now() < end) {
//      Math.sqrt(Math.random());
//    }

    const count = values_ids.length / 2;
    const values = values_ids.slice(0, count);
    const ids = values_ids.slice(count);

    const entries = encodeUrlParams(ids, values);

    const currentParams = new URLSearchParams(window.location.search); // Could come from Dash State

    // Trigger_id is [] when page is just opened. Otherwise it's a control that's changed.
    trigger_id = dash_clientside.callback_context.triggered_id;

//    if (trigger_id === undefined) {
//        if (currentParams['size'] === 0) {
//            // Controls -> URL
//            console.log(" -> testtest: Page is just opened with NO URL PARAMS");
//        }
//        else {
//            // URL -> Controls
//            console.log(" -> testtest: Page with URL PARAMS");
//        }
//    }
//    else {
//        // Controls -> URL
//        console.log(" -> testtest: Control is changed");
//    }

    if (trigger_id === undefined && currentParams['size'] !== 0) {
        // URL -> Controls
        console.log("CS:CB Page with URL PARAMS (url -> controls)");

        const { ids: decodedIds, values: decodedValues } = decodeUrlParams(currentParams.toString());

        for (const [k, v] of entries) {
          if (!currentParams.has(k)) {
            currentParams.set(k, v);  // Set only if the key doesn't exist
          }
        }
        const new_query_string = '?' + currentParams.toString();

        // Update the controls with the values from the URL. Slide through the ids and set values if it matches otherwise set clientside.no_update.
        const result = ids.map(id => {
          const index = decodedIds.indexOf(id);
          return index !== -1 ? decodedValues[index] : dash_clientside.no_update;
        });


        //  is dash_clientside.no_update where the value is not set through the URL.
        return ["Trigger-OPL", new_query_string].concat(result);
    }

    const listOfNoUpdateObjects = Array(ids.length).fill(dash_clientside.no_update);

    // Controls -> URL
    if (trigger_id === undefined) {
        console.log("CS:CB Page with NO URL PARAMS (controls -> url)");

        // TODO: Refactor so this IF only sets TRIGGER-OPL. Make return at the end of the function.
        for (const [k, v] of entries) {
          currentParams.set(k, v);  // Merge new/updated value
        }
        const new_query_string = '?' + currentParams.toString();

        return ["Trigger-OPL", new_query_string].concat(listOfNoUpdateObjects);
    }
    else {
        // TODO: Be careful with Slider/RangeSlider clientside callbacks, because it can happen that it unexpectedly trigger this callback when the page is opened.

        console.log("CS:CB Control is changed (controls -> url)");

        for (const [k, v] of entries) {
          currentParams.set(k, v);  // Merge new/updated value
        }
        const new_query_string = '?' + currentParams.toString();

        // Avoid triggering OPL.
        return [dash_clientside.no_update, new_query_string].concat(listOfNoUpdateObjects);
    }
}

window.dash_clientside = {
  ...window.dash_clientside,
  dashboard: {
    update_dashboard_theme: update_dashboard_theme,
    update_ag_grid_theme: update_ag_grid_theme,
    update_graph_theme: update_graph_theme,
    collapse_nav_panel: collapse_nav_panel,
//    sync_url_query_params_and_controls: sync_url_query_params_and_controls,
    testtest: testtest
  },
};
