export function _update_slider_values(start, slider, input_store, self_data) {
  var text_value, trigger_id;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }
  if (trigger_id === `${self_data["id"]}_text_value`) {
    text_value = start;
  } else if (trigger_id === self_data["id"]) {
    text_value = slider;
  } else {
    text_value = input_store !== null ? input_store : self_data["min"];
  }

  text_value = Math.min(
    Math.max(self_data["min"], text_value),
    self_data["max"],
  );

  return [text_value, text_value, text_value];
}
