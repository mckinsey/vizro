/**
 * @jest-environment jsdom
 */

// Mock dash_clientside
global.dash_clientside = {
  no_update: Symbol("no_update"),
  set_props: jest.fn(),
};

// Mock dash_mantine_components notifications API used by show_progress_notification
global.dash_mantine_components = {
  appNotifications: {
    api: {
      hide: jest.fn(),
    },
  },
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


const { replaceTemplateVariables } = require("../../../src/vizro/static/js/models/action.js");

describe("replaceTemplateVariables", () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    console.debug = jest.fn();
  });

  describe("when text contains no template variables", () => {
    it("should return the original string unchanged", () => {
      expect(replaceTemplateVariables("Text", { key: "value" })).toBe("Text");
    });

    it("should handle empty string", () => {
      expect(replaceTemplateVariables("", { key: "value" })).toBe("");
    });
  });

  describe("when valuesMap does not contain a referenced key", () => {
    it("should leave the template if not key in valuesMap", () => {
      expect(replaceTemplateVariables("Hello {{key}}!", {})).toBe("Hello {{key}}!");
    });
  });

  describe("when keys match template placeholders", () => {
    it("should replace multiple different keys", () => {
      expect(
        replaceTemplateVariables("A={{a}}, B={{b}}, C={{c}}", { a: 1, b: 2, c: 3 }),
      ).toBe("A=1, B=2, C=3");
    });

    it("should replace multiple occurrences of the same key", () => {
      expect(replaceTemplateVariables("{{key}}-{{key}}-{{key}}", { key: "value" })).toBe("value-value-value");
    });

    it("should replace adjacent placeholders correctly", () => {
      expect(replaceTemplateVariables("{{a}}{{b}}{{a}}", { a: 1, b: 2 })).toBe("121");
    });

    it("should replace placeholders even if they are nested within other braces", () => {
      expect(replaceTemplateVariables("Hello {{{name}}}!", { name: "World" })).toBe("Hello {World}!");
    });
  });

  describe("when values need to be stringified", () => {
    it("should stringify booleans", () => {
      expect(replaceTemplateVariables("{{key}}", { key: false })).toBe(
        "false",
      );
    });

    it("should stringify null and undefined", () => {
      expect(replaceTemplateVariables("null={{a}} undefined={{b}}", { a: null, b: undefined })).toBe(
        "null=null undefined=undefined"
      );
    });

    it("should stringify arrays and objects via JSON.stringify(value)", () => {
      expect(replaceTemplateVariables("arr={{arr}}", { arr: [1, 2] })).toBe("arr=[1,2]");
      expect(replaceTemplateVariables("obj={{obj}}", { obj: { a: 1 } })).toBe(
        "obj={\"a\":1}",
      );
    });
  });

  describe("when placeholders do not match the regex \\{\\{(\\w+)\\}\\}", () => {
    it("should not replace hyphenated keys (not matched by \\w+)", () => {
      expect(
        replaceTemplateVariables("Hello {{key-key}}!", { "key-key": "value" }),
      ).toBe("Hello {{key-key}}!");
    });

    it("should not replace placeholders containing spaces inside braces", () => {
      expect(replaceTemplateVariables("Hello {{ key }}!", { key: "World" })).toBe(
        "Hello {{ key }}!",
      );
    });

    it("should not replace empty keys", () => {
      expect(replaceTemplateVariables("Value: {{}}", { "": "X" })).toBe("Value: {{}}");
    });

    it("should not replace keys containing dots", () => {
      expect(replaceTemplateVariables("Value: {{a.b}}", { "a.b": "X" })).toBe("Value: {{a.b}}");
    });

    it("should leave single braces or malformed templates unchanged", () => {
      expect(replaceTemplateVariables("Hello {name}!", { name: "World" })).toBe("Hello {name}!");
      expect(replaceTemplateVariables("Hello {{name}!", { name: "World" })).toBe("Hello {{name}!");
      expect(replaceTemplateVariables("Hello { {name}}!", { name: "World" })).toBe(
        "Hello { {name}}!",
      );
    });
  });
});
