export function _update_slider_values(start, slider, input_store, self_data) {
  var end_value, trigger_id;

  trigger_id = dash_clientside.callback_context.triggered;
  if (trigger_id.length != 0) {
    trigger_id =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  }
  if (trigger_id === `${self_data["id"]}_end_value`) {
    if (isNaN(start)) {
      return dash_clientside.no_update;
    }
    end_value = start;
  } else if (trigger_id === self_data["id"]) {
    end_value = slider;
  } else {
    end_value = input_store !== null ? input_store : self_data["min"];
  }

  end_value = Math.min(Math.max(self_data["min"], end_value), self_data["max"]);

  return [end_value, end_value, end_value];
}
