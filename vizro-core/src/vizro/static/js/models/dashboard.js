export function _update_dashboard_theme(on) {
  return on ? "vizro_dark" : "vizro_light";
}

export function _collapse_nav_panel(n_clicks, is_open) {
  if (n_clicks) return !is_open;

  return is_open;
}
