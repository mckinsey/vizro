function collapse_container(n_clicks, is_open) {
  return [
    !is_open,
    {
      // The arrow is correctly pointing up/down to begin with, so we only rotate it when there's an odd number of
      // clicks. If this was conditional instead on is_open then it wouldn't work correctly.
      transform: n_clicks % 2 ? "rotate(180deg)" : "rotate(0deg)",
      transition: "transform 0.35s ease-in-out",
    },
    is_open ? "Show Content" : "Hide Content",
  ];
}

window.dash_clientside = {
  ...window.dash_clientside,
  container: { collapse_container: collapse_container },
};
