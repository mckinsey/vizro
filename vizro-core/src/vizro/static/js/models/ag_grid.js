/**
 * Combine and propagate cellClicked and selectedRows AgGrid inputs to tables's action trigger.
 *
 *
 * @param {Object|null} cellClicked     AgGrid cellClicked from the table.
 * @param {Object|null} selectedRows    AgGrid selectedRows from the table.
 * @returns {Object} In format: {cellClicked: cellClicked, selectedRows: selectedRows}
 */
function update_ag_grid_action_trigger(cellClicked, selectedRows) {
  if (cellClicked === undefined && selectedRows === undefined) {
    return dash_clientside.no_update;
  }
  return { cellClicked: cellClicked, selectedRows: selectedRows };
}

window.dash_clientside = {
  ...window.dash_clientside,
  ag_grid: {
    update_ag_grid_action_trigger: update_ag_grid_action_trigger,
  },
};
