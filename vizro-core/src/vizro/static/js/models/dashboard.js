/**
 * Updates the dashboard theme by setting theme attributes on the document element.
 *
 * @param {boolean} theme_selector_checked - Whether the theme selector is checked (true for light theme, false for dark theme)
 * @returns {*} Returns dash_clientside.no_update to prevent component updates
 */
function update_dashboard_theme(theme_selector_checked) {
  const theme = theme_selector_checked ? "light" : "dark";

  // Update theme attributes for Bootstrap and Mantine
  document.documentElement.setAttribute("data-bs-theme", theme);
  document.documentElement.setAttribute("data-mantine-color-scheme", theme);

  return dash_clientside.no_update;
}

// Define Vizro theme function for AG Grid using Bootstrap CSS variables and new theming API v33
// Reference: https://www.ag-grid.com/theme-builder/
// This theme automatically adapts to light/dark mode via Bootstrap's data-bs-theme attribute
var dashAgGridFunctions = window.dashAgGridFunctions || {};
dashAgGridFunctions.vizroTheme = function (theme, agGrid) {
  return theme.withPart(agGrid.createPart(agGrid.iconSetMaterial)).withParams({
    accentColor: "var(--bs-border-color-translucent)",
    backgroundColor: "var(--bs-body-bg)",
    borderColor: "var(--bs-border-color)",
    borderRadius: 0,
    chromeBackgroundColor: "transparent",
    columnBorder: false,
    fontFamily: ["inter", "sans-serif", "arial", "serif"],
    foregroundColor: "var(--bs-body-color)",
    headerBackgroundColor: "var(--bs-body-bg)",
    headerFontSize: 14,
    headerFontWeight: 400,
    headerRowBorder: true,
    headerTextColor: "var(--bs-secondary-color)",
    headerVerticalPaddingScale: 1,
    rowBorder: true,
    spacing: 8,
    wrapperBorder: false,
    wrapperBorderRadius: 0,
  });
};

window.dashAgGridFunctions = dashAgGridFunctions;

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
    update_graph_theme: update_graph_theme,
    collapse_nav_panel: collapse_nav_panel,
  },
};
