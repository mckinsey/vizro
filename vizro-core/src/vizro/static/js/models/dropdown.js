// TO-DO: Check if this function triggered when a page is opened
function update_dropdown_values(
  value = [],
  checklist_value = [],
  options = [],
) {
  const ctx = dash_clientside.callback_context.triggered;
  let options_list = options.map((dict) => dict["value"]);
  let updated_options = options_list.filter((element) => element !== "ALL");

  if (!ctx.length) {
    return dash_clientside.no_update;
  } else {
    const triggeredId =
      dash_clientside.callback_context.triggered[0]["prop_id"].split(".")[0];
    if (!value.length) {
      return [[], []];
    }
    if (triggeredId.includes("_checklist_all")) {
      if (value.length === updated_options.length + 1) {
        return [[], []];
      }
      return [updated_options, ["ALL"]];
    } else {
      if (value.length === updated_options.length) {
        return [updated_options, ["ALL"]];
      } else {
        return [value, []];
      }
    }
  }
}

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_values: update_dropdown_values,
  },
};
