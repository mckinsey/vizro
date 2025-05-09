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
    if (window.innerWidth < 768 || window.innerHeight < 768) {
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

window.dash_clientside = {
  ...window.dash_clientside,
  dashboard: {
    update_dashboard_theme: update_dashboard_theme,
    update_ag_grid_theme: update_ag_grid_theme,
    update_graph_theme: update_graph_theme,
    collapse_nav_panel: collapse_nav_panel,
  },
};
