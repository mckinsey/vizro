/**
 * @jest-environment jsdom
 */

// Mock dash_clientside
global.dash_clientside = {
  no_update: Symbol("no_update"),
};

// Import the module
require("../../../src/vizro/static/js/models/ag_grid.js");

describe("update_ag_grid_action_trigger", () => {
  let update_ag_grid_action_trigger;

  beforeEach(() => {
    jest.clearAllMocks();

    // Get the function from the global object
    update_ag_grid_action_trigger =
      global.dash_clientside.ag_grid.update_ag_grid_action_trigger;
  });

  test("should return no_update when both inputs are undefined", () => {
    const result = update_ag_grid_action_trigger(undefined, undefined);

    expect(result).toBe(dash_clientside.no_update);
  });

  test("should return both values when cellClicked is defined and selectedRows is undefined", () => {
    const cellClicked = { row: 1, column: "name" };

    const result = update_ag_grid_action_trigger(cellClicked, undefined);

    // Note: `undefined` is not JSON-serializable, so it gets removed before the payload reaches Python.
    expect(result).toEqual({
      cellClicked,
      selectedRows: undefined,
    });
  });

  test("should return both values when cellClicked is undefined and selectedRows is defined", () => {
    const selectedRows = [{ id: 1 }, { id: 2 }];

    const result = update_ag_grid_action_trigger(undefined, selectedRows);

    // Note: `undefined` is not JSON-serializable, so it gets removed before the payload reaches Python.
    expect(result).toEqual({
      cellClicked: undefined,
      selectedRows,
    });
  });

  test("should return both values when both inputs are defined", () => {
    const cellClicked = { row: 1, column: "name" };
    const selectedRows = [{ id: 1 }, { id: 2 }];

    const result = update_ag_grid_action_trigger(cellClicked, selectedRows);

    expect(result).toEqual({
      cellClicked,
      selectedRows,
    });
  });

  test("should treat null as a real value and return it", () => {
    const result = update_ag_grid_action_trigger(null, null);

    // Note: `null` is JSON-serializable, and it's converted to None when it reaches Python.
    expect(result).toEqual({
      cellClicked: null,
      selectedRows: null,
    });
  });
});
