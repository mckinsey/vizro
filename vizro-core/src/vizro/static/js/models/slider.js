export function _update_slider_values(start, slider, input_store, self_data) {
  var end_value, trigger_id, is_on_page_load_triggered=false;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }

  // input form component is the trigger
  if (trigger_id === `${self_data["id"]}_end_value`) {
    if (isNaN(start)) {
      return dash_clientside.no_update;
    }
    end_value = start;

  // slider component is the trigger
  } else if (trigger_id === self_data["id"]) {
    end_value = slider;

  // on_page_load is the trigger
  } else {
    is_on_page_load_triggered = true;
    end_value = input_store !== null ? input_store : self_data["min"];
  }

  end_value = Math.min(Math.max(self_data["min"], end_value), self_data["max"]);

  if (is_on_page_load_triggered && !self_data["is_dynamic_build"]) {
    return [dash_clientside.no_update, dash_clientside.no_update, end_value];
  }
  return [end_value, end_value, end_value];

}
