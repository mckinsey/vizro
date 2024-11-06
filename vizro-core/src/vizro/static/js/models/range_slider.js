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
    trigger_id,
    is_on_page_load_triggered=false;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }

  // input form component is the trigger
  if (
    trigger_id === `${self_data["id"]}_start_value` ||
    trigger_id === `${self_data["id"]}_end_value`
  ) {
    if (isNaN(start) || isNaN(end)) {
      return dash_clientside.no_update;
    }
    [start_text_value, end_text_value] = [start, end];

  // slider component is the trigger
  } else if (trigger_id === self_data["id"]) {
    [start_text_value, end_text_value] = [slider[0], slider[1]];

  // on_page_load is the trigger
  } else {
    is_on_page_load_triggered = true;
    [start_text_value, end_text_value] = input_store !== null ? input_store : [slider[0], slider[1]];
  }

  start_value = Math.min(start_text_value, end_text_value);
  end_value = Math.max(start_text_value, end_text_value);
  start_value = Math.max(self_data["min"], start_value);
  end_value = Math.min(self_data["max"], end_value);
  slider_value = [start_value, end_value];

  if (is_on_page_load_triggered && !self_data["is_dynamic_build"]) {
    return [dash_clientside.no_update, dash_clientside.no_update, dash_clientside.no_update, slider_value];
  }

  return [start_value, end_value, slider_value, slider_value];
}
