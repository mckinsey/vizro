import { _update_dashboard_theme, _collapse_nav_panel } from "../../../src/vizro/static/js/models/dashboard.js";


test("true returns vizro_light and false vizro_dark", () => {
  expect(_update_dashboard_theme(true)).toBe("vizro_light");
  expect(_update_dashboard_theme(false)).toBe("vizro_dark");
});


describe('_collapse_nav_panel function', () => {
  test('should return the correct values when n_clicks is 0', () => {
    const is_open = true;
    const result = _collapse_nav_panel(0, is_open);
    const expected = [is_open, { transform: 'rotate(180deg)', transition: 'transform 0.35s ease-in-out' }];

    expect(result).toEqual(expected);
  });

  test('should return the correct values when n_clicks is not 0 and is_open is true', () => {
    const result = _collapse_nav_panel(1, true);
    const expected = [false, { transform: 'rotate(0deg)' }, 'Show Menu'];

    expect(result).toEqual(expected);
  });

  test('should return the correct values when n_clicks is not 0 and is_open is false', () => {
    const result = _collapse_nav_panel(1, false);
    const expected = [true, { transform: 'rotate(180deg)', transition: 'transform 0.35s ease-in-out' }, 'Hide Menu'];

    expect(result).toEqual(expected);
  });
});
