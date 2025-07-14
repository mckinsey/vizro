function update_slider_values(slider_value, end_value, slider_component_id) {
  console.debug("update_slider_values");
  const trigger_id = dash_clientside.callback_context.triggered_id;

  // slider component is triggered (slider_value)
  if (trigger_id === slider_component_id) {
    return [dash_clientside.no_update, slider_value];
  }

  // text form component is triggered (end_value)
  if (isNaN(end_value)) {
    throw dash_clientside.PreventUpdate;
  }
  return [end_value, dash_clientside.no_update];
}

window.dash_clientside = {
  ...window.dash_clientside,
  slider: { update_slider_values: update_slider_values },
};
