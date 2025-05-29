# Console errors and warnings

INVALID_PROP_ERROR = "Invalid prop `persisted_props[0]` of value `on` supplied to `t`"
REACT_NOT_RECOGNIZE_ERROR = "React does not recognize the `%s` prop on a DOM element"
SCROLL_ZOOM_ERROR = "_scrollZoom"
REACT_RENDERING_ERROR = "unstable_flushDiscreteUpdates: Cannot flush updates when React is already rendering"
UNMOUNT_COMPONENTS_ERROR = "React state update on an unmounted component"
WILLMOUNT_RENAMED_WARNING = "componentWillMount has been renamed"
WILLRECEIVEPROPS_RENAMED_WARNING = "componentWillReceiveProps has been renamed"
READPIXELS_WARNING = "GPU stall due to ReadPixels"
WEBGL_WARNING = "WebGL"  # https://issues.chromium.org/issues/40277080

# Pages and its components

HOME_PAGE = "homepage (cards + graph)"
HOME_PAGE_PATH = "/"
HOME_PAGE_ID = "hp"
AREA_GRAPH_ID = "ArEa"
DROPDOWN_FILTER_HOMEPAGEPAGE = "drop-homepagepage"

FILTERS_PAGE = "filters page (tabs + containers)"
FILTERS_PAGE_PATH = "/filters-page-tabs--containers"
FILTERS_TAB_CONTAINER = "filters tab_container"
FILTERS_COMPONENTS_CONTAINER = "filters components container"
SCATTER_GRAPH_ID = "scatter"
BOX_GRAPH_ID = "box graph"
DROPDOWN_FILTER_FILTERS_PAGE = "drop-filters-page"
RADIO_ITEMS_FILTER_FILTERS_PAGE = "radio-filters-page"
CHECK_LIST_FILTER_FILTERS_PAGE = "check filters-page"
SLIDER_FILTER_FILTERS_PAGE = "slider-filters-page"
RANGE_SLIDER_FILTER_FILTERS_PAGE = "range slider-filters-page"
FILTERED_CSV = "scatter.csv"
FILTERED_XLSX = "scatter.xlsx"
FILTERED_BASE_CSV = "tests/tests_utils/e2e/vizro/files/filtered_scatter_base.csv"

FILTERS_INSIDE_CONTAINERS_PAGE = "filters inside containers page (tabs + containers)"
FILTERS_INSIDE_CONTAINERS_PAGE_PATH = "/filters-inside-containers-page-tabs--containers"
SCATTER_INSIDE_CONTAINER = "scatter_inside_container"
DROPDOWN_INSIDE_CONTAINERS = "drop-inside filters-page"
RADIO_ITEMS_INSIDE_CONTAINERS = "radio-inside filters-page"
CHECK_LIST_INSIDE_CONTAINERS = "check inside filters-page"
SLIDER_INSIDE_CONTAINERS = "slider-inside filters-page"
RANGE_SLIDER_INSIDE_CONTAINERS = "range slider-inside filters-page"
RANGE_DATEPICKER_INSIDE_CONTAINERS = "range datepicker-inside filters-page"

PARAMETERS_PAGE = "parameters_p@ge! (tabs + containers)"
PARAMETERS_PAGE_PATH = "/parameters_page"
PARAMETERS_TAB_CONTAINER = "parameters-tab_container"
PARAMETERS_SUB_TAB_ID = "sub tab params"
PARAMETERS_SUB_TAB_CONTAINER_ONE = "parameters sub t@b container 1"
PARAMETERS_SUB_TAB_CONTAINER_TWO = "parameters sub t@b container 2"
PARAMETERS_CONTAINER = "parameters container"
BAR_GRAPH_ID = "b@R-graph"
BAR_GRAPH_ID_CONTAINER = "b@R-graph__container"
HISTOGRAM_GRAPH_ID = "-histogram-graph--"
DROPDOWN_PARAMETERS_ONE = "dropdown parameters one"
DROPDOWN_PARAMETERS_TWO = "dropdown parameters two"
RADIO_ITEMS_PARAMETERS_ONE = "radio items parameters one"
RADIO_ITEMS_PARAMETERS_TWO = "radio items parameters two"
SLIDER_PARAMETERS = "slider parameters"
RANGE_SLIDER_PARAMETERS = "range slider parameters"

FILTER_INTERACTIONS_PAGE = "filter-interactions-page"
SCATTER_INTERACTIONS_ID = "scatter_inter"
BOX_INTERACTIONS_ID = "box_inter"
CARD_INTERACTIONS_ID = "card_inter"
DROPDOWN_INTER_FILTER = "dropdown_inter_filter"
RADIOITEM_INTER_PARAM = "radio_inter_param"

KPI_INDICATORS_PAGE = "kpi-indicators-page"
DROPDOWN_FILTER_KPI_PAGE = "drop-kpi-page"

EXPORT_PAGE = "export page"
EXPORT_PAGE_PATH = "/exportp"
LINE_EXPORT_ID = "line--export--id"
UNFILTERED_CSV = "line--export--id.csv"
UNFILTERED_XLSX = "line--export--id.xlsx"
UNFILTERED_BASE_CSV = "tests/tests_utils/e2e/vizro/files/unfiltered_line_base.csv"

DATEPICKER_PAGE = "datepicker-page"
BAR_POP_RANGE_ID = "bar pop range"
BAR_POP_DATE_ID = "bar pop date"
TABLE_POP_RANGE_ID = "table pop range"
TABLE_POP_DATE_ID = "table pop date"
DATEPICKER_RANGE_ID = "datepicker range"
DATEPICKER_SINGLE_ID = "datepicker single"

DATEPICKER_PARAMS_PAGE = "datepicker-parameters-page"
DATEPICKER_PARAMS_ID = "datepicker_params"
BAR_CUSTOM_ID = "bar_custom"

TABLE_AG_GRID_PAGE = "table-ag-grid-page"
TABLE_AG_GRID_ID = "123_ag_grid_table"
BOX_AG_GRID_PAGE_ID = "B@x on ag grid page"
TABLE_AG_GRID_CONTAINER = "table_ag_grid_container"
RADIOITEMS_AGGRID_FILTER = "radioitems_agdrid_filter"
CHECKLIST_AGGRID_FILTER = "checklist_agdrid_filter"
RANGESLIDER_AGGRID_FILTER = "rangeslider_agdrid_filter"
AG_GRID_TOOLTIP_TEXT = "AgGrid tooltip"
AG_GRID_TOOLTIP_ICON = "info"

TABLE_AG_GRID_INTERACTIONS_PAGE = "table-ag-grid-inter-page"
TABLE_AG_GRID_INTERACTIONS_ID = "ag grid inter id"
LINE_AG_GRID_INTERACTIONS_ID = "line_ag_grid_inter"

TABLE_PAGE = "table-page"
TABLE_ID = "123_table"
TABLE_CONTAINER = "table container"
RADIOITEMS_TABLE_FILTER = "radioitems_table_filter"
CHECKLIST_TABLE_FILTER = "checklist_table_filter"
RANGESLIDER_TABLE_FILTER = "rangeslider_table_filter"
TABLE_TOOLTIP_TEXT = "Table tooltip"
TABLE_TOOLTIP_ICON = "info"

TABLE_INTERACTIONS_PAGE = "table-inter-page"
TABLE_INTERACTIONS_ID = "interactions-123_table"
LINE_INTERACTIONS_ID = "line inter id"

DYNAMIC_DATA_PAGE = "dynamic-data-page"
SCATTER_DYNAMIC_CACHED_ID = "scatter_dynamic_cached"
SCATTER_DYNAMIC_ID = "scatter_dynamic"
SLIDER_DYNAMIC_DATA_CACHED_ID = "slider_dynamic_data_cached"
SLIDER_DYNAMIC_DATA_ID = "slider_dynamic_data"

DYNAMIC_DATA_DF_PARAMETER_PAGE = "dynamic-filter-update-from-dfp"
SCATTER_DF_PARAMETER = "scatter_dynamic_data_frame_parameter"
SCATTER_DF_STATIC = "scatter_data_frame_parameter_static"
RADIOITEMS_FILTER_DF_PARAMETER = "radioitems filter with df parameter"
SLIDER_DF_PARAMETER = "slider df parameter"

DYNAMIC_FILTERS_CATEGORICAL_PAGE = "dynamic-filters-categorical"
BOX_DYNAMIC_FILTERS_ID = "box dynamic"
DROPDOWN_MULTI_DYNAMIC_FILTER_ID = "dropdown_multi_dynamic"
DROPDOWN_DYNAMIC_FILTER_ID = "dropdown_dynamic"
CHECKLIST_DYNAMIC_FILTER_ID = "checklist_dynamic"
RADIOITEMS_DYNAMIC_FILTER_ID = "radio_dynamic"

DYNAMIC_FILTERS_NUMERICAL_PAGE = "dynamic-filters-numerical"
BAR_DYNAMIC_FILTER_ID = "bar_dynamic"
SLIDER_DYNAMIC_FILTER_ID = "slider_dynamic"
RANGE_SLIDER_DYNAMIC_FILTER_ID = "range_slider_dynamic"

DYNAMIC_FILTERS_DATEPICKER_PAGE = "dynamic-filters-datepicker-numerical"
BAR_DYNAMIC_DATEPICKER_SINGLE_FILTER_ID = "bar_dynamic_single_datepicker"
BAR_DYNAMIC_DATEPICKER_FILTER_ID = "bar_dynamic_datepicker"
DATEPICKER_DYNAMIC_RANGE_ID = "datepicker dynamic range"
DATEPICKER_DYNAMIC_SINGLE_ID = "datepicker dynamic single"

CUSTOM_COMPONENTS_PAGE = "custom-components-page"
SCATTER_CUSTOM_COMPONENTS_ID = "scatter_custom_id"
CUSTOM_DROPDOWN_ID = "dropdown_custom"
CUSTOM_RANGE_SLIDER_ID = "range_slider_custom"

FILTER_AND_PARAM_PAGE = "filter-and-param-page"
BOX_FILTER_AND_PARAM_ID = "box mix graph"
DROPDOWN_FILTER_AND_PARAM = "dropdown mix filter"
RADIO_ITEMS_FILTER_AND_PARAM = "radioitems mix param"

CONTAINER_VARIANTS_PAGE = "container-variants"
SCATTER_FILLED = "scatter filled"
SCATTER_OUTLINED = "scatter outlined"

LAYOUT_FLEX_DEFAULT = "flex-default"

LAYOUT_FLEX_ALL_PARAMS = "flex-all-params"

LAYOUT_FLEX_DIRECTION_AND_GRAPH = "flex-direction-and-graph"

LAYOUT_FLEX_GAP_AND_TABLE = "flex-gap-and-table"

LAYOUT_FLEX_WRAP_AND_AG_GRID = "flex-wrap-and-ag_grid"

BUTTONS_PAGE = "buttons-with-different-styles"

EXTRAS_PAGE = "extras-page"
DROPDOWN_TOOLTIP_TEXT = "Dropdown tooltip with extra parameters if you like!"
DROPDOWN_TOOLTIP_ICON = "progress_activity"
RADIOITEMS_TOOLTIP_TEXT = "Simple description tooltip for RadioItems, is it ok?"
RADIOITEMS_TOOLTIP_ICON = "info"
CHECKLIST_TOOLTIP_TEXT = (
    "Checklist tooltip without extra parameters multiple times. "
    "Checklist tooltip without extra parameters multiple times. "
    "Checklist tooltip without extra parameters multiple times. "
    "Checklist tooltip without extra parameters multiple times."
)
CHECKLIST_TOOLTIP_ICON = "stat_0"
SLIDER_TOOLTIP_TEXT = "Tooltip again, this time for slider"
SLIDER_TOOLTIP_ICON = "sync_arrow_down"
RANGESLIDER_TOOLTIP_TEXT = "Range Slider deserves proper text here, in future, and proper icon"
RANGESLIDER_TOOLTIP_ICON = "rebase"
DATEPICKER_TOOLTIP_TEXT = "Datepicker, show me your tooltip, please!"
DATEPICKER_TOOLTIP_ICON = "deployed_code"
PAGE_TOOLTIP_TEXT = "Page tooltip"
PAGE_TOOLTIP_ICON = "view_timeline"
CONTAINER_TOOLTIP_TEXT = "Container tooltip"
CONTAINER_TOOLTIP_ICON = "width_normal"
GRAPH_TOOLTIP_TEXT = "Graph tooltip"
GRAPH_TOOLTIP_ICON = "resize"


COLLAPSIBLE_CONTAINERS_GRID = "collapsible-containers-grid-layout"

COLLAPSIBLE_CONTAINERS_FLEX = "collapsible-containers-flex-layout"

PAGE_404_PATH = "/404-page"

# Accordion names

GENERAL_ACCORDION = "generAl"
DATEPICKER_ACCORDION = "DATEpicker"
AG_GRID_ACCORDION = "AGgrid"
DYNAMIC_DATA_ACCORDION = "DYNAMIC data"
KPI_ACCORDION = "KPI"
CONTAINER_ACCORDION = "Containers"
LAYOUT_ACCORDION = "Layouts"

# Ports

DEFAULT_PORT = 5002
ONE_PAGE_PORT = 5003
NAVBAR_ACCORDIONS_PORT = 5004
NAVBAR_PAGES_PORT = 5005
NAVBAR_NAVLINK_PORT = 5006
YAML_PORT = 5007

# Dashboards

DASHBOARD_DEFAULT = "dashboard_default_gunicorn"
DASHBOARD_YAML = "dashboard_yaml_gunicorn"

# Themes

THEME_DARK = "dark"
THEME_LIGHT = "light"
RGBA_TRANSPARENT = "rgba(0, 0, 0, 0)"
STYLE_TRANSPARENT = "background: rgba(0, 0, 0, 0);"
STYLE_TRANSPARENT_FIREFOX = "background: none;"
AG_GRID_DARK = "ag-theme-quartz-dark ag-theme-vizro"
AG_GRID_LIGHT = "ag-theme-quartz ag-theme-vizro"

# Configs

DYNAMIC_FILTERS_DATA_CONFIG = "tests/e2e/vizro/dashboards/default/dynamic_filters_data.yaml"
PIXELMATCH_THRESHOLD = "0.18"
SELENIUM_WAITERS_TIMEOUT = 10
