export function _update_date_picker_values(value, input_store) {
  if (
    value === null ||
    dash_clientside.callback_context.triggered.length === 0
  ) {
    return [input_store, input_store];
  }
  return [value, value];
}

export function _update_date_picker_position(clicks) {
  var element_id = window.dash_clientside.callback_context.inputs_list[0]["id"];
  var element = document.getElementById(element_id);
  var rect = element.getBoundingClientRect();
  var position =
    rect.y + 360 > window.innerHeight ? "top-start" : "bottom-start";

  return position;
}
