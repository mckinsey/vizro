// Mock dash_clientside first
global.dash_clientside = {
  no_update: "no_update",
};

// Mock window.dash_clientside
global.window = {
  dash_clientside: global.dash_clientside,
};

// Import the module to test
require("../../../src/vizro/static/js/models/dropdown.js");

describe("update_dropdown_select_all", () => {
  const mockOptions = [
    { value: "__SELECT_ALL" },
    { value: "option1" },
    { value: "option2" },
    { value: "option3" },
  ];

  const realOptions = ["option1", "option2", "option3"];

  describe("when Select All option is clicked", () => {
    test("should select all options when Select All is clicked and not all options are selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["__SELECT_ALL", "option1"],
        mockOptions
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toEqual(realOptions);
    });

    test("should deselect all options when Select All is clicked and all options are already selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["__SELECT_ALL", "option1", "option2", "option3"],
        mockOptions
      );

      expect(result[0]).toBe(false);
      expect(result[1]).toEqual([]);
    });

    test("should select all options when only Select All is clicked", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["__SELECT_ALL"],
        mockOptions
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toEqual(realOptions);
    });
  });

  describe("when regular dropdown item is clicked", () => {
    test("should set select all to true when all real options are selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["option1", "option2", "option3"],
        mockOptions
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should set select all to false when not all real options are selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["option1", "option2"],
        mockOptions
      );

      expect(result[0]).toBe(false);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should set select all to false when only one option is selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["option1"],
        mockOptions
      );

      expect(result[0]).toBe(false);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should set select all to false when no options are selected", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        [],
        mockOptions
      );

      expect(result[0]).toBe(false);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });
  });

  describe("edge cases", () => {
    test("should handle empty options array", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        [],
        []
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle options array with only __SELECT_ALL", () => {
      const selectAllOnlyOptions = [];

      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["__SELECT_ALL"],
        selectAllOnlyOptions
      );

      expect(result[0]).toBe(false);
      expect(result[1]).toEqual([]);
    });

    test("should filter out __SELECT_ALL from real options correctly", () => {
      const mixedOptions = [
        { value: "option1" },
        { value: "__SELECT_ALL" },
        { value: "option2" },
        { value: "option3" },
      ];

      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["option1", "option2", "option3"],
        mixedOptions
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle dropdown value with mixed real options and __SELECT_ALL", () => {
      const result = window.dash_clientside.dropdown.update_dropdown_select_all(
        ["option1", "__SELECT_ALL", "option2"],
        mockOptions
      );

      expect(result[0]).toBe(true);
      expect(result[1]).toEqual(realOptions);
    });
  });
});
