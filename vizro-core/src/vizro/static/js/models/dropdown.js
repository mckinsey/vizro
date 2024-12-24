function update_dropdown_values(value = [], options = []) {
  let options_list = options.map((dict) => dict["value"]);
  let updated_options = options_list.filter((element) => element !== "ALL");

  if (!value.length) {
    return [[], []];
  }
  if (value.includes("ALL")) {
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

window.dash_clientside = {
  ...window.dash_clientside,
  dropdown: {
    update_dropdown_values: update_dropdown_values,
  },
};
