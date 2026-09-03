// Suffixes appended to the parent selector id when DateTimePicker builds its sub-components.
// Must stay in sync with the ids built in vizro.models._components.form.datetime_picker.DateTimePicker.build:
//   - range:  "{id}-date-start" and "{id}-date-end" (two DatePickerInput type=default),
//             "{id}-time-start" and "{id}-time-end" (two TimePickers),
//             "{id}" (proxy dcc.Store).
//   - single: "{id}-date" (DatePickerInput type=default),
//             "{id}-time" (TimePicker),
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
 * Synchronizes the proxy dcc.Store with the four sub-components that implement a range DateTimePicker:
 *   - dmc.DatePickerInput at `{id}-date-start` and `{id}-date-end`
 *   - dmc.TimePicker     at `{id}-time-start` and `{id}-time-end`
 *
 * Two directions:
 *  - A sub-component changed -> recompute the [start_iso, end_iso] tuple and push it into the Store;
 *    leave sub-components alone. If either date is missing the partial state is ignored (Store keeps
 *    its previous valid value) so the actions chain doesn't oscillate while the user is mid-edit.
 *  - The Store changed externally (URL sync on page load, reset button, set_control, custom action)
 *    -> split each Store entry into a date and time and push them into the sub-components. This does
 *    NOT touch the guard: whoever wrote the Store owns it. URL sync and reset raise the guard
 *    themselves before writing so the chain stays suppressed; set_control leaves it down on purpose
 *    so the target control's actions chain (its update_targets) fires. Raising the guard here would
 *    conflate the two and silently swallow set_control-driven updates (vizro-internal#2973).
 */
function update_range_datetime_picker_store(
  store_data,
  date_start_value,
  date_end_value,
  time_start_value,
  time_end_value,
  selector_id,
) {
  const DATE_START_SUFFIX = "-date-start.value";
  const DATE_END_SUFFIX = "-date-end.value";
  const TIME_START_SUFFIX = "-time-start.value";
  const TIME_END_SUFFIX = "-time-end.value";

  const triggered = dash_clientside.callback_context.triggered[0];
  if (!triggered) return dash_clientside.no_update;

  console.debug("update_range_datetime_picker_store", triggered);

  const prop_id = triggered.prop_id;
  const isComponentTrigger =
    prop_id.endsWith(DATE_START_SUFFIX) ||
    prop_id.endsWith(DATE_END_SUFFIX) ||
    prop_id.endsWith(TIME_START_SUFFIX) ||
    prop_id.endsWith(TIME_END_SUFFIX);

  if (isComponentTrigger) {
    // Both ends of the range need a date for the filter to make sense. While the user is mid-selection
    // keep the previous Store value to avoid action-chain churn (which would otherwise fire the actions
    // chain — including any control sync — on an incomplete range). dmc.DatePickerInput clears to null,
    // but guard on "" too (as the single-mode callback below already does) so an empty string can never
    // leak a half-range into the Store. A set date is always a truthy "YYYY-MM-DD" string.
    if (!date_start_value || !date_end_value) return dash_clientside.no_update;

    const start_iso = _combine_date_time(date_start_value, time_start_value);
    const end_iso = _combine_date_time(date_end_value, time_end_value);
    // Idempotence guard: if the recomputed pair already equals the Store, don't rewrite it. An
    // external write lands in the branch below, which pushes the Store values into the sub-components;
    // those changes re-enter here. Without this check we would echo the identical value back into the
    // Store, and because this callback no longer raises the guard that echo could re-trigger the
    // actions chain. A real edit always differs from the Store, so it still passes.
    if (
      Array.isArray(store_data) &&
      start_iso === store_data[0] &&
      end_iso === store_data[1]
    ) {
      return dash_clientside.no_update;
    }
    return [
      [start_iso, end_iso],
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
      dash_clientside.no_update,
    ];
  }

  // Store changed externally -> push values into the sub-components. Do NOT raise the guard here
  // (see the docstring): the writer owns it, so set_control-driven updates reach the target's chain.
  const store = Array.isArray(store_data) ? store_data : [null, null];
  const [start_date, start_time] = _split_iso(store[0]);
  const [end_date, end_time] = _split_iso(store[1]);

  return [
    dash_clientside.no_update,
    start_date,
    end_date,
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
    // Idempotence guard (see the range callback above): don't echo the Store's own value back into it,
    // which — now that this callback no longer raises the guard — could re-trigger the actions chain.
    if (iso === store_data) return dash_clientside.no_update;
    return [iso, dash_clientside.no_update, dash_clientside.no_update];
  }

  // Store changed externally -> push values into the sub-components. Do NOT raise the guard here
  // (see the docstring): the writer owns it, so set_control-driven updates reach the target's chain.
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
