export function _update_range_slider_values(
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
  if (
    trigger_id === `${self_data["id"]}_start_value` ||
    trigger_id === `${self_data["id"]}_end_value`
  ) {
    if (isNaN(start) || isNaN(end)) {
      return dash_clientside.no_update;
    }
    [start_text_value, end_text_value] = [start, end];
  } else if (trigger_id === self_data["id"]) {
    [start_text_value, end_text_value] = [slider[0], slider[1]];
  } else {
    [start_text_value, end_text_value] =
      input_store !== null ? input_store : [slider[0], slider[1]];
  }

  start_value = Math.min(start_text_value, end_text_value);
  end_value = Math.max(start_text_value, end_text_value);
  start_value = Math.max(self_data["min"], start_value);
  end_value = Math.min(self_data["max"], end_value);
  slider_value = [start_value, end_value];

  return [start_value, end_value, slider_value, [start_value, end_value]];
}
