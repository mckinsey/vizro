function update_checklist_values(
  checklist_all_value,
  checklist_value = [],
  options = [],
  checklist_all_value_id,
) {
  const triggeredId = dash_clientside.callback_context.triggered_id;
  const allSelected = checklist_value.length === options.length;
  const options_list = options.map((dict) => dict["value"]);

  if (checklist_all_value_id === triggeredId) {
    return checklist_all_value ? [true, options_list] : [false, []];
  }

  return allSelected ? [true, checklist_value] : [false, checklist_value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};
