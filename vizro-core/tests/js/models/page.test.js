// Mock dash_clientside before importing the module
global.dash_clientside = {
  no_update: "no_update",
  PreventUpdate: "PreventUpdate",
  callback_context: {
    triggered_id: null,
  },
};

// Mock browser APIs
global.btoa = jest.fn();
global.atob = jest.fn();
global.TextEncoder = jest.fn(() => ({
  encode: jest.fn(),
}));
global.TextDecoder = jest.fn(() => ({
  decode: jest.fn(),
}));

// Mock window and history
Object.defineProperty(global, "window", {
  value: {
    location: {
      search: "",
      pathname: "/test-page",
    },
  },
  writable: true,
});

Object.defineProperty(global, "history", {
  value: {
    replaceState: jest.fn(),
  },
  writable: true,
});

global.URLSearchParams = jest.fn(() => ({
  set: jest.fn(),
  toString: jest.fn(() => "param1=value1&param2=value2"),
}));

// Mock window.dash_clientside
global.window = {
  dash_clientside: global.dash_clientside,
};

// Import the page module
require("../../../src/vizro/static/js/models/page.js");

describe("page.js functions", () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    global.dash_clientside.callback_context.triggered_id = null;
    global.window.location.search = "";

    // Reset URLSearchParams mock
    global.URLSearchParams = jest.fn(() => ({
      set: jest.fn(),
      toString: jest.fn(() => "param1=value1&param2=value2"),
    }));
  });

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
    beforeEach(() => {
      // Mock atob and TextDecoder for decoding tests
      global.atob = jest.fn(str => "decoded_" + str);
      global.TextDecoder = jest.fn(() => ({
        decode: jest.fn(bytes => '{"test": "value"}'),
      }));
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

      // Mock console.warn to avoid noise in test output
      global.console = { warn: jest.fn() };

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
    console.log(global.dash_clientside);
    const sync_url_query_params_and_controls =
      global.dash_clientside.page.sync_url_query_params_and_controls;

    test("should handle page opened scenario", () => {
      // Set triggered_id to undefined to simulate page opened
      global.dash_clientside.callback_context.triggered_id = undefined;

      const values_ids = ["value1", "value2", "control1", "control2"];

      const result = sync_url_query_params_and_controls(...values_ids);

      // First element should be null (trigger OPL)
      expect(result[0]).toBe(null);
      // Should return array with length = 1 + number of controls
      expect(result.length).toBe(3); // 1 for trigger + 2 controls
    });

    // test("should handle control changed scenario", () => {
    //   // Set triggered_id to some value to simulate control change
    //   global.dash_clientside.callback_context.triggered_id = "some-control";

    //   const values_ids = ["value1", "value2", "control1", "control2"];

    //   const result = sync_url_query_params_and_controls(...values_ids);

    //   // First element should be no_update (don't trigger OPL)
    //   expect(result[0]).toBe(global.dash_clientside.no_update);
    //   // Should return array with length = 1 + number of controls
    //   expect(result.length).toBe(3); // 1 for trigger + 2 controls
    // });

    // test("should split values and IDs correctly", () => {
    //   global.dash_clientside.callback_context.triggered_id = "test-control";

    //   const values_ids = ["val1", "val2", "val3", "id1", "id2", "id3"];

    //   const result = sync_url_query_params_and_controls(...values_ids);

    //   // Should handle 3 controls (6 total parameters / 2)
    //   expect(result.length).toBe(4); // 1 for trigger + 3 controls
    // });

    // test("should call history.replaceState with correct URL", () => {
    //   global.dash_clientside.callback_context.triggered_id = "test-control";
    //   global.window.location.pathname = "/test-dashboard";

    //   const values_ids = ["value1", "control1"];

    //   sync_url_query_params_and_controls(...values_ids);

    //   expect(global.history.replaceState).toHaveBeenCalledWith(
    //     null,
    //     "",
    //     "/test-dashboard?param1=value1&param2=value2"
    //   );
    // });

    // test("should handle empty values_ids array", () => {
    //   global.dash_clientside.callback_context.triggered_id = undefined;

    //   const result = sync_url_query_params_and_controls();

    //   expect(result).toEqual([null]);
    // });

    // test("should handle odd number of parameters", () => {
    //   global.dash_clientside.callback_context.triggered_id = "test";

    //   // Odd number should still work (though not typical usage)
    //   const values_ids = ["value1", "value2", "control1"];

    //   const result = sync_url_query_params_and_controls(...values_ids);

    //   // Should handle 1.5 -> 1 control (Math.floor behavior)
    //   expect(result.length).toBe(2); // 1 for trigger + 1 control
    // });

    // test("should update URLSearchParams with encoded values", () => {
    //   global.dash_clientside.callback_context.triggered_id = "test-control";

    //   const mockUrlParams = {
    //     set: jest.fn(),
    //     toString: jest.fn(() => "encoded=params"),
    //   };
    //   global.URLSearchParams = jest.fn(() => mockUrlParams);

    //   const values_ids = ["value1", "control1"];

    //   sync_url_query_params_and_controls(...values_ids);

    //   expect(mockUrlParams.set).toHaveBeenCalled();
    //   expect(global.history.replaceState).toHaveBeenCalledWith(
    //     null,
    //     "",
    //     expect.stringContaining("encoded=params")
    //   );
    // });
  });

  //   describe("integration tests", () => {
  //     test("should work with realistic control data", () => {
  //       const sync_url_query_params_and_controls =
  //         global.dash_clientside.page.sync_url_query_params_and_controls;

  //       global.dash_clientside.callback_context.triggered_id = undefined; // Page opened
  //       global.window.location.search = "?vizro_1=b64_encodedValue";

  //       // Simulate realistic control data: 2 control values + 2 control IDs
  //       const controlValues = [["option1", "option2"], 50];
  //       const controlIds = ["dropdown-1", "slider-1"];
  //       const values_ids = [...controlValues, ...controlIds];

  //       const result = sync_url_query_params_and_controls(...values_ids);

  //       expect(result[0]).toBe(null); // Should trigger OPL
  //       expect(result.length).toBe(3); // 1 trigger + 2 controls
  //       expect(Array.isArray(result)).toBe(true);
  //     });

  //     test("should handle control changes properly", () => {
  //       const sync_url_query_params_and_controls =
  //         global.dash_clientside.page.sync_url_query_params_and_controls;

  //       global.dash_clientside.callback_context.triggered_id = "dropdown-1"; // Control changed

  //       const controlValues = [["new_option"], 75];
  //       const controlIds = ["dropdown-1", "slider-1"];
  //       const values_ids = [...controlValues, ...controlIds];

  //       const result = sync_url_query_params_and_controls(...values_ids);

  //       expect(result[0]).toBe(global.dash_clientside.no_update); // Should not trigger OPL
  //       expect(result.length).toBe(3); // 1 trigger + 2 controls
  //     });
  //   });
});
