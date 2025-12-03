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
function update_graph_actions_trigger_prop(clickData, selectedData, figure, figureId) {
  // Check whether graph supports selection by looking for "Box Select" option in the graph's modebar in chart's header.
  const isGraphSelectable = !!document.getElementById(figureId).querySelector('[data-title="Box Select"]');

  // Extract the "clickmode" setting from the figure layout or default template.
  // figure.layout.clickmode can be defined if user has explicitly set it with figure.update_layout(clickmode=...).
  // figure.layout.template.layout.clickmode can be defined if user has overwritten the default template's clickmode.
  // By default, Vizro sets figure.layout.template.layout.clickmode to "event+select".
  const isClickmodeEventSelect = (
    figure?.layout?.clickmode ??
    figure?.layout?.template?.layout?.clickmode
  ) === "event+select";

  // Extract trigger IDs.
  const triggeredIds = dash_clientside.callback_context.triggered;
  const isClickDataTriggered = triggeredIds.some(t => t.prop_id.includes("clickData"));
  const isSelectedDataTriggered = triggeredIds.some(t => t.prop_id.includes("selectedData"));

  // Return clickData if:
  // 1. graph is not selectable or
  // 2. clickmode is not "event+select" (default value is overwritten) and clickData is triggered.
  if (!isGraphSelectable || (!isClickmodeEventSelect && isClickDataTriggered)) {
    return clickData;
  }

  // Ignore "clickData" event for "event+select" mode for charts that support selectedData.
  // This is a workaround for a Plotly issue where "event+select" is set,
  // and clickData changes but selectedData and graph's highlight stays unaffected.
  if (!isSelectedDataTriggered) {
    return dash_clientside.no_update;
  }

  // Otherwise, graph is selectable and selectedData is triggered.
  return selectedData;
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_actions_trigger_prop: update_graph_actions_trigger_prop,
  },
};
