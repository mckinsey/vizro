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
 *  - The Store changed externally (URL sync on page load, reset button, set_control, custom action) ->
 *    push both Store values back into the pickers. This callback deliberately does NOT touch the
 *    guard: whoever wrote the Store owns it. URL sync and reset raise the guard themselves before
 *    writing, so the chain stays suppressed; set_control leaves it down on purpose so the target
 *    control's actions chain (its update_targets) fires. Raising the guard here would conflate the two
 *    and silently swallow set_control-driven updates (vizro-internal#2973).
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
    // Skip until both pickers have a value, otherwise the Store would briefly hold a half-range
    // (e.g. ["10:00", ""]) that fires the actions chain — including any control sync — on an
    // incomplete range while the user is still mid-edit. dmc.TimePicker represents "empty" as ""
    // (not null), so a bare `== null` check would let the "" end through; guard on falsy instead.
    // A set time is always a truthy "HH:MM[:SS]" string, so `!value` catches only empty/cleared ends.
    if (!start_val || !end_val) return dash_clientside.no_update;
    // Idempotence guard: if the recomputed pair already equals the Store, don't rewrite it. An
    // external write lands in the branch below, which pushes the Store values into the pickers; those
    // picker changes re-enter here. Without this check we would write the identical value straight
    // back into the Store, and because this callback no longer raises the guard that echo could
    // re-trigger the actions chain. A real edit always differs from the Store, so it still passes.
    if (
      Array.isArray(store_data) &&
      start_val === store_data[0] &&
      end_val === store_data[1]
    ) {
      return dash_clientside.no_update;
    }
    return [
      [start_val, end_val],
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }

  // The Store changed externally (URL load, reset, set_control, custom action) -> push both Store
  // values into the pickers. Do NOT raise the guard here (see the docstring): the writer owns it.
  return [dash_clientside.no_update, store_data[0], store_data[1]];
}

window.dash_clientside = {
  ...window.dash_clientside,
  time_picker: {
    update_range_time_picker_store: update_range_time_picker_store,
  },
};
