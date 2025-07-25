// Mock dash_clientside first
global.dash_clientside = {
  no_update: "no_update",
  callback_context: {
    triggered_id: null,
  },
};

// Mock window.dash_clientside
global.window = {
  dash_clientside: global.dash_clientside,
};

// Import the module to test
require("../../../src/vizro/static/js/models/checklist.js");

describe("update_checklist_select_all", () => {
  const mockOptions = [
    { value: "option1" },
    { value: "option2" },
    { value: "option3" },
  ];
  const selectAllId = "select-all-checkbox";

  beforeEach(() => {
    // Reset callback context before each test
    global.dash_clientside.callback_context.triggered_id = null;
  });

  describe("when Select All checkbox is clicked", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id = selectAllId;
    });

    test("should select all options when select_all_value is true", () => {
      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          true,
          [],
          mockOptions,
          selectAllId,
        );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toEqual(["option1", "option2", "option3"]);
    });

    test("should deselect all options when select_all_value is false", () => {
      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          false,
          ["option1", "option2"],
          mockOptions,
          selectAllId,
        );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toEqual([]);
    });
  });

  describe("when regular checklist item is clicked", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id = "some-other-id";
    });

    test("should set select all to true when all options are selected", () => {
      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          false,
          ["option1", "option2", "option3"],
          mockOptions,
          selectAllId,
        );

      expect(result[0]).toBe(true);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should set select all to false when not all options are selected", () => {
      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          true,
          ["option1", "option2"],
          mockOptions,
          selectAllId,
        );

      expect(result[0]).toBe(false);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should set select all to false when no options are selected", () => {
      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          false,
          [],
          mockOptions,
          selectAllId,
        );

      expect(result[0]).toBe(false);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });
  });

  describe("edge cases", () => {
    test("should handle empty options array", () => {
      global.dash_clientside.callback_context.triggered_id = "some-other-id";

      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          false,
          [],
          [],
          selectAllId,
        );

      expect(result[0]).toBe(true);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle select all with empty options array", () => {
      global.dash_clientside.callback_context.triggered_id = selectAllId;

      const result =
        window.dash_clientside.checklist.update_checklist_select_all(
          true,
          [],
          [],
          selectAllId,
        );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toEqual([]);
    });
  });
});
