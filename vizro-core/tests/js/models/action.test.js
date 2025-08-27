/**
 * @jest-environment jsdom
 */

// Mock dash_clientside
global.dash_clientside = {
  no_update: Symbol("no_update"),
  set_props: jest.fn(),
};

// Import the module
require("../../../src/vizro/static/js/models/action.js");

describe("guard_action_chain", () => {
  let guard_action_chain;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Get the function from the global object
    guard_action_chain = window.dash_clientside.action.guard_action_chain;
  });

  describe("when created is true", () => {
    it("should return no_update and set guard to false", () => {
      const value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(value, true, trigger_component_id);

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "test_component_guard_actions_chain",
        { data: false }
      );
      expect(console.debug).toHaveBeenCalledWith(
        "Not running actions chain (guard is True) -> Trigger component: test_component"
      );
    });
  });

  describe("when created is null", () => {
    it("should return original value and log debug message", () => {
      const value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(value, null, trigger_component_id);

      expect(result).toBe(value);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
      expect(console.debug).toHaveBeenCalledWith(
        "Running actions chain (no guard exists) -> Trigger component: test_component"
      );
    });
  });

  describe("when created is false", () => {
    it("should return original value and log debug message", () => {
      const value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(value, false, trigger_component_id);

      expect(result).toBe(value);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
      expect(console.debug).toHaveBeenCalledWith(
        "Running actions chain (guard is False) -> Trigger component: test_component"
      );
    });
  });

  describe("with different value types", () => {
    it("should handle object values correctly", () => {
      const value = { test: "data" };

      const result = guard_action_chain(value, false, "component");

      expect(result).toBe(value);
    });

    it("should handle array values correctly", () => {
      const value = [1, 2, 3];

      const result = guard_action_chain(value, null, "component");

      expect(result).toBe(value);
    });

    it("should handle undefined values correctly", () => {
      const value = undefined;

      const result = guard_action_chain(value, false, "component");

      expect(result).toBe(value);
    });
  });
});
