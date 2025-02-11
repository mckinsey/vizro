function update_checklist_values(
  checklist_all_value = [],
  checklist_value = [],
  options = [],
) {
  const ctx = dash_clientside.callback_context.triggered;
  if (!ctx.length) return dash_clientside.no_update;

  const triggeredId = ctx[0]["prop_id"].split(".")[0];
  const allSelected = checklist_value.length === options.length;
  const noneSelected = checklist_value.length === 0;

  if (triggeredId.includes("select_all")) {
    return checklist_all_value.length
      ? [checklist_all_value, options]
      : [[], []];
  }

  if (checklist_all_value.length) {
    return noneSelected ? [[], []] : [[], checklist_value];
  }

  return allSelected ? [["ALL"], options] : [[], checklist_value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};
