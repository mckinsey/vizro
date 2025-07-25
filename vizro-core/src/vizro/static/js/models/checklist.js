/**
 * Updates the checklist and select all checkbox state based on user interactions.
 *
 * @param {boolean} select_all_value - The current state of the "Select All" checkbox
 * @param {Array} checklist_value - Array of currently selected values in the checklist
 * @param {Array<Object>} options - Array of option objects, each containing a "value" property
 * @param {string} select_all_id - The ID of the "Select All" checkbox element
 * @returns {Array} Returns a tuple where:
 *   - First element: updated select all checkbox state or dash_clientside.no_update
 *   - Second element: updated checklist values array or dash_clientside.no_update
 *
 * @description
 * When the "Select All" checkbox is clicked:
 * - If checked, selects all available options in the checklist
 * - If unchecked, deselects all options in the checklist
 *
 * When a regular checklist item is clicked:
 * - Updates the "Select All" checkbox state based on whether all options are selected
 */
function update_checklist_select_all(
  select_all_value,
  checklist_value,
  options,
  select_all_id,
) {
  console.debug("update_checklist_select_all");

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
