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

// TODO PP NOW: Add tests. (Test it manually first and make it robust on different inputs)
/**
 * Replaces template variables in the format {{key}} within the given text with corresponding values from valuesMap.
 *
 * @param {string} text - The text containing template variables.
 * @param {Object} valuesMap - An object mapping keys to their replacement values.
 * @returns {string} The text with template variables replaced by their corresponding values.
 */
function replaceTemplateVariables(text, valuesMap) {
  if (typeof text !== "string") return text;

  return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    if (Object.prototype.hasOwnProperty.call(valuesMap, key)) {
      return String(valuesMap[key]);
    }

    // leave {{key}} unchanged
    return match;
  });
}

/**
 * Shows a progress notification which textual content can be adjusted based on action runtime arguments.
 *
 * @param {*} trigger - The trigger value (not used in this function).
 * @param {Array} notificationObject - The notification object to be displayed.
 * @param {Array} actionParameters - The list of action function parameter names.
 * @param {...*} actionRuntimeArguments - The current runtime values of the action function parameters.
 * @returns {void} - This function does not return a value. It updates the notification component directly using set_props instead to avoid duplication callback output dash exception.
 */
// TODO OQ: Should we clear notifications from the page before the new actions chain is triggered?
// TODO OQ: This would generally improve the UX. This comment is added here but should happen before progress is shown.
function show_progress_notification(
  trigger,
  notificationObject,
  actionParameters,
  ...actionRuntimeArguments
) {
  console.debug("Showing progress notification");

  // Map of action function parameter names and the current runtime values. For example: {"btn_n_clicks": 10}
  const actionParameterToRuntimeValueMap = Object.fromEntries(
    actionParameters.map((key, i) => [key, actionRuntimeArguments[i]]),
  );

  // Deep copy notificationObject to avoid mutating the original object.
  const copyNotificationObject = structuredClone(notificationObject);

  // Replace template in copyNotificationObject text with actual values from actionParameterToRuntimeValueMap.
  // It looks for patterns like {{key}} (where `key` represents an action parameter name) and replaces them with
  // the corresponding runtime value from actionParameterToRuntimeValueMap.
  copyNotificationObject[0].message.props.children = replaceTemplateVariables(
    copyNotificationObject[0].message.props.children,
    actionParameterToRuntimeValueMap,
  );

  // set_props used to avoid the duplication callback output dash exception.
  dash_clientside.set_props("vizro-notifications", {
    sendNotifications: copyNotificationObject,
  });
}

window.dash_clientside = {
  ...window.dash_clientside,
  action: {
    guard_action_chain: guard_action_chain,
    show_progress_notification: show_progress_notification,
  },
};
