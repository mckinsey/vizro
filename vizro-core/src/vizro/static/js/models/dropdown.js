function update_dropdown_values(
  checklist_value = [],
  value = [],
  options = [],
  checklist_value_id,
) {
  const triggeredId = dash_clientside.callback_context.triggered_id;
  const options_list = options.map((dict) => dict["value"]);
  const updated_options = options_list.filter((element) => element !== "ALL");

  const isTriggeredByChecklist = triggeredId === checklist_value_id;
  const hasAllSelected = value.includes("ALL");
  const allOptionsSelected = value.length === updated_options.length;

  if (isTriggeredByChecklist) {
    return value.length === updated_options.length + 1
      ? [false, []]
      : [true, updated_options];
  }

  if (hasAllSelected) {
    return value.length === updated_options.length + 1
      ? [false, []]
      : [true, updated_options];
  }

  return allOptionsSelected ? [true, updated_options] : [false, value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_values: update_dropdown_values,
  },
};
