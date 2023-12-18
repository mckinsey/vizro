export function _update_dashboard_theme(checked) {
  return checked ? "vizro_light" : "vizro_dark";
}

export function _collapse_nav_panel(n_clicks, is_open) {
  if (!n_clicks)
    return [
      is_open,
      is_open
        ? {
            transform: "rotate(180deg)",
            transition: "transform 0.35s ease-in-out",
          }
        : { transform: "rotate(0deg)" },
    ];

  if (is_open) {
    return [false, { transform: "rotate(0deg)" }, "Show Menu"];
  } else {
    return [
      true,
      {
        transform: "rotate(180deg)",
        transition: "transform 0.35s ease-in-out",
      },
      "Hide Menu",
    ];
  }
}
