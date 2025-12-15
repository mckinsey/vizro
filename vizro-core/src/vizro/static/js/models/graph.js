/**
 * Decide whether a graph action should be triggered based on clickData / selectedData.
 *
 * Behavior:
 * - If the graph does NOT support box selection (no "Box Select" in the modebar) -> propagate clickData.
 * - If clickmode has been changed from "event+select" to something else and clickData is triggered -> propagate clickData.
 * - If previous conditions are not met it means that we are in "event+select" mode and that the graph supports selection -> return selectedData.
 *
 * @param {Object|null} clickData     Plotly clickData from the graph.
 * @param {Object|null} selectedData  Plotly selectedData from the graph.
 * @param {Object|null} figure        Figure object used to inspect layout / clickmode.
 * @param {string}      figureId      DOM id of the graph container used to check for modebar options.
 * @returns {Object|null}             One of clickData, selectedData, or dash_clientside.no_update.
 */
function update_graph_action_trigger(
  clickData,
  selectedData,
  figure,
  figureId,
) {
  // Check whether graph supports selection by looking for "Box Select" option in the graph's modebar in chart's header.
  const isGraphSelectable = !!document
    .getElementById(figureId)
    .querySelector('[data-title="Box Select"]');

  // Extract the "clickmode" setting from the figure layout or default template.
  // figure.layout.clickmode can be explicitly set with figure.update_layout(clickmode=...).
  // If not set, it falls back to the default "event+select" (which is set in figure.layout.template.layout.clickmode).
  const isClickmodeEventSelect =
    (figure?.layout?.clickmode ?? "event+select") === "event+select";

  // Extract trigger IDs.
  const triggeredIds = dash_clientside.callback_context.triggered;
  const isClickDataTriggered = triggeredIds.some((t) =>
    t.prop_id.includes("clickData"),
  );
  const isSelectedDataTriggered = triggeredIds.some((t) =>
    t.prop_id.includes("selectedData"),
  );

  // ADD THIS TO STOP ONLY []. KEEP IT HERE and not BELOW. -> Another solution. Treat selected_data == [] as no_update. Leave selected_data == null as valid and reset.
  if (
    isSelectedDataTriggered &&
    selectedData?.points !== undefined &&
    selectedData.points.length === 0
  ) {
    return dash_clientside.no_update;
  }

  // Return clickData if:
  // 1. Graph is not selectable or
  // 2. clickmode is not "event+select" (default value is overwritten) and clickData is triggered.
  if (!isGraphSelectable || (!isClickmodeEventSelect && isClickDataTriggered)) {
    // ADD THIS CODE:
    //    if (clickData?.points === undefined){
    //        return dash_clientside.no_update;
    //    }

    return clickData?.points ?? null;
  }

  // Ignore "clickData" event for "event+select" mode for charts that support selectedData.
  // This is a workaround for a Plotly issue where "event+select" is set,
  // and clickData changes but selectedData and graph's highlight stays unaffected.
  // See: https://github.com/plotly/plotly.js/issues/6898
  if (!isSelectedDataTriggered) {
    return dash_clientside.no_update;
  }

  // ADD THIS CODE:
  //  if (selectedData?.points === undefined || selectedData.points.length === 0) {
  //    return dash_clientside.no_update;
  //  }
  //  return selectedData?.points;

  // Otherwise, graph is selectable and selectedData is triggered.
  return selectedData?.points ?? null;
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_action_trigger: update_graph_action_trigger,
  },
};
