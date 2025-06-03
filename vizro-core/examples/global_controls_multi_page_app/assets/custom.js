function update_hidden_parameters(parameter_id_trigger, store_data) {
    return store_data["number_of_data_points"];
}

console.log("Custom JS loaded: update_hidden_parameter_page_1");

window.dash_clientside = {
  ...window.dash_clientside,
  custom: { update_hidden_parameters: update_hidden_parameters },
};
