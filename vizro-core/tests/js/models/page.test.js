const mockSearchParams = new Map([
  ["vizro_1", "b64_encodedValue"],
  ["foo", "raw_value"],
  ["vizro_2", "b64_anotherEncoded"],
]);

global.TextEncoder = jest.fn(() => ({
  encode: jest.fn(),
}));
global.TextDecoder = jest.fn(() => ({
  decode: jest.fn(),
}));

global.URLSearchParams = jest.fn(() => ({
  set: jest.fn((key, value) => mockSearchParams.set(key, value)),
  toString: jest.fn(() => "controlId1=controlVal1&controlId2=controlVal2"),
  entries: jest.fn(() => mockSearchParams.entries()),
  get: jest.fn((key) => mockSearchParams.get(key)),
  has: jest.fn((key) => mockSearchParams.has(key)),
  forEach: jest.fn((callback) => mockSearchParams.forEach(callback)),
}));

global.dash_clientside = {
  set_props: jest.fn(),
  no_update: "no_update",
  PreventUpdate: "PreventUpdate",
  callback_context: {
    triggered_id: undefined,
  },
};

// Mock window.dash_clientside
global.window = {
  location: {
    search:
      "?vizro_1=b64_encodedValue&foo=raw_value&vizro_2=b64_anotherEncoded",
    pathname: "/",
  },
  dash_clientside: global.dash_clientside,
};

// Import the page module
require("../../../src/vizro/static/js/models/page.js");

describe("page.js functions", () => {
  describe("encodeUrlParams", () => {
    beforeEach(() => {
      // Mock btoa and TextEncoder for encoding tests
      global.btoa = jest.fn((str) => "encoded_" + str);
      global.TextEncoder = jest.fn(() => ({
        encode: jest.fn((str) => new Uint8Array([1, 2, 3])), // Mock byte array
      }));
    });

    test("should encode specified keys only", () => {
      const decodedMap = new Map([
        ["vizro_1", 123],
        ["foo", ["a", "b"]],
        ["bar", "test"],
      ]);
      const applyOnKeys = ["vizro_1", "foo"];

      const result = encodeUrlParams(decodedMap, applyOnKeys);

      expect(result.size).toBe(2);
      expect(result.has("vizro_1")).toBe(true);
      expect(result.has("foo")).toBe(true);
      expect(result.has("bar")).toBe(false);
    });

    test("should add b64_ prefix to encoded values", () => {
      const decodedMap = new Map([["key1", "value1"]]);
      const applyOnKeys = ["key1"];

      global.btoa.mockReturnValue("encodedValue");

      const result = encodeUrlParams(decodedMap, applyOnKeys);

      expect(result.get("key1")).toBe("b64_encodedValue");
    });

    test("should handle empty map", () => {
      const decodedMap = new Map();
      const applyOnKeys = ["key1"];

      const result = encodeUrlParams(decodedMap, applyOnKeys);

      expect(result.size).toBe(0);
    });

    test("should handle empty applyOnKeys array", () => {
      const decodedMap = new Map([["key1", "value1"]]);
      const applyOnKeys = [];

      const result = encodeUrlParams(decodedMap, applyOnKeys);

      expect(result.size).toBe(0);
    });
  });

  describe("decodeUrlParams", () => {
    let originalJSON;
    let originalConsole;

    beforeEach(() => {
      // Save original JSON and console functions
      originalJSON = global.JSON;
      originalConsole = global.console;

      // Mock atob and TextDecoder for decoding tests
      global.atob = jest.fn((str) => "decoded_" + str);
      global.TextDecoder = jest.fn(() => ({
        decode: jest.fn((bytes) => '{"test": "value"}'),
      }));
    });

    afterEach(() => {
      // Return original functions after each test
      global.JSON = originalJSON;
      global.console = originalConsole;
    });

    test("should decode b64_ prefixed values for specified keys", () => {
      const encodedMap = new Map([
        ["vizro_1", "b64_encodedValue"],
        ["foo", "raw_value"],
        ["vizro_2", "b64_anotherEncoded"],
      ]);
      const applyOnKeys = ["vizro_1", "vizro_2"];

      global.JSON = {
        parse: jest.fn((str) => ({ decoded: "data" })),
      };

      const result = decodeUrlParams(encodedMap, applyOnKeys);

      expect(result.size).toBe(2);
      expect(result.has("vizro_1")).toBe(true);
      expect(result.has("vizro_2")).toBe(true);
      expect(result.has("foo")).toBe(false);
    });

    test("should not decode values without b64_ prefix", () => {
      const encodedMap = new Map([
        ["key1", "raw_value"],
        ["key2", "another_raw_value"],
      ]);
      const applyOnKeys = ["key1", "key2"];

      const result = decodeUrlParams(encodedMap, applyOnKeys);

      expect(result.size).toBe(0);
    });

    test("should handle decoding errors gracefully", () => {
      const encodedMap = new Map([["key1", "b64_invalidEncoding"]]);
      const applyOnKeys = ["key1"];

      global.console.warn = jest.fn();

      // Make atob throw an error
      global.atob.mockImplementation(() => {
        throw new Error("Invalid encoding");
      });

      const result = decodeUrlParams(encodedMap, applyOnKeys);

      expect(result.size).toBe(0);
      expect(global.console.warn).toHaveBeenCalled();
    });

    test("should handle empty map", () => {
      const encodedMap = new Map();
      const applyOnKeys = ["key1"];

      const result = decodeUrlParams(encodedMap, applyOnKeys);

      expect(result.size).toBe(0);
    });
  });

  describe("sync_url_query_params_and_controls", () => {
    let replaceStateSpy;

    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id = undefined;

      if (!global.window.history) {
        global.window.history = { replaceState: function () {} };
      }
      if (!global.history) {
        global.history = global.window.history;
      }

      replaceStateSpy = jest
        .spyOn(global.window.history, "replaceState")
        .mockImplementation(() => {});

      global.history.replaceState = global.window.history.replaceState;
    });

    afterEach(() => {
      // Reset spy after each test
      if (replaceStateSpy) {
        replaceStateSpy.mockRestore();
      }
    });

    test("should trigger on page load after the function (return null)", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          opl_triggered,
        );

      // Returned element should be null (trigger OPL)
      expect(result).toBe(null);
    });

    test("should handle control changed scenario", () => {
      // If opl_triggered is null, it means the page is NOT just opened
      // but the control has changed
      const opl_triggered = null;

      const values_ids = ["controlVal1", "controlId1", "selectorId1"];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          opl_triggered,
        );

      // Returned element should be dash_clientside.no_update (do NOT trigger OPL)
      expect(result).toBe(global.dash_clientside.no_update);
    });

    test("should split control values and control and selector IDs correctly", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      const values_ids = [
        "controlVal1",
        "controlVal2",
        "controlVal3",
        "controlId1",
        "controlId2",
        "controlId3",
        "selectorId1",
        "selectorId2",
        "selectorId3",
      ];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          opl_triggered,
          ...values_ids,
        );

      // Returned element should be null (trigger OPL)
      expect(result).toBe(null);
    });

    test("should call history.replaceState with correct URL", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      // These values_ids will NOT be used in the expect statement below. Mocked urlParams.toString() is used instead.
      const values_ids = [
        "controlVal1",
        "controlVal2",
        "controlId1",
        "controlId2",
        "selectorId1",
        "selectorId2",
      ];

      global.dash_clientside.page.sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
      );

      // values_ids are not used in the expect statement below. Mocked urlParams.toString() is used instead.
      expect(replaceStateSpy).toHaveBeenCalledWith(
        null,
        "",
        "/?controlId1=controlVal1&controlId2=controlVal2",
      );
    });

    test("should handle empty values_ids array", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          opl_triggered,
        );

      expect(result).toEqual(null);
    });

    test("should raise an exception if a number of input parameters is not divisible by three", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      const values_ids = [
        "value1",
        "value2",
        "control1",
        "control2",
        "selector1",
      ];

      expect(() => {
        global.dash_clientside.page.sync_url_query_params_and_controls(
          opl_triggered,
          ...values_ids,
        );
      }).toThrow(
        `Invalid number of input parameters: received 5.
Expected format: [selector-1-value, selector-N-value, ..., control-1-id, control-N-id, ..., selector-1-id, selector-N-id, ...]
Received input: ["value1","value2","control1","control2","selector1"]`,
      );
    });

    test("should update URLSearchParams with encoded values", () => {
      // If opl_triggered is undefined, it means the page is opened
      const opl_triggered = undefined;

      const mockUrlParams = {
        set: jest.fn(),
        toString: jest.fn(() => "encoded=params"),
      };

      const values_ids = [
        "controlVal1",
        "controlVal2",
        "controlId1",
        "controlId2",
        "selectorId1",
        "selectorId2",
      ];

      global.dash_clientside.page.sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
      );

      expect(replaceStateSpy).toHaveBeenCalledWith(
        null,
        "",
        "/?controlId1=controlVal1&controlId2=controlVal2",
      );
    });
  });
});
