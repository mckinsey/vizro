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
    test("should return no_update and set guard to false", () => {
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
    test("should return original value", () => {
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
    test("should return original value", () => {
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

describe("replaceTemplateVariables", () => {
  let replaceTemplateVariables;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Get the function from the global object
    replaceTemplateVariables = global.replaceTemplateVariables;
  });

  describe("when text contains no template variables", () => {
    test("should return the original string unchanged", () => {
      expect(replaceTemplateVariables("Text", { key: "value" })).toBe("Text");
    });

    test("should handle empty string", () => {
      expect(replaceTemplateVariables("", { key: "value" })).toBe("");
    });
  });

  describe("when valuesMap does not contain a referenced key", () => {
    test("should leave the template if not key in valuesMap", () => {
      expect(replaceTemplateVariables("Hello {{key}}!", {})).toBe(
        "Hello {{key}}!",
      );
    });
  });

  describe("when keys match template placeholders", () => {
    test("should replace multiple different keys", () => {
      expect(
        replaceTemplateVariables("A={{a}}, B={{b}}, C={{c}}", {
          a: 1,
          b: 2,
          c: 3,
        }),
      ).toBe("A=1, B=2, C=3");
    });

    test("should replace multiple occurrences of the same key", () => {
      expect(
        replaceTemplateVariables("{{key}}-{{key}}-{{key}}", { key: "value" }),
      ).toBe("value-value-value");
    });

    test("should replace adjacent placeholders correctly", () => {
      expect(replaceTemplateVariables("{{a}}{{b}}{{a}}", { a: 1, b: 2 })).toBe(
        "121",
      );
    });

    test("should replace placeholders even if they are nested within other braces", () => {
      expect(
        replaceTemplateVariables("Hello {{{name}}}!", { name: "World" }),
      ).toBe("Hello {World}!");
    });
  });

  describe("when values need to be stringified", () => {
    test("should stringify booleans", () => {
      expect(replaceTemplateVariables("{{key}}", { key: false })).toBe("false");
    });

    test("should stringify null and undefined", () => {
      expect(
        replaceTemplateVariables("null={{a}} undefined={{b}}", {
          a: null,
          b: undefined,
        }),
      ).toBe("null=null undefined=undefined");
    });

    test("should stringify arrays and objects via JSON.stringify(value)", () => {
      expect(replaceTemplateVariables("arr={{arr}}", { arr: [1, 2] })).toBe(
        "arr=[1,2]",
      );
      expect(replaceTemplateVariables("obj={{obj}}", { obj: { a: 1 } })).toBe(
        'obj={"a":1}',
      );
    });
  });

  describe("when placeholders do not match the regex \\{\\{(\\w+)\\}\\}", () => {
    test("should not replace hyphenated keys (not matched by \\w+)", () => {
      expect(
        replaceTemplateVariables("Value: {{key-key}}!", { "key-key": "value" }),
      ).toBe("Value: {{key-key}}!");
    });

    test("should not replace placeholders containing spaces inside braces", () => {
      expect(
        replaceTemplateVariables("Value: {{ key }}!", { key: "value" }),
      ).toBe("Value: {{ key }}!");
    });

    test("should not replace empty keys", () => {
      expect(replaceTemplateVariables("Value: {{}}", { "": "value" })).toBe(
        "Value: {{}}",
      );
    });

    test("should not replace keys containing dots", () => {
      expect(
        replaceTemplateVariables("Value: {{a.b}}", { "a.b": "value" }),
      ).toBe("Value: {{a.b}}");
    });

    test("should leave single braces or malformed templates unchanged", () => {
      expect(replaceTemplateVariables("Hello {name}!", { name: "World" })).toBe(
        "Hello {name}!",
      );
      expect(
        replaceTemplateVariables("Hello {{name}!", { name: "World" }),
      ).toBe("Hello {{name}!");
      expect(
        replaceTemplateVariables("Hello { {name}}!", { name: "World" }),
      ).toBe("Hello { {name}}!");
    });
  });
});

// Ensure structuredClone that's used in the code exists and is observable in tests.
// If Jest runtime already provides structuredClone, we wrap it in a spy.
// Otherwise, we provide a simple JSON-based clone (sufficient for these fixtures).
if (typeof global.structuredClone === "function") {
  global.structuredClone = jest.fn(global.structuredClone);
} else {
  global.structuredClone = jest.fn((obj) => JSON.parse(JSON.stringify(obj)));
}

describe("show_progress_notification", () => {
  let show_progress_notification;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Get the function from the global object
    show_progress_notification =
      global.dash_clientside.action.show_progress_notification;
  });

  test("should hide the existing notification by id and send the updated notification payload via set_props", () => {
    const notificationObject = [
      {
        id: "notif-1",
        message: { props: { children: "Clicked {{n_clicks}} times" } },
      },
    ];

    const actionParameters = ["n_clicks"];
    const actionArguments = 123;

    const result = show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      actionParameters,
      actionArguments,
    );

    expect(result).toBeUndefined();

    // Clears existing notification so it can be shown again
    expect(
      dash_mantine_components.appNotifications.api.hide,
    ).toHaveBeenCalledTimes(1);
    expect(
      dash_mantine_components.appNotifications.api.hide,
    ).toHaveBeenCalledWith("notif-1");

    // Sends updated notifications via Dash set_props
    expect(dash_clientside.set_props).toHaveBeenCalledTimes(1);

    const [targetId, props] = dash_clientside.set_props.mock.calls[0];
    expect(targetId).toBe("vizro-notifications");
    expect(props).toHaveProperty("sendNotifications");

    // Template variables replaced
    expect(props.sendNotifications[0].message.props.children).toBe(
      "Clicked 123 times",
    );

    // Original input must not be mutated
    expect(notificationObject[0].message.props.children).toBe(
      "Clicked {{n_clicks}} times",
    );
  });

  test("should replace multiple template variables using parameter-to-runtime-value mapping", () => {
    const notificationObject = [
      {
        id: "notif-2",
        message: { props: { children: "A={{a}}, B={{b}}" } },
      },
    ];

    show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      ["a", "b"],
      1,
      2,
    );

    // Template variables replaced
    const [, props] = dash_clientside.set_props.mock.calls[0];
    expect(props.sendNotifications[0].message.props.children).toBe("A=1, B=2");
  });

  test("should leave unknown keys", () => {
    const notificationObject = [
      {
        id: "notif-3",
        message: { props: { children: "This is {{unknown}}" } },
      },
    ];

    // No action parameters => values map is empty => {{unknown}} stays {{unknown}""
    show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      [],
    );

    const [, props] = dash_clientside.set_props.mock.calls[0];
    expect(props.sendNotifications[0].message.props.children).toBe(
      "This is {{unknown}}",
    );
  });

  test("should only replace keys matching \\w+ (placeholders remain unchanged)", () => {
    const notificationObject = [
      {
        id: "notif-4",
        message: {
          props: { children: "{{key-key}}, {{ key }}, {{}}, {{a.b}}" },
        },
      },
    ];

    show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      ["key-key", "key", "", "a.b"],
      "value",
      "value",
      "value",
      "value",
    );

    const [, props] = dash_clientside.set_props.mock.calls[0];
    expect(props.sendNotifications[0].message.props.children).toBe(
      "{{key-key}}, {{ key }}, {{}}, {{a.b}}",
    );
  });

  test("should stringify booleans/null/undefined", () => {
    const notificationObject = [
      {
        id: "notif-5",
        message: { props: { children: "{{a}}, {{b}}, {{c}}" } },
      },
    ];

    show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      ["a", "b", "c"],
      false,
      null,
      undefined,
    );

    const [, props] = dash_clientside.set_props.mock.calls[0];
    expect(props.sendNotifications[0].message.props.children).toBe(
      "false, null, undefined",
    );
  });

  test("should stringify arrays and objects via JSON.stringify(value", () => {
    const notificationObject = [
      {
        id: "notif-6",
        message: { props: { children: "arr={{arr}}, obj={{obj}}" } },
      },
    ];

    show_progress_notification(
      "trigger_value_not_used",
      notificationObject,
      ["arr", "obj"],
      [1, 2],
      { a: 1 },
    );

    const [, props] = dash_clientside.set_props.mock.calls[0];
    expect(props.sendNotifications[0].message.props.children).toBe(
      'arr=[1,2], obj={"a":1}',
    );
  });
});
