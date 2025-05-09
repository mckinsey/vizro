function trigger_to_global_store(input, data) {
  return data;
}

function gateway(
  remaining_actions,
  trigger_to_actions_chain_mapper,
  action_trigger_actions_id,
  cycle_breaker_div,
  ...gateway_triggers
) {
  // Based on the triggered input, determines what is the next action to execute.
  var ctx_triggered,
    triggered_actions_chains_ids,
    actions_chain_to_trigger,
    next_action,
    trigger_next;

  ctx_triggered = dash_clientside.callback_context.triggered;

  // If the 'cycle_breaker_div' is triggered that means that at least one action is already executed.
  if (
    ctx_triggered.length == 1 &&
    ctx_triggered[0]["prop_id"].split(".")[0] === "cycle_breaker_div"
  ) {
    // If there's no more actions to execute, stop the loop perform.
    if (remaining_actions.length == 0) {
      throw dash_clientside.PreventUpdate;
    }
  }
  // Actions chain is triggered from the UI, find the list of actions that should be executed.
  else {
    triggered_actions_chains_ids = [];
    for (let i = 0; i < ctx_triggered.length; i++) {
      if (ctx_triggered[i]["prop_id"].split(".")[0] === "cycle_breaker_div") {
        // TODO: handle when a new action chain is started before the previous one has finished.
        continue;
      }
      triggered_actions_chains_ids.push(
        JSON.parse(ctx_triggered[i]["prop_id"].split(".")[0])["trigger_id"],
      );
    }

    // Trigger only the on_page_load action if exists.
    // Otherwise, a single regular (non on_page_load) actions chain is triggered.
    function findStringInList(list, string) {
      for (let i = 0; i < list.length; i++) {
        if (list[i].indexOf(string) !== -1) {
          // The on_page_load action found
          return list[i];
        }
      }
      // A single regular (non on_page_load) action is triggered.
      return list[0];
    }
    actions_chain_to_trigger = findStringInList(
      triggered_actions_chains_ids,
      "on_page_load",
    );
    remaining_actions =
      trigger_to_actions_chain_mapper[actions_chain_to_trigger];
  }

  next_action = remaining_actions[0];

  // Return dash.no_update for all outputs except for the next action
  trigger_next = [];
  for (let i = 0; i < action_trigger_actions_id.length; i++) {
    if (next_action === action_trigger_actions_id[i]) {
      trigger_next.push(null);
    } else {
      trigger_next.push(dash_clientside.no_update);
    }
  }

  return [remaining_actions.slice(1)].concat(trigger_next);
}

function after_action_cycle_breaker(data) {
  document.getElementById("cycle_breaker_div").click();
  return [];
}

window.dash_clientside = {
  ...window.dash_clientside,
  build_action_loop_callbacks: {
    trigger_to_global_store: trigger_to_global_store,
    gateway: gateway,
    after_action_cycle_breaker: after_action_cycle_breaker,
  },
};
