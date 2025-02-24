function update_checklist_select_all(
  select_all_value,
  checklist_value,
  options,
  select_all_id,
) {
  // When "Select All" checkbox is clicked, set checklist value to be:
  // - all the values in options if checkbox is ticked (select_all_value=True)
  // - none of the options if checkbox is unticked (select_all_value=False)
  if (dash_clientside.callback_context.triggered_id === select_all_id) {
    const newChecklistValue = select_all_value
      ? options.map((dict) => dict["value"])
      : [];
    return [dash_clientside.no_update, newChecklistValue];
  }

  // Otherwise callback is triggered by clicking a "real" (non-"Select All") value in the checklist.
  // Now we tick or untick the checkbox depending on whether all the checklist values have been selected.
  const allOptionsSelected = checklist_value.length === options.length;
  return [allOptionsSelected, dash_clientside.no_update];
}

window.dash_clientside = {
  ...window.dash_clientside,
  checklist: {
    update_checklist_select_all: update_checklist_select_all,
  },
};
