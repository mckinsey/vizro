function update_range_slider_values(
  start,
  end,
  slider,
  input_store,
  self_data,
) {
  var end_text_value,
    end_value,
    slider_value,
    start_text_value,
    start_value,
    trigger_id;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }

  // text form component is the trigger
  if (
    trigger_id === `${self_data["id"]}_start_value` ||
    trigger_id === `${self_data["id"]}_end_value`
  ) {
    if (isNaN(start) || isNaN(end)) {
      throw dash_clientside.PreventUpdate;
    }
    return [start, end, [start, end], [start, end]];

    // slider component is the trigger
  } else if (trigger_id === self_data["id"]) {
    return [slider[0], slider[1], slider, slider];
  }
  // on_page_load is the trigger
  if (input_store === null) {
    return [
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
      slider,
    ];
  }
  if (
    slider[0] === start &&
    input_store[0] === start &&
    slider[1] === end &&
    input_store[1] === end
  ) {
    // To prevent filter_action to be triggered after on_page_load
    return [
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }
  return [input_store[0], input_store[1], input_store, input_store];
}

window.dash_clientside = {
  ...window.dash_clientside,
  range_slider: { update_range_slider_values: update_range_slider_values },
};
