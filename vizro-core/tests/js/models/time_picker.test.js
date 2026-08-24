/**
 * @jest-environment jsdom
 */

// Mock dash_clientside
global.dash_clientside = {
  no_update: Symbol("no_update"),
  set_props: jest.fn(),
  callback_context: {
    triggered: [],
  },
};

// Import the module (registers update_range_time_picker_store on window.dash_clientside.time_picker)
require("../../../src/vizro/static/js/models/time_picker.js");

describe("update_range_time_picker_store", () => {
  let update_range_time_picker_store;

  beforeEach(() => {
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Reset triggered to empty before each test.
    global.dash_clientside.callback_context.triggered = [];

    // Get the function from the registered namespace.
    update_range_time_picker_store =
      global.dash_clientside.time_picker.update_range_time_picker_store;
  });

  describe("when there is no trigger (empty callback_context.triggered)", () => {
    test("should return no_update and not call set_props", () => {
      const result = update_range_time_picker_store(
        ["09:00", "17:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should not log when there is no trigger", () => {
      update_range_time_picker_store(
        ["09:00", "17:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(console.debug).not.toHaveBeenCalled();
    });
  });

  describe("when the start picker triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "tp-1-start.value" },
      ];
    });

    test("should push both values into the Store when both are set", () => {
      const result = update_range_time_picker_store(
        ["09:00", "18:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toEqual([
        ["10:00", "18:00"],
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when start_val is null", () => {
      const result = update_range_time_picker_store(
        ["09:00", "18:00"],
        null,
        "18:00",
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when end_val is null", () => {
      const result = update_range_time_picker_store(
        ["10:00", "17:00"],
        "10:00",
        null,
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when start_val is undefined", () => {
      const result = update_range_time_picker_store(
        ["09:00", "18:00"],
        undefined,
        "18:00",
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });

    test("should return no_update when end_val is undefined", () => {
      const result = update_range_time_picker_store(
        ["10:00", "17:00"],
        "10:00",
        undefined,
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });

    test("should return no_update when both values are null", () => {
      const result = update_range_time_picker_store(
        ["09:00", "17:00"],
        null,
        null,
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });
  });

  describe("when the end picker triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "tp-1-end.value" },
      ];
    });

    test("should push both values into the Store when both are set", () => {
      const result = update_range_time_picker_store(
        ["10:00", "17:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toEqual([
        ["10:00", "18:00"],
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when end_val is null", () => {
      const result = update_range_time_picker_store(
        ["10:00", "17:00"],
        "10:00",
        null,
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });

    test("should return no_update when start_val is null", () => {
      const result = update_range_time_picker_store(
        ["09:00", "18:00"],
        null,
        "18:00",
        "tp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });
  });

  describe("when the Store triggers the callback (external change)", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "tp-1.data" },
      ];
    });

    test("should push both Store values into the pickers and raise the guard", () => {
      const result = update_range_time_picker_store(
        ["09:00", "17:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, "09:00", "17:00"]);
      expect(dash_clientside.set_props).toHaveBeenCalledTimes(1);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "tp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should propagate null Store values to the pickers and still raise the guard", () => {
      const result = update_range_time_picker_store(
        [null, null],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, null, null]);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "tp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should propagate an asymmetric [null, value] Store tuple to the pickers", () => {
      const result = update_range_time_picker_store(
        [null, "17:00"],
        "10:00",
        "18:00",
        "tp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, null, "17:00"]);
    });
  });
});
