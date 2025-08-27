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
  get: jest.fn(key => mockSearchParams.get(key)),
  has: jest.fn(key => mockSearchParams.has(key)),
  forEach: jest.fn(callback => mockSearchParams.forEach(callback)),
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

      // Mock JSON.parse using jest.spyOn to avoid circular reference
      jest.spyOn(JSON, "parse").mockReturnValue({ decoded: "data" });

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
    let mockUrlParams;

    beforeEach(() => {
      // Reset all mocks
      jest.clearAllMocks();
      jest.restoreAllMocks();
      global.dash_clientside.set_props.mockClear();

      // Create fresh mock for URLSearchParams
      mockUrlParams = new Map();
      global.URLSearchParams = jest.fn(() => ({
        set: jest.fn((key, value) => mockUrlParams.set(key, value)),
        toString: jest.fn(() => {
          return Array.from(mockUrlParams.entries())
            .map(
              ([key, value]) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
            )
            .join("&");
        }),
        entries: jest.fn(() => mockUrlParams.entries()),
        get: jest.fn(key => mockUrlParams.get(key)),
        has: jest.fn(key => mockUrlParams.has(key)),
        forEach: jest.fn(callback => mockUrlParams.forEach(callback)),
      }));

      // Setup history mock
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
      if (replaceStateSpy) {
        replaceStateSpy.mockRestore();
      }
    });

    describe("Page opened scenarios (opl_triggered = undefined)", () => {
      const opl_triggered = undefined;

      test("should decode URL params and call setProps for matching control IDs", () => {
        // Mock the decoding to return specific values
        global.atob = jest
          .fn()
          .mockReturnValueOnce('{"value":"value1"}') // for control-1
          .mockReturnValueOnce('{"value":"value2"}'); // for control-2

        // Mock JSON.parse using jest.spyOn to avoid circular reference
        jest
          .spyOn(JSON, "parse")
          .mockReturnValueOnce({ value: "value1" }) // for control-1
          .mockReturnValueOnce({ value: "value2" }); // for control-2

        // Setup encoded URL params that match control IDs
        mockUrlParams.set("control-1", "b64_InZhbHVlMSI"); // "value1" encoded
        mockUrlParams.set("control-2", "b64_InZhbHVlMiI"); // "value2" encoded

        const values_ids = [
          "initial-1",
          "initial-2", // selector values
          "control-1",
          "control-2", // control IDs
          "selector-1",
          "selector-2", // selector IDs
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        // Should trigger OPL
        expect(result).toBe(null);

        // Should call setProps for both controls
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-1_guard_actions_chain",
          { data: true }
        );
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-1",
          { value: { value: "value1" } }
        );
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-2_guard_actions_chain",
          { data: true }
        );
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-2",
          { value: { value: "value2" } }
        );
      });

      test("should handle partially defined URL params", () => {
        // Mock the decoding to return specific value for control-1 only
        global.atob = jest.fn().mockReturnValueOnce('{"value":"value1"}');
        jest.spyOn(JSON, "parse").mockReturnValueOnce({ value: "value1" });

        // Only one control is defined in URL
        mockUrlParams.set("control-1", "b64_InZhbHVlMSI"); // "value1" encoded

        const values_ids = [
          "initial-1",
          "initial-2", // selector values
          "control-1",
          "control-2", // control IDs
          "selector-1",
          "selector-2", // selector IDs
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        expect(result).toBe(null);

        // Should only call setProps for control-1
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-1_guard_actions_chain",
          { data: true }
        );
        expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
          "selector-1",
          { value: { value: "value1" } }
        );

        // Should NOT call setProps for control-2
        expect(global.dash_clientside.set_props).not.toHaveBeenCalledWith(
          "selector-2_guard_actions_chain",
          { data: true }
        );
        expect(global.dash_clientside.set_props).not.toHaveBeenCalledWith(
          "selector-2",
          { value: expect.anything() }
        );
      });

      test("should not call setProps when URL params are empty", () => {
        // No URL params - mockUrlParams is already cleared in beforeEach
        const values_ids = [
          "initial-1",
          "initial-2",
          "control-1",
          "control-2",
          "selector-1",
          "selector-2",
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        expect(result).toBe(null);
        expect(global.dash_clientside.set_props).not.toHaveBeenCalled();
      });

      test("should not call setProps when URL param IDs don't match control IDs", () => {
        // URL contains params that don't match any control IDs
        mockUrlParams.set("different-control", "b64_InZhbHVlMSI");
        mockUrlParams.set("another-control", "b64_InZhbHVlMiI");

        const values_ids = [
          "initial-1",
          "initial-2",
          "control-1",
          "control-2",
          "selector-1",
          "selector-2",
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        expect(result).toBe(null);
        expect(global.dash_clientside.set_props).not.toHaveBeenCalled();
      });
    });

    describe("Control changed scenarios (opl_triggered = null)", () => {
      const opl_triggered = null;

      test("should update URL with single control change and not trigger OPL", () => {
        // Save original TextEncoder before mocking
        const OriginalTextEncoder = TextEncoder;

        // Mock encoding for the new value
        global.btoa = jest.fn().mockReturnValue("bmV3LXZhbHVl"); // "new-value" encoded
        global.TextEncoder = jest.fn(() => ({
          encode: jest
            .fn()
            .mockReturnValue(
              new OriginalTextEncoder().encode(JSON.stringify("new-value"))
            ),
        }));

        // URL initially contains one encoded control
        mockUrlParams.set("control-1", "b64_SW5pdGlhbFZhbHVl"); // old value

        const values_ids = [
          "new-value", // new selector value
          "control-1", // control ID
          "selector-1", // selector ID
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        expect(result).toBe(global.dash_clientside.no_update);
        expect(global.dash_clientside.set_props).not.toHaveBeenCalled();

        // Should update URL with new encoded value
        expect(replaceStateSpy).toHaveBeenCalledWith(
          null,
          "",
          expect.stringContaining("control-1=b64_bmV3LXZhbHVl") // "new-value" encoded
        );
      });

      test("should update URL with multiple controls, changing only one", () => {
        // Save original TextEncoder before mocking
        const OriginalTextEncoder = TextEncoder;

        // Mock encoding for both values
        global.btoa = jest
          .fn()
          .mockReturnValueOnce("bmV3LXZhbHVl") // "new-value" encoded
          .mockReturnValueOnce("dW5jaGFuZ2VkLXZhbHVl"); // "unchanged-value" encoded

        global.TextEncoder = jest.fn(() => ({
          encode: jest
            .fn()
            .mockReturnValueOnce(
              new OriginalTextEncoder().encode(JSON.stringify("new-value"))
            )
            .mockReturnValueOnce(
              new OriginalTextEncoder().encode(
                JSON.stringify("unchanged-value")
              )
            ),
        }));

        // URL initially contains two encoded controls
        mockUrlParams.set("control-1", "b64_SW5pdGlhbFZhbHVlMQ"); // old value1
        mockUrlParams.set("control-2", "b64_SW5pdGlhbFZhbHVlMg"); // old value2

        const values_ids = [
          "new-value",
          "unchanged-value", // selector values - only first one changed
          "control-1",
          "control-2", // control IDs
          "selector-1",
          "selector-2", // selector IDs
        ];

        const result =
          global.dash_clientside.page.sync_url_query_params_and_controls(
            opl_triggered,
            ...values_ids
          );

        expect(result).toBe(global.dash_clientside.no_update);
        expect(global.dash_clientside.set_props).not.toHaveBeenCalled();

        // Should update URL with new values for both controls
        const finalUrl = replaceStateSpy.mock.calls[0][2];
        expect(finalUrl).toContain("control-1=b64_bmV3LXZhbHVl"); // "new-value" encoded
        expect(finalUrl).toContain("control-2=b64_dW5jaGFuZ2VkLXZhbHVl"); // "unchanged-value" encoded
      });
    });
  });
});
