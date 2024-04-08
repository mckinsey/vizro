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

export function _collapse_nav_panel(n_clicks, is_open) {
  if (!n_clicks) {
    /* Automatically collapses left-side if xs and s-devices are detected*/
    if (window.innerWidth < 576 || window.innerHeight < 576) {
      return [
        false,
        {
          transform: "rotate(180deg)",
          left: "4px",
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
        left: "4px",
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
