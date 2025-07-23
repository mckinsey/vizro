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
  toString: jest.fn(() => "param1=value1&param2=value2"),
  entries: jest.fn(() => mockSearchParams.entries()),
  get: jest.fn(key => mockSearchParams.get(key)),
  has: jest.fn(key => mockSearchParams.has(key)),
  forEach: jest.fn(callback => mockSearchParams.forEach(callback)),
}));

global.dash_clientside = {
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
      global.btoa = jest.fn(str => "encoded_" + str);
      global.TextEncoder = jest.fn(() => ({
        encode: jest.fn(str => new Uint8Array([1, 2, 3])), // Mock byte array
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
      global.atob = jest.fn(str => "decoded_" + str);
      global.TextDecoder = jest.fn(() => ({
        decode: jest.fn(bytes => '{"test": "value"}'),
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
        parse: jest.fn(str => ({ decoded: "data" })),
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
      // Resetujemo spy nakon svakog testa
      if (replaceStateSpy) {
        replaceStateSpy.mockRestore();
      }
    });

    test("should handle page opened scenario", () => {
      const values_ids = ["value1", "value2", "control1", "control2"];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          ...values_ids
        );

      // First element should be null (trigger OPL)
      expect(result[0]).toBe(null);
      // Should return array with length = 1 + number of controls
      expect(result.length).toBe(3); // 1 for trigger + 2 controls
    });

    test("should handle control changed scenario", () => {
      // Set triggered_id to some value to simulate control change
      global.dash_clientside.callback_context.triggered_id = "some-control";

      const values_ids = ["value1", "value2", "control1", "control2"];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          ...values_ids
        );

      // First element should be no_update (don't trigger OPL)
      expect(result[0]).toBe(global.dash_clientside.no_update);
      // Should return array with length = 1 + number of controls
      expect(result.length).toBe(3); // 1 for trigger + 2 controls
    });

    test("should split values and IDs correctly", () => {
      global.dash_clientside.callback_context.triggered_id = "test-control";

      const values_ids = ["val1", "val2", "val3", "id1", "id2", "id3"];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          ...values_ids
        );

      // Should handle 3 controls (6 total parameters / 2)
      expect(result.length).toBe(4); // 1 for trigger + 3 controls
    });

    test("should call history.replaceState with correct URL", () => {
      global.dash_clientside.callback_context.triggered_id = "test-control";

      const values_ids = ["value1", "control1"];

      global.dash_clientside.page.sync_url_query_params_and_controls(
        ...values_ids
      );

      expect(replaceStateSpy).toHaveBeenCalledWith(
        null,
        "",
        "/?param1=value1&param2=value2"
      );
    });

    test("should handle empty values_ids array", () => {
      global.dash_clientside.callback_context.triggered_id = undefined;

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls();

      expect(result).toEqual([null]);
    });

    test("should handle odd number of parameters", () => {
      global.dash_clientside.callback_context.triggered_id = "test";

      const values_ids = ["value1", "value2", "control1"];

      const result =
        global.dash_clientside.page.sync_url_query_params_and_controls(
          ...values_ids
        );

      expect(result.length).toBe(3);
    });

    test("should update URLSearchParams with encoded values", () => {
      global.dash_clientside.callback_context.triggered_id = "test-control";

      const mockUrlParams = {
        set: jest.fn(),
        toString: jest.fn(() => "encoded=params"),
      };
      global.URLSearchParams = jest.fn(() => mockUrlParams);

      const values_ids = ["value1", "control1"];

      global.dash_clientside.page.sync_url_query_params_and_controls(
        ...values_ids
      );

      expect(mockUrlParams.set).toHaveBeenCalled();
      expect(replaceStateSpy).toHaveBeenCalledWith(
        null,
        "",
        "/?encoded=params"
      );
    });
  });
});
