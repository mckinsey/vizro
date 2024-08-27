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
  figure,
  theme_selector_checked,
  vizro_themes,
) {
  const theme_to_apply = theme_selector_checked ? "vizro_light" : "vizro_dark";

  // If graph has been returned from the server then it already has the dashboard default template applied in
  // Graph.__call__, and so we don't need to do any updates apart from to undo the {"style": {"visibility": "hidden"}}.
  // If this callback has been triggered through the theme selector toggle then we always want to update though.
  if (theme_to_apply === vizro_themes["default"] && dash_clientside.callback_context.triggered_id !== "theme_selector") {
    return [dash_clientside.no_update, {}];
  }

  const updated_figure = {
    ...figure,
    layout: {
      ...figure.layout,
      template: vizro_themes[theme_to_apply]
    }
  };

  return [updated_figure, {}]
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
