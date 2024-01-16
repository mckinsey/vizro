import { _update_dashboard_theme } from "../../../src/vizro/static/js/models/dashboard.js";

test("true returns vizro_light and false vizro_dark", () => {
  expect(_update_dashboard_theme(true)).toBe("vizro_light");
  expect(_update_dashboard_theme(false)).toBe("vizro_dark");
});
