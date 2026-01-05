/**
 * Updates the dropdown selection state when the "Select All" option is toggled or when individual options are selected.
 *
 * @param {Array} dropdown_value - Array of currently selected dropdown values, may include "__SELECT_ALL"
 * @param {Array<Object>} options - Array of dropdown option objects, each containing a "value" property
 * @returns {Array} A tuple containing [isSelectAllChecked, newDropdownValue] where:
 *   - isSelectAllChecked (boolean): Whether the "Select All" checkbox should be checked
 *   - newDropdownValue (Array|dash_clientside.no_update): The new dropdown values or no_update if no change needed
 */
function update_dropdown_select_all(dropdown_value, options) {
  console.debug("update_dropdown_select_all");

  // Turn into array of values excluding the __SELECT_ALL one.
  const realOptions = options
    .map((dict) => dict["value"])
    .filter((value) => value !== "__SELECT_ALL");

  // Ensure `dropdown_value` is an array as Dropdown is multi=True.
  if (!Array.isArray(dropdown_value)) {
    dropdown_value = [dropdown_value];
  }

  // When "Select All" option is clicked (includes when clicks on checkbox itself and area next to checkbox).
  if (dropdown_value.includes("__SELECT_ALL")) {
    // All the real options are already selected, so untick the checkbox and empty the dropdown value.
    if (dropdown_value.length === realOptions.length + 1) {
      return [false, []];
    }
    // Otherwise tick the checkbox and set dropdown value to be all the real options.
    return [true, realOptions];
  }

  // A real option has been selected, so the only special treatment that's needed is to update the checkbox to reflect
  // whether all real options have been selected. The dropdown value itself doesn't need anything done to it.
  const allRealOptionsSelected = dropdown_value.length === realOptions.length;
  return [allRealOptionsSelected, dash_clientside.no_update];
}

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_select_all: update_dropdown_select_all,
  },
};
