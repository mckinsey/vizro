function update_slider_values(start, slider, input_store, self_data) {
  var end_value, trigger_id;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }

  // text form component is the trigger
  if (trigger_id === `${self_data["id"]}_end_value`) {
    if (isNaN(start)) {
      throw dash_clientside.PreventUpdate;
    }
    return [start, start, start];

    // slider component is the trigger
  } else if (trigger_id === self_data["id"]) {
    return [slider, slider, slider];
  }
  // on_page_load is the trigger
  if (input_store === null) {
    return [dash_clientside.no_update, dash_clientside.no_update, slider];
  }
  if (slider === start && start === input_store) {
    // To prevent filter_action to be triggered after on_page_load
    return [
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }
  return [input_store, input_store, input_store];
}

window.dash_clientside = {
  ...window.dash_clientside,
  slider: { update_slider_values: update_slider_values },
};
