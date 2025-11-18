function update_graph_actions_trigger_prop(clickData, selectedData) {
  // TODO NOW PP: Add a comment
  //
  if (
    dash_clientside.callback_context.triggered.some(t => t.prop_id.includes("clickData")) &&
    JSON.stringify(selectedData) === '{"points":[]}'
  ){
    console.log("clickData:", clickData);
    return [clickData];
  }
  if (!dash_clientside.callback_context.triggered.some(t => t.prop_id.includes("selectedData"))) {
    return dash_clientside.no_update;
  }
  return [selectedData];
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_actions_trigger_prop: update_graph_actions_trigger_prop,
  },
};
