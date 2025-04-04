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
  // Unlike collapse_container, this needs to always run on initial page load to be responsive to screen size.
  const collapsed_state = [
    false,
    {
      transform: "rotate(180deg)",
      transition: "transform 0.35s ease-in-out",
      marginLeft: "8px",
    },
    "Show Menu",
  ];
  const expanded_state = [
    true,
    {
      transform: "rotate(0deg)",
      transition: "transform 0.35s ease-in-out",
    },
    "Hide Menu",
  ];

  if (!n_clicks) {
    /* Automatically collapses left-side if xs and s-devices are detected*/
    if (window.innerWidth < 576 || window.innerHeight < 576) {
      return collapsed_state;
    }
    return dash_clientside.no_update;
  }

  return is_open ? collapsed_state : expanded_state;
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
