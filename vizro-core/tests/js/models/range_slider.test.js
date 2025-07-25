// Mock dash_clientside before importing the module
global.dash_clientside = {
  no_update: "no_update",
  PreventUpdate: "PreventUpdate",
  callback_context: {
    triggered_id: null,
  },
};

// Import the range slider module
require("../../../src/vizro/static/js/models/range_slider.js");

describe("update_range_slider_values", () => {
  const update_range_slider_values =
    global.dash_clientside.range_slider.update_range_slider_values;
  const slider_component_id = "test-range-slider";

  beforeEach(() => {
    // Reset callback context before each test
    global.dash_clientside.callback_context.triggered_id = null;
  });

  describe("slider component triggered", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id =
        slider_component_id;
    });

    test("should return slider values when slider component is triggered", () => {
      const slider_value = [10, 80];
      const start_value = 5;
      const end_value = 90;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        global.dash_clientside.no_update,
        10, // slider_value[0]
        80, // slider_value[1]
      ]);
    });

    test("should handle slider with minimum range", () => {
      const slider_value = [0, 1];
      const start_value = 10;
      const end_value = 20;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([global.dash_clientside.no_update, 0, 1]);
    });

    test("should handle slider with maximum range", () => {
      const slider_value = [0, 100];
      const start_value = 25;
      const end_value = 75;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([global.dash_clientside.no_update, 0, 100]);
    });

    test("should handle slider with same start and end values", () => {
      const slider_value = [50, 50];
      const start_value = 10;
      const end_value = 90;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([global.dash_clientside.no_update, 50, 50]);
    });

    test("should handle negative slider values", () => {
      const slider_value = [-50, -10];
      const start_value = 0;
      const end_value = 100;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([global.dash_clientside.no_update, -50, -10]);
    });

    test("should handle decimal slider values", () => {
      const slider_value = [1.5, 98.7];
      const start_value = 0;
      const end_value = 100;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([global.dash_clientside.no_update, 1.5, 98.7]);
    });
  });

  describe("text form component triggered", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id =
        "some-other-component";
    });

    test("should return text values when text form component is triggered", () => {
      const slider_value = [10, 80];
      const start_value = 20;
      const end_value = 70;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        [20, 70], // [start_value, end_value]
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle valid text values with decimals", () => {
      const slider_value = [0, 100];
      const start_value = 15.5;
      const end_value = 85.2;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        [15.5, 85.2],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle valid text values with zero", () => {
      const slider_value = [10, 90];
      const start_value = 0;
      const end_value = 100;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        [0, 100],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle valid negative text values", () => {
      const slider_value = [0, 50];
      const start_value = -20;
      const end_value = 30;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        [-20, 30],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle valid text values with same start and end", () => {
      const slider_value = [10, 90];
      const start_value = 50;
      const end_value = 50;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        [50, 50],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });
  });

  describe("error handling - invalid values", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id =
        "text-input-component";
    });

    test("should throw PreventUpdate when start_value is NaN", () => {
      const slider_value = [10, 80];
      const start_value = NaN;
      const end_value = 70;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end_value is NaN", () => {
      const slider_value = [10, 80];
      const start_value = 20;
      const end_value = NaN;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when both values are NaN", () => {
      const slider_value = [10, 80];
      const start_value = NaN;
      const end_value = NaN;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when start_value > end_value", () => {
      const slider_value = [10, 80];
      const start_value = 80;
      const end_value = 20;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when start_value is undefined", () => {
      const slider_value = [10, 80];
      const start_value = undefined;
      const end_value = 70;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end_value is undefined", () => {
      const slider_value = [10, 80];
      const start_value = 20;
      const end_value = undefined;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    // Note: Testing null values - in JavaScript, isNaN(null) returns false because null coerces to 0
    test("should throw PreventUpdate when start_value is null (coerces to 0)", () => {
      const slider_value = [10, 80];
      const start_value = null;
      const end_value = 70;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end_value is null", () => {
      const slider_value = [10, 80];
      const start_value = -10;
      const end_value = null;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    // Note: Testing empty string values - in JavaScript, isNaN('') returns false because an empty string coerces to 0, which is a valid number.
    test("should throw PreventUpdate when start_value is empty string", () => {
      const slider_value = [10, 80];
      const start_value = "";
      const end_value = 50;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end_value is empty string", () => {
      const slider_value = [10, 80];
      const start_value = -5;
      const end_value = "";

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when string values cannot be converted to numbers", () => {
      const slider_value = [10, 80];
      const start_value = "not-a-number";
      const end_value = 70;

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when both string values cannot be converted to numbers", () => {
      const slider_value = [10, 80];
      const start_value = "invalid";
      const end_value = "also-invalid";

      expect(() => {
        update_range_slider_values(
          slider_value,
          start_value,
          end_value,
          slider_component_id,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });
  });

  describe("edge cases", () => {
    test("should handle when triggered_id is null", () => {
      global.dash_clientside.callback_context.triggered_id = null;
      const slider_value = [10, 80];
      const start_value = 20;
      const end_value = 70;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      // When triggered_id is null, it's treated as text form component trigger
      expect(result).toEqual([
        [20, 70],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle when triggered_id is empty string", () => {
      global.dash_clientside.callback_context.triggered_id = "";
      const slider_value = [10, 80];
      const start_value = 30;
      const end_value = 60;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      // When triggered_id is empty string, it's treated as text form component trigger
      expect(result).toEqual([
        [30, 60],
        global.dash_clientside.no_update,
        global.dash_clientside.no_update,
      ]);
    });

    test("should handle when slider_value is empty array", () => {
      global.dash_clientside.callback_context.triggered_id =
        slider_component_id;
      const slider_value = [];
      const start_value = 20;
      const end_value = 70;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        global.dash_clientside.no_update,
        undefined, // slider_value[0] is undefined for empty array
        undefined, // slider_value[1] is undefined for empty array
      ]);
    });

    test("should handle when slider_value has only one element", () => {
      global.dash_clientside.callback_context.triggered_id =
        slider_component_id;
      const slider_value = [42];
      const start_value = 20;
      const end_value = 70;

      const result = update_range_slider_values(
        slider_value,
        start_value,
        end_value,
        slider_component_id,
      );

      expect(result).toEqual([
        global.dash_clientside.no_update,
        42, // slider_value[0]
        undefined, // slider_value[1] is undefined
      ]);
    });
  });
});
