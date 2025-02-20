function update_dropdown_select_all(dropdown_value, options) {
  // Turn into array of values excluding the ALL one.
  const realOptions = options
    .map((dict) => dict["value"])
    .filter((value) => value !== "ALL");

  // When "Select All" option is clicked (includes when clicks on checkbox itself and area next to checkbox).
  if (dropdown_value.includes("ALL")) {
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
  return [allRealOptionsSelected, dropdown_value];
}

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_select_all: update_dropdown_select_all,
  },
};
