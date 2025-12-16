/**
 * Propagate clickData.points, selectedData.points, null or dash_clientside.no_update to graph's action trigger.
 *
 * Behavior:
 * - If `selectedData` is triggered:
 *   - With no points selected -> return dash_clientside.no_update (see the reason in the comment below).
 *   - With points selected -> return `selectedData`.
 * - If only `clickData` is triggered:
 *   - If the graph supports box selection (has "Box Select" in the modebar) AND clickmode is "event+select"
 *       -> return dash_clientside.no_update (see the reason in the comment below).
 *   - Otherwise -> return clickData.
 *
 * @param {Object|null} clickData     Plotly clickData from the graph.
 * @param {Object|null} selectedData  Plotly selectedData from the graph.
 * @param {Object|null} figure        Figure object used to inspect layout / clickmode.
 * @param {string}      figureId      DOM id of the graph container used to check for modebar options.
 * @returns {Array|null|dash_clientside.no_update} One of: clickData.points, selectedData.points, null or dash_clientside.no_update.
 */
function update_graph_action_trigger(
  clickData,
  selectedData,
  figure,
  figureId,
) {
  // Check whether selectedData is triggered.
  const triggeredIds = dash_clientside.callback_context.triggered;
  const isSelectedDataTriggered = triggeredIds.some((t) =>
    t.prop_id.endsWith(".selectedData"),
  );

  // If `selectedData` is triggered (regardless of `clickData`):
  if (isSelectedDataTriggered) {
    // If `selectedData` is triggered but has no points, stop the execution (return no_update).
    // This is primarily to avoid the bug that occurs when graph with selection is refreshed.
    // Refreshed graph sets `selectedData` to an empty object, which can trigger the action unintentionally.
    if (selectedData?.points?.length === 0) {
      return dash_clientside.no_update;
    }
    return selectedData?.points ?? null;
  }
  // If only `clickData` is triggered:
  else {
    // Check whether graph supports selection by looking for "Box Select" option in the graph's modebar in chart's header.
    const isGraphSelectable = !!document
      .getElementById(figureId)
      .querySelector('[data-title="Box Select"]');

    // Extract the "clickmode" setting from the figure layout or default template.
    // figure.layout.clickmode can be explicitly set with figure.update_layout(clickmode=...).
    // If not set, it falls back to the default "event+select" (which is set in figure.layout.template.layout.clickmode).
    const isClickmodeEventSelect =
      (figure?.layout?.clickmode ?? "event+select") === "event+select";

    // Ignore `clickData` event for "event+select" mode for charts that support `selectedData`.
    // This is a workaround for a Plotly issue where "event+select" is set,
    // and `clickData` changes but `selectedData` and graph's highlight stays unaffected.
    // See: https://github.com/plotly/plotly.js/issues/6898
    if (isGraphSelectable && isClickmodeEventSelect) {
      return dash_clientside.no_update;
    }
    return clickData?.points ?? null;
  }
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_action_trigger: update_graph_action_trigger,
  },
};
