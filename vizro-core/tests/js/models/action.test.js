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
    guard_action_chain = global.dash_clientside.action.guard_action_chain;
  });

  describe("when guard_data is true", () => {
    it("should return no_update and set guard to false", () => {
      const trigger_value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(
        trigger_value,
        true,
        trigger_component_id,
      );

      expect(result).toBe(dash_clientside.no_update);
      expect(dash_clientside.set_props).toHaveBeenCalledWith(
        "test_component_guard_actions_chain",
        { data: false },
      );
    });
  });

  describe("when created is null", () => {
    it("should return original value", () => {
      const trigger_value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(
        trigger_value,
        null,
        trigger_component_id,
      );

      expect(result).toBe(trigger_value);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });
  });

  describe("when created is false", () => {
    it("should return original value", () => {
      const trigger_value = "test_value";
      const trigger_component_id = "test_component";

      const result = guard_action_chain(
        trigger_value,
        false,
        trigger_component_id,
      );

      expect(result).toBe(trigger_value);
      expect(dash_clientside.set_props).not.toHaveBeenCalled();
    });
  });
});
