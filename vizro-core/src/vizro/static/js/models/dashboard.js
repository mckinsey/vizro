export function _update_dashboard_theme(checked) {
  document.documentElement.setAttribute(
    "data-bs-theme",
    checked ? "light" : "dark",
  );
  return checked ? "vizro_light" : "vizro_dark";
}

export function _update_ag_grid_theme(checked) {
  return checked
    ? "ag-theme-quartz ag-theme-vizro"
    : "ag-theme-quartz-dark ag-theme-vizro";
}

export function _update_graph_theme(checked, vizro_themes, graph_id) {
  // Determine the theme to be applied based on the checked value
  const theme_to_apply = checked ? vizro_themes["light"] : vizro_themes["dark"];

  // Find the Plotly graph element in the HTML document
  const plotly_graph = document
    .getElementById(graph_id)
    .querySelector(".js-plotly-plot");

  // Adjust `layout` property for the Plotly graph element
  Plotly.relayout(plotly_graph, { template: theme_to_apply });

  return dash_clientside.no_update;
}

export function _collapse_nav_panel(n_clicks, is_open) {
  if (!n_clicks) {
    /* Automatically collapses left-side if xs and s-devices are detected*/
    if (window.innerWidth < 176 || window.innerHeight < 176) {
      return [
        false,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
        },
        "Show Menu",
      ];
    }
    return dash_clientside.no_update;
  }
  if (is_open) {
    return [
      false,
      {
        transform: "rotate(180deg)",
        transition: "transform 0.35s ease-in-out",
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
