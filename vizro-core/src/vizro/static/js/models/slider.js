/**
 * Updates slider values based on user interaction with either the slider component or text input.
 *
 * @param {number} slider_value - The current value of the slider component
 * @param {number} end_value - The value from the text input component
 * @param {string} slider_component_id - The ID of the slider component to identify trigger source
 * @returns {Array} Array containing [text_input_value, slider_value] where one element is updated and the other is dash_clientside.no_update
 * @throws {dash_clientside.PreventUpdate} When end_value is NaN (invalid number input)
 */
function update_slider_values(slider_value, end_value, slider_component_id) {
  console.debug("update_slider_values");
  const trigger_id = dash_clientside.callback_context.triggered_id;

  // slider component is triggered (slider_value)
  if (trigger_id === slider_component_id) {
    return [dash_clientside.no_update, slider_value];
  }

  // text form component is triggered (end_value)
  // Check if end_value is a valid number, JavaScript's Number.isNaN is used to check for NaN.
  // If end_value is not a valid number, throw PreventUpdate to stop further processing.
  // This includes cases where end_value is null, or an empty string.
  // JavaScript's Number() will convert empty strings and null to 0, so we check for that explicitly.
  if (
    end_value === null ||
    end_value === "" ||
    Number.isNaN(Number(end_value))
  ) {
    throw dash_clientside.PreventUpdate;
  }
  return [end_value, dash_clientside.no_update];
}

window.dash_clientside = {
  ...window.dash_clientside,
  slider: { update_slider_values: update_slider_values },
};
