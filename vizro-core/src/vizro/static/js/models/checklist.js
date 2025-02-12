function update_checklist_values(
  checklist_all_value = [],
  checklist_value = [],
  options = [],
) {
  const triggeredId = dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
  const allSelected = checklist_value.length === options.length;

  if (triggeredId.includes("select_all")) {
    return checklist_all_value.length
      ? [checklist_all_value, options]
      : [[], []];
  }

  return allSelected ? [["ALL"], checklist_value] : [[], checklist_value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};
