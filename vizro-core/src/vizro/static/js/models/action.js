/**
 * Prevents an "actions chain" from running when guard_data is True (when trigger object is just created).
 *
 * @param {*} trigger_value - The value to return if the guard allows the chain to proceed.
 * @param {boolean|null} guard_data
 *        true -> The component was just created; skip running actions, and set guard to False.
 *        null -> Guard component does not exist; treat as a genuine trigger.
 *        false -> Guard component exists and is set to False; treat as a genuine trigger.
 * @returns {*} Either the original `trigger_value` (run the chain) or dash_clientside.no_update (skip).
 */
function guard_action_chain(trigger_value, guard_data, trigger_component_id) {
  if (guard_data === true) {
    // Case 1: Guard component has data = true.
    // This means that the trigger component was just created,
    // so we must skip running the actions chain - it’s not a genuine trigger.
    console.debug(
      `Not running actions chain (guard is True) -> Trigger component: ${trigger_component_id}`,
    );

    // Set the guard component's data to false so that future triggers from this component are treated as genuine.
    // We must use set_props here rather than using Output(component_guard_id, "data") because the
    // component might not exist. This is allowed for a state with allow_optional=True but not for an Output.
    dash_clientside.set_props(`${trigger_component_id}_guard_actions_chain`, {
      data: false,
    });

    // Return dash_clientside.no_update to prevent actions chain from running.
    return dash_clientside.no_update;
  } else if (guard_data === null) {
    // Case 2: Guard component does not exist.
    // This means the component is not using the guard mechanism,
    // so it’s a genuine trigger and the actions chain should run.
    console.debug(
      `Running actions chain (no guard exists) -> Trigger component: ${trigger_component_id}`,
    );
  } else if (guard_data === false) {
    // Case 3: Guard component exists and is explicitly set to false.
    // This means the trigger did not come from component creation,
    // so it’s a genuine trigger and the actions chain should run.
    console.debug(
      `Running actions chain (guard is False) -> Trigger component: ${trigger_component_id}`,
    );
  }

  // In all "genuine trigger" cases, return the original trigger_value so the actions chain can proceed.
  return trigger_value;
}

window.dash_clientside = {
  ...window.dash_clientside,
  action: {
    guard_action_chain: guard_action_chain,
  },
};
