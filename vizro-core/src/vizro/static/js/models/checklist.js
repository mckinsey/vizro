function update_checklist_values(value1 = [], value2 = [], options = []) {
  const ctx = dash_clientside.callback_context.triggered;
  if (!ctx.length) return dash_clientside.no_update;

  const triggeredId = ctx[0]["prop_id"].split(".")[0];
  const allSelected = value2.length === options.length;
  const noneSelected = value2.length === 0;

  if (triggeredId.includes("select_all")) {
    return value1.length ? [options, value1] : [[], []];
  }

  if (value1.length) {
    return noneSelected ? [[], []] : [value2, []];
  }

  return allSelected ? [options, ["ALL"]] : [value2, []];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_values: update_checklist_values,
  },
};
