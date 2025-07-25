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
    { value: "option1", label: "Option 1" },
    { value: "option2", label: "Option 2" },
    { value: "option3", label: "Option 3" },
  ];

  const updateDropdownSelectAll = (selectedValues) => {
    return window.dash_clientside.dropdown.update_dropdown_select_all(
      selectedValues,
      mockOptions,
    );
  };

  describe("when all real options are selected", () => {
    it("should set select all to true", () => {
      const selectedValues = ["option1", "option2", "option3"];
      const [selectAllValue, updateValue] =
        updateDropdownSelectAll(selectedValues);

      expect(selectAllValue).toBe(true);
      expect(updateValue).toBe(global.dash_clientside.no_update);
    });
  });

  describe("when not all real options are selected", () => {
    it.each([
      {
        description: "two options selected",
        selectedValues: ["option1", "option2"],
        expectedSelectAll: false,
      },
      {
        description: "one option selected",
        selectedValues: ["option1"],
        expectedSelectAll: false,
      },
      {
        description: "no options selected",
        selectedValues: [],
        expectedSelectAll: false,
      },
    ])(
      "should set select all to $expectedSelectAll when $description",
      ({ selectedValues, expectedSelectAll }) => {
        const [selectAllValue, updateValue] =
          updateDropdownSelectAll(selectedValues);

        expect(selectAllValue).toBe(expectedSelectAll);
        expect(updateValue).toBe(global.dash_clientside.no_update);
      },
    );
  });

  // Alternative approach using test.each if you prefer more explicit test cases
  describe("edge cases", () => {
    it.each([
      ["option1", false],
      ["option1", "option2", false],
      ["option1", "option2", "option3", true],
      [[], false],
    ])(
      "should return correct select all state for selected values: %p",
      (...selectedValues) => {
        const expectedSelectAll = selectedValues.length === mockOptions.length;
        const [selectAllValue, updateValue] =
          updateDropdownSelectAll(selectedValues);

        expect(selectAllValue).toBe(expectedSelectAll);
        expect(updateValue).toBe(global.dash_clientside.no_update);
      },
    );
  });
});
