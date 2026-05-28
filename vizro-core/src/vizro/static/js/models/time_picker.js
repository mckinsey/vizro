
function update_time_picker_store(store_data, start_val, end_val, selectorId) {
  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return [window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update];

  console.debug("update_time_picker_store", triggered);

  const prop_id = triggered.prop_id;

  if (prop_id.includes("-start") || prop_id.includes("-end")) {
    // A picker changed — update the Store, leave pickers alone.
    if (start_val === null || start_val === undefined) return window.dash_clientside.no_update;
    if (end_val === null || end_val === undefined) return window.dash_clientside.no_update;
    return [[start_val, end_val], window.dash_clientside.no_update, window.dash_clientside.no_update];
  } else {
    // The Store changed (e.g. reset, or url set)
    // In case store_data is null return "" to reset the pickers to their empty state.
    dash_clientside.set_props(`${selectorId}_guard_actions_chain`, {data: true});
    if (!store_data || store_data.length < 2) return [window.dash_clientside.no_update, "", ""];
    // Otherwise update the pickers to match the store, leave the Store alone.
    return [window.dash_clientside.no_update, store_data[0], store_data[1]];
  }
}

window.dash_clientside = {
  ...window.dash_clientside,
  time_picker: {
    update_time_picker_store: update_time_picker_store,
  },
};
