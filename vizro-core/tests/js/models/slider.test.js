// Mock dash_clientside first
global.dash_clientside = {
  no_update: "no_update",
  PreventUpdate: "PreventUpdate",
  callback_context: {
    triggered_id: null,
  },
};

// Mock window.dash_clientside
global.window = {
  dash_clientside: global.dash_clientside,
};

// Import the module to test
require("../../../src/vizro/static/js/models/slider.js");

describe("update_slider_values", () => {
  const sliderComponentId = "test-slider";

  beforeEach(() => {
    // Reset callback context before each test
    global.dash_clientside.callback_context.triggered_id = null;
  });

  describe("when slider component is triggered", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id = sliderComponentId;
    });

    test("should update end value when slider value changes", () => {
      const sliderValue = 50;
      const endValue = 30;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toBe(sliderValue);
    });

    test("should handle negative slider values", () => {
      const sliderValue = -25;
      const endValue = 10;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toBe(sliderValue);
    });

    test("should handle zero slider value", () => {
      const sliderValue = 0;
      const endValue = 100;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toBe(sliderValue);
    });

    test("should handle decimal slider values", () => {
      const sliderValue = 42.5;
      const endValue = 20;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toBe(sliderValue);
    });
  });

  describe("when text form component is triggered", () => {
    beforeEach(() => {
      global.dash_clientside.callback_context.triggered_id =
        "some-other-component";
    });

    test("should update slider value when valid end value is provided", () => {
      const sliderValue = 30;
      const endValue = 75;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle zero end value", () => {
      const sliderValue = 50;
      const endValue = 0;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle negative end values", () => {
      const sliderValue = 20;
      const endValue = -15;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle decimal end values", () => {
      const sliderValue = 40;
      const endValue = 37.8;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should throw PreventUpdate when end value is NaN", () => {
      const sliderValue = 30;
      const endValue = "invalid";

      expect(() => {
        window.dash_clientside.slider.update_slider_values(
          sliderValue,
          endValue,
          sliderComponentId,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end value is undefined", () => {
      const sliderValue = 30;
      const endValue = undefined;

      expect(() => {
        window.dash_clientside.slider.update_slider_values(
          sliderValue,
          endValue,
          sliderComponentId,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end value is null", () => {
      const sliderValue = 30;
      const endValue = null;

      expect(() => {
        window.dash_clientside.slider.update_slider_values(
          sliderValue,
          endValue,
          sliderComponentId,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });

    test("should throw PreventUpdate when end value is empty string", () => {
      const sliderValue = 30;
      const endValue = "";

      expect(() => {
        window.dash_clientside.slider.update_slider_values(
          sliderValue,
          endValue,
          sliderComponentId,
        );
      }).toThrow(global.dash_clientside.PreventUpdate);
    });
  });

  describe("edge cases", () => {
    test("should handle string numbers as end values", () => {
      global.dash_clientside.callback_context.triggered_id = "text-input";
      const sliderValue = 20;
      const endValue = "45";

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });

    test("should handle very large numbers", () => {
      global.dash_clientside.callback_context.triggered_id = sliderComponentId;
      const sliderValue = 999999;
      const endValue = 100;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(global.dash_clientside.no_update);
      expect(result[1]).toBe(sliderValue);
    });

    test("should handle very small decimal numbers", () => {
      global.dash_clientside.callback_context.triggered_id = "text-input";
      const sliderValue = 50;
      const endValue = 0.001;

      const result = window.dash_clientside.slider.update_slider_values(
        sliderValue,
        endValue,
        sliderComponentId,
      );

      expect(result[0]).toBe(endValue);
      expect(result[1]).toBe(global.dash_clientside.no_update);
    });
  });
});
