// Suffixes appended to the parent selector id when DateTimePicker builds its sub-components.
// Must stay in sync with the ids built in vizro.models._components.form.datetime_picker.DateTimePicker.build:
//   - range:  "{id}-date" (DatePickerInput type=range),
//             "{id}-time-start" and "{id}-time-end" (two clearable TimePickers),
//             "{id}" (proxy dcc.Store).
//   - single: "{id}-date" (DatePickerInput type=default),
//             "{id}-time" (clearable TimePicker),
//             "{id}" (proxy dcc.Store).

/**
 * Combine a date string and an optional time string into the ISO value stored in the proxy.
 *  - (null, _)        -> null (no date == no filter target)
 *  - (date, null|"")  -> "YYYY-MM-DD"            (time cleared; filter pads to 00:00 / 23:59)
 *  - (date, time)     -> "YYYY-MM-DDTHH:MM[:SS]"
 */
function _combine_date_time(date, time) {
  if (date == null || date === "") return null;
  if (time == null || time === "") return date;
  return `${date}T${time}`;
}

/**
 * Split a stored ISO string back into [date_part, time_part] for the sub-components.
 * Accepts both "T" (Python emits this) and " " (Mantine emits this) as the separator.
 * The time part is returned as "" (not null) when missing — dmc.TimePicker only clears when fed
 * an empty string; null is ignored, leaving stale displayed values.
 * Returns [null, ""] for null/empty input, [date, ""] for date-only strings.
 */
function _split_iso(value) {
  if (value == null || typeof value !== "string" || value === "")
    return [null, ""];
  let idx = value.indexOf("T");
  if (idx === -1) idx = value.indexOf(" ");
  if (idx === -1) return [value, ""];
  return [value.slice(0, idx), value.slice(idx + 1)];
}

/**
 * Synchronizes the proxy dcc.Store with the three sub-components that implement a range DateTimePicker:
 *   - dmc.DatePickerInput(type="range") at `{id}-date` -> [start_date, end_date]
 *   - dmc.TimePicker(clearable=True)    at `{id}-time-start` and `{id}-time-end`
 *
 * Two directions:
 *  - A sub-component changed -> recompute the [start_iso, end_iso] tuple and push it into the Store;
 *    leave sub-components alone. If either date is missing the partial state is ignored (Store keeps
 *    its previous valid value) so the actions chain doesn't oscillate during a fresh range selection.
 *  - The Store changed externally (URL sync on page load, reset button, custom action) -> split each
 *    Store entry into a date and time, push them into the sub-components, and raise the guard so the
 *    downstream actions chain does NOT fire on this propagation.
 */
function update_range_datetime_picker_store(
  store_data,
  date_value,
  time_start_value,
  time_end_value,
  selector_id,
) {
  const DATE_SUFFIX = "-date.value";
  const TIME_START_SUFFIX = "-time-start.value";
  const TIME_END_SUFFIX = "-time-end.value";

  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return dash_clientside.no_update;

  console.debug("update_range_datetime_picker_store", triggered);

  const prop_id = triggered.prop_id;
  const isComponentTrigger =
    prop_id.endsWith(DATE_SUFFIX) ||
    prop_id.endsWith(TIME_START_SUFFIX) ||
    prop_id.endsWith(TIME_END_SUFFIX);

  if (isComponentTrigger) {
    const dates = Array.isArray(date_value) ? date_value : [null, null];
    // Both ends of the range need a date for the filter to make sense. While the user is mid-selection
    // (first click made, second pending) keep the previous Store value to avoid action-chain churn.
    if (dates[0] == null || dates[1] == null) return dash_clientside.no_update;

    const start_iso = _combine_date_time(dates[0], time_start_value);
    const end_iso = _combine_date_time(dates[1], time_end_value);
    return [
      [start_iso, end_iso],
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }

  // Store changed externally -> push values into the sub-components and raise the guard.
  dash_clientside.set_props(`${selector_id}_guard_actions_chain`, {
    data: true,
  });

  const store = Array.isArray(store_data) ? store_data : [null, null];
  const [start_date, start_time] = _split_iso(store[0]);
  const [end_date, end_time] = _split_iso(store[1]);

  return [
    dash_clientside.no_update,
    [start_date, end_date],
    start_time,
    end_time,
  ];
}

/**
 * Single-mode counterpart: one DatePickerInput + one clearable TimePicker, glued by a proxy dcc.Store.
 * Same two-direction sync model as the range variant.
 */
function update_single_datetime_picker_store(
  store_data,
  date_value,
  time_value,
  selector_id,
) {
  const DATE_SUFFIX = "-date.value";
  const TIME_SUFFIX = "-time.value";

  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return dash_clientside.no_update;

  console.debug("update_single_datetime_picker_store", triggered);

  const prop_id = triggered.prop_id;
  const isComponentTrigger =
    prop_id.endsWith(DATE_SUFFIX) || prop_id.endsWith(TIME_SUFFIX);

  if (isComponentTrigger) {
    // No date -> nothing to filter on. Keep the previous Store value rather than nulling it out so a
    // transient empty state doesn't fire the actions chain.
    if (date_value == null || date_value === "")
      return dash_clientside.no_update;

    const iso = _combine_date_time(date_value, time_value);
    return [iso, dash_clientside.no_update, dash_clientside.no_update];
  }

  // Store changed externally -> push values into the sub-components and raise the guard.
  dash_clientside.set_props(`${selector_id}_guard_actions_chain`, {
    data: true,
  });

  const [date, time] = _split_iso(store_data);
  return [dash_clientside.no_update, date, time];
}

window.dash_clientside = {
  ...window.dash_clientside,
  datetime_picker: {
    update_range_datetime_picker_store: update_range_datetime_picker_store,
    update_single_datetime_picker_store: update_single_datetime_picker_store,
  },
};
