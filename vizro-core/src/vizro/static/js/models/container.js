function toggle_container(n_clicks, is_open) {
  if (!n_clicks) {
    if (is_open) {
      return [
        is_open,
        {
          transform: "rotate(180deg)",
          transition: "transform 0.35s ease-in-out",
        },
      ];
    }
    return dash_clientside.no_update;
  }
  return [
    !is_open,
    {
      transform: !is_open ? "rotate(180deg)" : "rotate(0deg)",
      transition: "transform 0.35s ease-in-out",
    },
  ];
}

window.dash_clientside = {
  ...window.dash_clientside,
  container: { toggle_container: toggle_container },
};
