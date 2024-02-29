export function _update_date_picker_values(value, input_store, self_data) {
  if (
    value === null ||
    dash_clientside.callback_context.triggered.length === 0
  ) {
    return [input_store, input_store];
  }
  return [value, value];
}
