// Suffixes appended to the parent selector id when the range TimePicker builds its two underlying
// dmc.TimePicker inputs. Must stay in sync with the ids built in
// vizro.models._components.form.time_picker.TimePicker.build (`f"{self.id}-start"` / `f"{self.id}-end"`).
const RANGE_PICKER_START_SUFFIX = "-start.value";
const RANGE_PICKER_END_SUFFIX = "-end.value";

/**
 * Synchronizes the proxy dcc.Store and the two underlying dmc.TimePicker inputs (start / end) that
 * together implement a range TimePicker.
 *
 * Two directions:
 *  - A picker changed -> push both picker values into the Store; leave pickers alone.
 *  - The Store changed externally (URL sync on page load, reset button, custom action) -> push both
 *    Store values back into the pickers and raise the guard so the downstream actions chain does NOT
 *    fire on this propagation.
 *
 * @param {Array|null}  store_data   - Current [start, end] tuple stored in the dcc.Store proxy.
 * @param {string|null} start_val    - Current value of the start picker.
 * @param {string|null} end_val      - Current value of the end picker.
 * @param {string}      selector_id  - The id of the parent Filter selector (and of the dcc.Store proxy).
 * @returns {Array|*} Three-tuple [store_output, start_output, end_output] with dash_clientside.no_update
 *                    where unchanged, or a single dash_clientside.no_update when there is no trigger.
 */
function update_range_time_picker_store(
  store_data,
  start_val,
  end_val,
  selector_id,
) {
  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return dash_clientside.no_update;

  console.debug("update_range_time_picker_store", triggered);

  const prop_id = triggered.prop_id;
  if (
    prop_id.endsWith(RANGE_PICKER_START_SUFFIX) ||
    prop_id.endsWith(RANGE_PICKER_END_SUFFIX)
  ) {
    // A picker changed -> push both picker values into the Store; leave pickers alone.
    // Skip until both pickers have a value, otherwise the Store would briefly hold [null, X].
    if (start_val == null || end_val == null) return dash_clientside.no_update;
    return [
      [start_val, end_val],
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }

  // The Store changed externally (URL load, reset, custom action) -> push both Store values into the
  // pickers and raise the guard so the actions chain does NOT fire on this propagation.
  dash_clientside.set_props(`${selector_id}_guard_actions_chain`, {
    data: true,
  });
  return [dash_clientside.no_update, store_data[0], store_data[1]];
}

window.dash_clientside = {
  ...window.dash_clientside,
  time_picker: {
    update_range_time_picker_store: update_range_time_picker_store,
  },
};
