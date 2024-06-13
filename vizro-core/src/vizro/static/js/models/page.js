export function _update_themed_components(theme_selector, themed_components, vizro_themes) {
  // Determine the theme to be applied based on the theme_selector value
  const theme_to_apply = theme_selector ? vizro_themes["light"] : vizro_themes["dark"];

  // Apply the selected theme to each component in the themed_components list
  themed_components.forEach(component_id => {
    const plotly_element = document.getElementById(component_id).querySelector('.js-plotly-plot');
    Plotly.relayout(plotly_element, { 'template': theme_to_apply });
  });

  return dash_clientside.no_update;
}
