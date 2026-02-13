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
    accentColor: "var(--bs-primary)",
    advancedFilterBuilderColumnPillColor: "var(--bs-success)",
    advancedFilterBuilderJoinPillColor: "var(--bs-danger)",
    advancedFilterBuilderOptionPillColor: "var(--bs-warning)",
    advancedFilterBuilderValuePillColor: "var(--bs-info)",
    backgroundColor: "var(--bs-body-bg)",
    borderColor: "var(--bs-border-color)",
    borderRadius: 0,
    buttonActiveBackgroundColor: "var(--bs-primary)",
    buttonActiveBorder: false,
    buttonActiveTextColor: "var(--text-primary-inverted)",
    buttonBackgroundColor: "var(--bs-primary)",
    buttonBorder: false,
    buttonBorderRadius: 0,
    buttonDisabledBorder: false,
    buttonDisabledTextColor: "var(--bs-tertiary-color)",
    buttonFontWeight: 600,
    buttonHoverBackgroundColor: "var(--bs-primary-text-emphasis)",
    buttonHoverTextColor: "var(--text-primary-inverted)",
    buttonTextColor: "var(--text-primary-inverted)",
    buttonVerticalPadding: 4,
    buttonHorizontalPadding: 8,
    cellHorizontalPaddingScale: 0.75,
    checkboxCheckedBackgroundColor: "var(--bs-body-bg)",
    checkboxCheckedBorderColor: "var(--bs-primary)",
    checkboxCheckedShapeColor: "var(--bs-primary)",
    chromeBackgroundColor: "var(--bs-secondary-bg)",
    columnBorder: false,
    focusErrorShadow: "var(--bs-form-invalid-color) 0px 0px 0px 1px",
    focusShadow: "var(--bs-focus-ring-color) 0px 0px 0px 1px",
    fontFamily: ["inter", "sans-serif", "arial", "serif"],
    foregroundColor: "var(--bs-primary)",
    headerBackgroundColor: "var(--bs-body-bg)",
    headerFontSize: 14,
    headerFontWeight: 400,
    headerHeight: 40,
    headerRowBorder: true,
    headerTextColor: "var(--bs-secondary-color)",
    headerVerticalPaddingScale: 1,
    iconButtonActiveBackgroundColor: "transparent",
    iconButtonBorderRadius: 0,
    iconButtonHoverBackgroundColor: "transparent",
    iconButtonHoverColor: "var(--bs-primary-text-emphasis)",
    iconColor: "var(--bs-secondary)",
    inputBorder: false,
    inputDisabledTextColor: "var(--bs-tertiary-color)",
    inputFocusBorder: false,
    inputIconColor: "var(--bs-secondary)",
    invalidColor: "var(--bs-form-invalid-color)",
    listItemHeight: 36,
    menuBackgroundColor: "var(--bs-tertiary-bg)",
    menuBorder: true,
    menuSeparatorColor: "var(--bs-border-color)",
    menuShadow: "var(--bs-box-shadow)",
    menuTextColor: "var(--bs-secondary)",
    panelTitleBarIconColor: "var(--bs-secondary)",
    pickerButtonBackgroundColor: "transparent",
    pickerButtonFocusBackgroundColor: "transparent",
    pickerButtonFocusBorder: false,
    pickerButtonBorder: false,
    rowHoverColor: "var(--bs-tertiary-bg)",
    rowVerticalPaddingScale: 1.2,
    rowBorder: true,
    selectCellBorder: false,
    spacing: 8,
    textColor: "var(--bs-primary)",
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
