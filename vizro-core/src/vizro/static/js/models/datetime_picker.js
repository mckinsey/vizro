// Suffixes appended to the parent selector id when the range DateTimePicker builds its two underlying
// dmc.DateTimePicker inputs. Must stay in sync with the ids built in
// vizro.models._components.form.datetime_picker.DateTimePicker.build (`f"{self.id}-start"` / `f"{self.id}-end"`).
// Inlined inside the function to avoid clashing with identically-named top-level constants in time_picker.js.

/**
 * Synchronizes the proxy dcc.Store and the two underlying dmc.DateTimePicker inputs (start / end) that
 * together implement a range DateTimePicker.
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
function update_range_datetime_picker_store(
  store_data,
  start_val,
  end_val,
  selector_id,
) {
  const RANGE_PICKER_START_SUFFIX = "-start.value";
  const RANGE_PICKER_END_SUFFIX = "-end.value";

  // Mantine's DateTimePicker always emits time 00:00:00 when the user picks a date from the calendar,
  // overriding the visual default set via timePickerProps. For the END picker we rewrite that to 23:59:00
  // (end-of-day) so the filter behaves intuitively, but only when the DATE actually changed — otherwise
  // we would clobber a user who deliberately set the time to 00:00 on an existing date.
  function _maybe_promote_end_to_eod(prev_store_end, new_end) {
    if (typeof new_end !== "string") return new_end;
    // Mantine accepts "T" as a separator on input but emits values with a space separator;
    // tolerate both when detecting the midnight suffix.
    const isMidnight = new_end.endsWith(" 00:00:00") || new_end.endsWith("T00:00:00");
    if (!isMidnight) return new_end;

    // Midnight emit on the END picker is almost always a Mantine reset (re-emit after our promotion,
    // or inner TimePicker state desync when the user clicks the calendar). If the previous stored
    // end time was non-midnight, the user did not actively type "00:00" — preserve that time on the
    // (possibly new) date. If the previous time was already midnight, fall back to 23:59:00 so the
    // initial state (and any user-cleared state) lands at end-of-day for the end picker.
    const newDate = new_end.split(/[T ]/)[0];
    const sep = new_end.includes(" ") ? " " : "T";

    let prevTime = null;
    if (typeof prev_store_end === "string") {
      const prevParts = prev_store_end.split(/[T ]/);
      if (prevParts.length === 2) prevTime = prevParts[1];
    }
    const prevIsMidnight =
      prevTime === "00:00:00" || prevTime === "00:00" || prevTime === null;
    const promotedTime = prevIsMidnight ? "23:59:00" : prevTime;
    return `${newDate}${sep}${promotedTime}`;
  }

  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return dash_clientside.no_update;

  console.debug("update_range_datetime_picker_store", triggered);

  const prop_id = triggered.prop_id;
  if (
    prop_id.endsWith(RANGE_PICKER_START_SUFFIX) ||
    prop_id.endsWith(RANGE_PICKER_END_SUFFIX)
  ) {
    // A picker changed -> push both picker values into the Store; leave pickers alone.
    // Skip until both pickers have a value, otherwise the Store would briefly hold [null, X].
    if (start_val == null || end_val == null) return dash_clientside.no_update;

    if (prop_id.endsWith(RANGE_PICKER_END_SUFFIX)) {
      const prev_end = Array.isArray(store_data) ? store_data[1] : null;
      const promoted = _maybe_promote_end_to_eod(prev_end, end_val);
      if (promoted !== end_val) {
        return [[start_val, promoted], dash_clientside.no_update, promoted];
      }
    }
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
  datetime_picker: {
    update_range_datetime_picker_store: update_range_datetime_picker_store,
  },
};
