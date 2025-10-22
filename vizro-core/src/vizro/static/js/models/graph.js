function update_graph_props_store(clickData, selectedData, propsStore) {
  console.debug("update_graph_props_store");

  propsStore["click"] = clickData["points"][0];
  propsStore["select"] = selectedData["points"];

  return [propsStore];
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_props_store: update_graph_props_store,
  },
};
