/**
 * Updates range slider values based on user input from either the slider component or text form inputs.
 *
 * @param {number[]} slider_value - Array containing the current slider range values [min, max]
 * @param {number} start_value - The start value from text input
 * @param {number} end_value - The end value from text input
 * @param {string} slider_component_id - The ID of the slider component to check against triggered component
 * @returns {Array} Returns an array with three elements:
 *   - [0]: Updated slider value array or dash_clientside.no_update
 *   - [1]: Updated start value or dash_clientside.no_update
 *   - [2]: Updated end value or dash_clientside.no_update
 * @throws {dash_clientside.PreventUpdate} When start_value or end_value are NaN or start_value > end_value
 */
function update_range_slider_values(
  slider_value,
  start_value,
  end_value,
  slider_component_id,
) {
  console.debug("update_range_slider_values");
  const trigger_id = dash_clientside.callback_context.triggered_id;

  // slider component is triggered (slider_value)
  if (trigger_id === slider_component_id) {
    return [dash_clientside.no_update, slider_value[0], slider_value[1]];
  }

  // text form component is triggered (start_value or end_value)
  // Check if end_value or start_value are a valid number, JavaScript's Number.isNaN is used to check for NaN.
  // If start_value or end_value are not a valid number, throw PreventUpdate to stop further processing.
  // This includes cases where end_value is null, or an empty string.
  // JavaScript's Number() will convert empty strings and null to 0, so we check for that explicitly.
  if (
    isNaN(start_value) ||
    start_value === null ||
    start_value === "" ||
    end_value === null ||
    end_value === "" ||
    isNaN(end_value) ||
    start_value > end_value
  ) {
    throw dash_clientside.PreventUpdate;
  }
  return [
    [start_value, end_value],
    dash_clientside.no_update,
    dash_clientside.no_update,
  ];
}

window.dash_clientside = {
  ...window.dash_clientside,
  range_slider: { update_range_slider_values: update_range_slider_values },
};
