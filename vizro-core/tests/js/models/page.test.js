global.dash_clientside = {
  set_props: jest.fn(),
  no_update: Symbol("no_update"),
};

// Import the page module
require("../../../src/vizro/static/js/models/page.js");

describe("encodeUrlParams", () => {
  beforeEach(() => {
    // Mock btoa and TextEncoder for encoding tests
    global.btoa = jest.fn((str) => `encoded_${str}`);
    global.TextEncoder = jest.fn(() => ({
      encode: jest.fn((_str) => new Uint8Array([1, 2, 3])), // Mock byte array
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
    global.atob = jest.fn((str) => `decoded_${str}`);
    global.TextDecoder = jest.fn(() => ({
      decode: jest.fn((_bytes) => '{"test": "value"}'),
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
  let sync_url_query_params_and_controls;

  // Build a vizro_controls_store entry with sensible defaults, overridable per test. This mirrors the per-control
  // shape produced in Dashboard._make_page_layout (vizro_controls_store).
  const storeEntry = (overrides = {}) => ({
    currentValue: null,
    originalValue: null,
    pageId: "page-1",
    selectorId: null,
    showInURL: false,
    crossPageTarget: false,
    ...overrides,
  });

  beforeEach(() => {
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
              `${encodeURIComponent(key)}=${encodeURIComponent(value)}`,
          )
          .join("&");
      }),
      entries: jest.fn(() => mockUrlParams.entries()),
    }));

    // encodeUrlParams always runs, so btoa/TextEncoder must be available. Individual tests can override atob/JSON.parse
    // to decode specific URL params.
    global.btoa = jest.fn((str) => `enc_${str}`);
    global.TextEncoder = jest.fn(() => ({
      encode: jest.fn(() => new Uint8Array([1, 2, 3])),
    }));
    global.atob = jest.fn((str) => str);
    global.TextDecoder = jest.fn(() => ({ decode: jest.fn(() => '"decoded"') }));

    // Setup history mock
    if (!global.window.history) {
      global.window.history = { replaceState: () => {} };
    }
    if (!global.history) {
      global.history = global.window.history;
    }

    replaceStateSpy = jest
      .spyOn(global.window.history, "replaceState")
      .mockImplementation(() => {});

    global.history.replaceState = global.window.history.replaceState;

    // Get the function from the global object
    sync_url_query_params_and_controls =
      global.dash_clientside.page.sync_url_query_params_and_controls;
  });

  describe("Page opened scenarios (opl_triggered = undefined)", () => {
    const opl_triggered = undefined;

    // Two controls on the current page. control-1 is a cross-page sync target; control-2 is a regular control.
    const values_ids = [
      "selector-value-1", // selector values (current mounted values)
      "selector-value-2",
      "control-id-1", // control IDs
      "control-id-2",
      "selector-id-1", // selector IDs
      "selector-id-2",
    ];

    test("restores crossPageTarget controls from the store, and not other controls", () => {
      const store = {
        "control-id-1": storeEntry({
          currentValue: "synced-value",
          selectorId: "selector-id-1",
          crossPageTarget: true,
        }),
        "control-id-2": storeEntry({
          currentValue: "stored-but-ignored",
          selectorId: "selector-id-2",
          crossPageTarget: false,
        }),
      };

      const result = sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
        store,
      );

      // control-1 (crossPageTarget) is restored from the store's currentValue.
      expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
        "selector-id-1",
        { value: "synced-value" },
      );
      expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
        "selector-id-1_guard_actions_chain",
        { data: true },
      );
      // control-2 (not a crossPageTarget) is NOT restored from the store.
      expect(global.dash_clientside.set_props).not.toHaveBeenCalledWith(
        "selector-id-2",
        { value: expect.anything() },
      );
      // Page open triggers the OPL.
      expect(result).toBe(null);
    });

    test("URL param takes precedence and is applied even to a non-crossPageTarget control", () => {
      const store = {
        "control-id-1": storeEntry({
          currentValue: "store-value",
          selectorId: "selector-id-1",
          crossPageTarget: false, // not restored from the store...
          showInURL: true,
        }),
        "control-id-2": storeEntry({
          selectorId: "selector-id-2",
          crossPageTarget: false,
        }),
      };

      // ...but a URL param for control-1 is applied on page open (drill-through / bookmark).
      mockUrlParams.set("control-id-1", "b64_whatever");
      global.atob = jest.fn().mockReturnValue('"url-value"');
      jest.spyOn(JSON, "parse").mockReturnValue("url-value");

      const result = sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
        store,
      );

      // URL value is applied to the selector...
      expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
        "selector-id-1",
        { value: "url-value" },
      );
      // ...and written back into the store, which is persisted.
      expect(store["control-id-1"].currentValue).toBe("url-value");
      expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
        "vizro_controls_store",
        { data: store },
      );
      expect(result).toBe(null);
    });

    test("encodes show_in_url controls into the URL on page open", () => {
      const store = {
        "control-id-1": storeEntry({
          currentValue: "X",
          selectorId: "selector-id-1",
          crossPageTarget: true,
          showInURL: true,
        }),
        "control-id-2": storeEntry({
          selectorId: "selector-id-2",
          showInURL: false,
        }),
      };

      sync_url_query_params_and_controls(opl_triggered, ...values_ids, store);

      const finalUrl = replaceStateSpy.mock.calls[0][2];
      // show_in_url control is written into the URL; the other is not.
      expect(finalUrl).toContain("control-id-1=");
      expect(finalUrl).not.toContain("control-id-2=");
    });

    test("does nothing to selectors when no control is a crossPageTarget and there are no URL params", () => {
      const store = {
        "control-id-1": storeEntry({ selectorId: "selector-id-1" }),
        "control-id-2": storeEntry({ selectorId: "selector-id-2" }),
      };

      const result = sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
        store,
      );

      // No selector is restored (nothing to restore) and the store is not rewritten (no URL params).
      expect(global.dash_clientside.set_props).not.toHaveBeenCalled();
      expect(result).toBe(null);
    });
  });

  describe("Control changed scenarios (opl_triggered = null)", () => {
    const opl_triggered = null;

    test("tracks the changed value into the store, persists it, and does not trigger OPL", () => {
      const store = {
        "control-id-1": storeEntry({
          currentValue: "old-value",
          selectorId: "selector-id-1",
        }),
      };

      const values_ids = [
        "new-value", // new selector value
        "control-id-1", // control ID
        "selector-id-1", // selector ID
      ];

      const result = sync_url_query_params_and_controls(
        opl_triggered,
        ...values_ids,
        store,
      );

      // currentValue is refreshed from the selector value and the store is persisted.
      expect(store["control-id-1"].currentValue).toBe("new-value");
      expect(global.dash_clientside.set_props).toHaveBeenCalledWith(
        "vizro_controls_store",
        { data: store },
      );
      // A control change must not re-set the selector value...
      expect(global.dash_clientside.set_props).not.toHaveBeenCalledWith(
        "selector-id-1",
        { value: expect.anything() },
      );
      // ...and must not trigger the OPL (the control's own action chain handles the refresh).
      expect(result).toBe(global.dash_clientside.no_update);
    });

    test("writes only show_in_url controls into the URL on change", () => {
      const store = {
        "control-id-1": storeEntry({
          currentValue: "old-1",
          selectorId: "selector-id-1",
          showInURL: true,
        }),
        "control-id-2": storeEntry({
          currentValue: "old-2",
          selectorId: "selector-id-2",
          showInURL: false,
        }),
      };

      const values_ids = [
        "new-1", // selector values - only the first changed in practice
        "new-2",
        "control-id-1", // control IDs
        "control-id-2",
        "selector-id-1", // selector IDs
        "selector-id-2",
      ];

      sync_url_query_params_and_controls(opl_triggered, ...values_ids, store);

      const finalUrl = replaceStateSpy.mock.calls[0][2];
      // Only the show_in_url control is mirrored into the URL.
      expect(finalUrl).toContain("control-id-1=");
      expect(finalUrl).not.toContain("control-id-2=");
    });
  });
});

describe("reset_controls", () => {
  let reset_controls;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    console.debug = jest.fn();

    // Get the function from the global object
    reset_controls = global.dash_clientside.page.reset_controls;
  });

  describe("when there are controls on the current page", () => {
    it("should return [null, ...originalValues, ...guards] for that page", () => {
      const vizroControlsStore = {
        controlA: { originalValue: "A", pageId: "page-1" },
        controlB: { originalValue: "B", pageId: "page-1" },
        controlC: { originalValue: "C", pageId: "page-2" },
      };

      const result = reset_controls(null, vizroControlsStore, "page-1");

      expect(console.debug).toHaveBeenCalledWith(
        "Reset controls on page:",
        "page-1",
      );

      // Only controls from page-1 are included.
      // Then guards: `true` for each of the page controls.
      expect(result).toEqual([null, "A", "B", true, true]);
    });

    it("should keep the order of values aligned to vizroControlsStore", () => {
      // Intentionally define keys in a "weird" order.
      const vizroControlsStore = {
        second: { originalValue: "2nd", pageId: "page-order" },
        first: { originalValue: "1st", pageId: "page-order" },
        third_other_page: { originalValue: "X", pageId: "other" },
        third: { originalValue: "3rd", pageId: "page-order" },
      };

      const result = reset_controls(null, vizroControlsStore, "page-order");

      expect(result).toEqual([null, "2nd", "1st", "3rd", true, true, true]);
    });
  });

  // In practice, this cannot happen as this client-side callback is only defined
  // when there's at least one control on the page. But we test it for robustness.
  describe("when there are no controls on the current page", () => {
    it("should return [null] (still triggers the OPL)", () => {
      const vizroControlsStore = {
        controlA: { originalValue: "A", pageId: "page-2" },
        controlB: { originalValue: "B", pageId: "page-3" },
      };

      const result = reset_controls(null, vizroControlsStore, "page-1");

      expect(result).toEqual([null]);
    });

    it("should return [null] when vizroControlsStore is empty", () => {
      const result = reset_controls(null, {}, "page-empty");

      expect(result).toEqual([null]);
    });
  });
});
