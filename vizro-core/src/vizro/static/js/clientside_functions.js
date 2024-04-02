import {
  _update_dashboard_theme,
  _collapse_nav_panel,
  _update_ag_grid_theme,
} from "./models/dashboard.js";
import { _update_range_slider_values } from "./models/range_slider.js";
import { _update_slider_values } from "./models/slider.js";
import {
  _trigger_to_global_store,
  _gateway,
  _after_action_cycle_breaker,
} from "./actions/build_action_loop_callbacks.js";
import {
  _update_date_picker_values,
  _update_date_picker_position,
} from "./models/date_picker.js";

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    update_dashboard_theme: _update_dashboard_theme,
    update_range_slider_values: _update_range_slider_values,
    update_slider_values: _update_slider_values,
    trigger_to_global_store: _trigger_to_global_store,
    gateway: _gateway,
    after_action_cycle_breaker: _after_action_cycle_breaker,
    collapse_nav_panel: _collapse_nav_panel,
    update_ag_grid_theme: _update_ag_grid_theme,
    update_date_picker_values: _update_date_picker_values,
    update_date_picker_position: _update_date_picker_position,
  },
});
