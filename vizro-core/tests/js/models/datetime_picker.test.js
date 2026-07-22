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

// Import the module (registers update_range_datetime_picker_store and
// update_single_datetime_picker_store on window.dash_clientside.datetime_picker).
require("../../../src/vizro/static/js/models/datetime_picker.js");

describe("update_range_datetime_picker_store", () => {
  let update_range_datetime_picker_store;

  beforeEach(() => {
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Reset triggered to empty before each test.
    global.dash_clientside.callback_context.triggered = [];

    // Get the function from the registered namespace.
    update_range_datetime_picker_store =
      global.dash_clientside.datetime_picker.update_range_datetime_picker_store;
  });

  describe("when there is no trigger (empty callback_context.triggered)", () => {
    test("should return no_update and not call set_props", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should not log when there is no trigger", () => {
      update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(console.debug).not.toHaveBeenCalled();
    });
  });

  describe("when a date sub-component triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1-date-start.value" },
      ];
    });

    test("should combine both date+time pairs into the Store when all are set", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toEqual([
        ["2026-01-01T10:00", "2026-12-31T18:00"],
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should emit date-only strings when both times are cleared", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        "2026-12-31",
        "",
        "",
        "dtp-1",
      );

      expect(result).toEqual([
        ["2026-01-01", "2026-12-31"],
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
    });

    test("should emit a mixed-precision tuple when only one time is set", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-20",
        "2026-12-29",
        "10:30",
        null,
        "dtp-1",
      );

      expect(result).toEqual([
        ["2026-01-20T10:30", "2026-12-29"],
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
    });

    test("should return no_update when start date is null", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        null,
        "2026-12-31",
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when end date is null", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        null,
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });
  });

  describe("when a time sub-component triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1-time-end.value" },
      ];
    });

    test("should combine both date+time pairs into the Store when all are set", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toEqual([
        ["2026-01-01T10:00", "2026-12-31T18:00"],
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when a date is still missing", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01", "2026-12-31"],
        "2026-01-01",
        null,
        "10:00",
        "18:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });
  });

  describe("when the Store triggers the callback (external change)", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1.data" },
      ];
    });

    test("should split each Store entry into date/time and raise the guard", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01T10:00", "2026-12-31T18:00"],
        "2026-06-15",
        "2026-06-20",
        "08:00",
        "20:00",
        "dtp-1",
      );

      // Return order: [store, date_start, date_end, time_start, time_end].
      expect(result).toEqual([
        dash_clientside.no_update,
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
      ]);
      expect(dash_clientside.set_props).toHaveBeenCalledTimes(1);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "dtp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should return empty-string times for date-only Store entries", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-20", "2026-12-29"],
        "2026-06-15",
        "2026-06-20",
        "08:00",
        "20:00",
        "dtp-1",
      );

      expect(result).toEqual([
        dash_clientside.no_update,
        "2026-01-20",
        "2026-12-29",
        "",
        "",
      ]);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "dtp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should accept a space separator (Mantine style) as well as T", () => {
      const result = update_range_datetime_picker_store(
        ["2026-01-01 10:00", "2026-12-31T18:00"],
        "2026-06-15",
        "2026-06-20",
        "08:00",
        "20:00",
        "dtp-1",
      );

      expect(result).toEqual([
        dash_clientside.no_update,
        "2026-01-01",
        "2026-12-31",
        "10:00",
        "18:00",
      ]);
    });

    test("should propagate null Store entries as [null, ''] and still raise the guard", () => {
      const result = update_range_datetime_picker_store(
        [null, null],
        "2026-06-15",
        "2026-06-20",
        "08:00",
        "20:00",
        "dtp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, null, null, "", ""]);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "dtp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should fall back to [null, null] when Store data is not an array", () => {
      const result = update_range_datetime_picker_store(
        null,
        "2026-06-15",
        "2026-06-20",
        "08:00",
        "20:00",
        "dtp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, null, null, "", ""]);
    });
  });
});

describe("update_single_datetime_picker_store", () => {
  let update_single_datetime_picker_store;

  beforeEach(() => {
    jest.clearAllMocks();
    console.debug = jest.fn();

    global.dash_clientside.callback_context.triggered = [];

    update_single_datetime_picker_store =
      global.dash_clientside.datetime_picker
        .update_single_datetime_picker_store;
  });

  describe("when there is no trigger (empty callback_context.triggered)", () => {
    test("should return no_update and not call set_props", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "2026-01-01",
        "10:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should not log when there is no trigger", () => {
      update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "2026-01-01",
        "10:00",
        "dtp-1",
      );

      expect(console.debug).not.toHaveBeenCalled();
    });
  });

  describe("when the date sub-component triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1-date.value" },
      ];
    });

    test("should combine date and time into the Store", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "2026-06-15",
        "08:00",
        "dtp-1",
      );

      expect(result).toEqual([
        "2026-06-15T08:00",
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should emit a date-only string when the time is cleared", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "2026-06-15",
        "",
        "dtp-1",
      );

      expect(result).toEqual([
        "2026-06-15",
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
    });

    test("should return no_update when the date is null", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        null,
        "08:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });

    test("should return no_update when the date is an empty string", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "",
        "08:00",
        "dtp-1",
      );

      expect(result).toBe(dash_clientside.no_update);
    });
  });

  describe("when the time sub-component triggers the callback", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1-time.value" },
      ];
    });

    test("should combine date and time into the Store", () => {
      const result = update_single_datetime_picker_store(
        "2026-01-01T10:00",
        "2026-06-15",
        "08:00",
        "dtp-1",
      );

      expect(result).toEqual([
        "2026-06-15T08:00",
        dash_clientside.no_update,
        dash_clientside.no_update,
      ]);
    });
  });

  describe("when the Store triggers the callback (external change)", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered = [
        { prop_id: "dtp-1.data" },
      ];
    });

    test("should split the Store value into date/time and raise the guard", () => {
      const result = update_single_datetime_picker_store(
        "2026-06-15T08:00",
        "2026-01-01",
        "10:00",
        "dtp-1",
      );

      expect(result).toEqual([
        dash_clientside.no_update,
        "2026-06-15",
        "08:00",
      ]);
      expect(dash_clientside.set_props).toHaveBeenCalledTimes(1);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "dtp-1_guard_actions_chain",
        { data: true },
      );
    });

    test("should return an empty-string time for a date-only Store value", () => {
      const result = update_single_datetime_picker_store(
        "2026-06-15",
        "2026-01-01",
        "10:00",
        "dtp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, "2026-06-15", ""]);
    });

    test("should propagate a null Store value as [null, ''] and still raise the guard", () => {
      const result = update_single_datetime_picker_store(
        null,
        "2026-01-01",
        "10:00",
        "dtp-1",
      );

      expect(result).toEqual([dash_clientside.no_update, null, ""]);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "dtp-1_guard_actions_chain",
        { data: true },
      );
    });
  });
});
