function update_range_slider_values(
  slider_value,
  start_value,
  end_value,
  slider_component_id,
) {
  console.debug("update_range_slider_values");
  const trigger_id = dash_clientside.callback_context.triggered_id;

  // slider component is triggered (slider_value)
  if (trigger_id === slider_component_id) {
    return [dash_clientside.no_update, slider_value[0], slider_value[1]];
  }

  // text form component is triggered (start_value or end_value)
  if (isNaN(start_value) || isNaN(end_value) || start_value > end_value) {
    throw dash_clientside.PreventUpdate;
  }
  return [
    [start_value, end_value],
    dash_clientside.no_update,
    dash_clientside.no_update,
  ];
}

window.dash_clientside = {
  ...window.dash_clientside,
  range_slider: { update_range_slider_values: update_range_slider_values },
};
