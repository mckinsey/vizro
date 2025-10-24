function update_graph_props_store(clickData, selectedData, propsStore) {


  console.debug("update_graph_props_store");

  // Reset to avoid stale data if new inputs are missing
  propsStore.click = null;
  propsStore.select = null;

  if (clickData && Array.isArray(clickData.points) && clickData.points.length > 0) {
    propsStore.click = clickData.points[0];
  }

  if (selectedData && Array.isArray(selectedData.points) && selectedData.points.length > 0) {
    propsStore.select = selectedData.points;
  }

  return [propsStore];
}

window.dash_clientside = {
  ...window.dash_clientside,
  graph: {
    update_graph_props_store: update_graph_props_store,
  },
};
