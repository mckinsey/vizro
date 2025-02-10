function update_dropdown_values(
  checklist_value = [],
  value = [],
  options = [],
) {
  const ctx = dash_clientside.callback_context.triggered;
  if (!ctx.length) return dash_clientside.no_update;

  const triggeredId = ctx[0]["prop_id"].split(".")[0];
  const options_list = options.map((dict) => dict["value"]);
  const updated_options = options_list.filter((element) => element !== "ALL");

  const isTriggeredByChecklist = triggeredId.includes("_checklist_all");
  const hasAllSelected = value.includes("ALL");
  const allOptionsSelected = value.length === updated_options.length;

  if (isTriggeredByChecklist) {
    return value.length === updated_options.length + 1
      ? [[], []]
      : [updated_options, ["ALL"]];
  }

  if (hasAllSelected) {
    return value.length === updated_options.length + 1
      ? [[], []]
      : [updated_options, ["ALL"]];
  }

  return allOptionsSelected ? [updated_options, ["ALL"]] : [value, []];
}

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_values: update_dropdown_values,
  },
};
