export function _update_dashboard_theme(theme_selector_checked) {
  document.documentElement.setAttribute(
    "data-bs-theme",
    theme_selector_checked ? "light" : "dark",
  );
  return theme_selector_checked ? "vizro_light" : "vizro_dark";
}

export function _update_ag_grid_theme(theme_selector_checked) {
  return theme_selector_checked
    ? "ag-theme-quartz ag-theme-vizro"
    : "ag-theme-quartz-dark ag-theme-vizro";
}

export function _update_graph_theme(
  theme_selector_checked,
  vizro_themes,
  graph_id,
) {
  // Determine the theme to be applied based on the theme_selector checked value
  const theme_to_apply = theme_selector_checked
    ? vizro_themes["light"]
    : vizro_themes["dark"];

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
    if (window.innerWidth < 576 || window.innerHeight < 576) {
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
