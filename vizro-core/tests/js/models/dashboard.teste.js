// Mock dash_clientside first
global.dash_clientside = {
  no_update: Symbol("no_update"),
};

// Mock window.dash_clientside
global.window = {
  dash_clientside: global.dash_clientside,
};

require("../../../src/vizro/static/js/models/dashboard.js");

// test("true returns vizro_light and false vizro_dark", () => {
//   expect(update_dashboard_theme(true)).toBe("vizro_light");
//   expect(update_dashboard_theme(false)).toBe("vizro_dark");
// });

describe("_collapse_nav_panel function", () => {
  // test("should return the correct values when n_clicks is not 0 and is_open is true", () => {
  //   const result = _collapse_nav_panel(1, true);
  //   const expected = [
  //     false,
  //     {
  //       transform: "rotate(180deg)",
  //       transition: "transform 0.35s ease-in-out",
  //     },
  //     "Show Menu",
  //     36,
  //   ];
  //   expect(result).toEqual(expected);
  // });
  // test("should return the correct values when n_clicks is not 0 and is_open is false", () => {
  //   const result = _collapse_nav_panel(1, false);
  //   const expected = [
  //     true,
  //     {
  //       transform: "rotate(0deg)",
  //       transition: "transform 0.35s ease-in-out",
  //     },
  //     "Hide Menu",
  //     24,
  //   ];
  //   expect(result).toEqual(expected);
  // });
});
