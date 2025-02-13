function update_checklist_values(
  checklist_all_value,
  checklist_value = [],
  options = [],
) {
  const triggeredId = dash_clientside.callback_context.triggered_id;
  const allSelected = checklist_value.length === options.length;

  if (triggeredId.includes("select_all")) {
    return checklist_all_value ? [true, options] : [false, []];
  }

  return allSelected ? [true, checklist_value] : [false, checklist_value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};
