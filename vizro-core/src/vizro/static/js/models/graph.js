function update_graph_actions_trigger_prop(clickData, selectedData, figure) {
  // TODO: Implement robust JS function!
  // TODO: Support if clickmode is not provided at all.
  // TODO NOW PP: Refactor + Add comments + Add description similar to the one from slider.js
  // TODO See is inputs=[State(...)] a new Dash bug?

  // If clickmode is overwritten from 'event+select' to 'event' and clickData is triggered, propagate clickData only.
  const clickmode = figure?.layout?.template?.layout?.clickmode ?? "event";
  if (clickmode === 'event' && dash_clientside.callback_context.triggered.some(t => t.prop_id.includes("clickData"))) {
    return clickData;
  }

  // Charts like: pie, area, line, funnel_area, density_heatmap, line_polar, treemap, parallel_coordinates do not support selectedData
  // For those type of charts we need take clickData and propagate to their actions_trigger store.
  // There's no other way to differentiate false clickData from bar chart and real clickData from pie chart.
  const isChartLineMode = figure?.data?.[0]?.mode === 'lines';
  const clickDataChartTypes = ['pie', 'funnelarea', 'histogram2d', 'treemap'];
  const chartType = figure?.data?.[0]?.type;
  if (isChartLineMode || clickDataChartTypes.includes(chartType)) {
    return clickData;
  }

  // Ignore "clickData" event for "event+select" mode for charts that support selectedData.
  if (!dash_clientside.callback_context.triggered.some(t => t.prop_id.includes("selectedData"))) {
    return dash_clientside.no_update;
  }

  return selectedData;
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_actions_trigger_prop: update_graph_actions_trigger_prop,
  },
};
