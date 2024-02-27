export function _update_date_picker_values(value, input_store, self_data) {
  if (value === null) {
    return [input_store, input_store];
  } else {
    return [value, value];
  }
}
