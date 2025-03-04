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

FILTERS_PAGE = "filters page (tabs + containers)"
FILTERS_PAGE_PATH = "/filters-page-tabs--containers"
FILTERS_TAB_CONTAINER = "filters tab_container"
FILTERS_COMPONENTS_CONTAINER = "filters components container"
SCATTER_GRAPH_ID = "Scatter"
BOX_GRAPH_ID = "box graph"
RADIO_ITEMS_FILTER_FILTERS_PAGE = "radio-filters-page"
CHECK_LIST_FILTER_FILTERS_PAGE = "check filters-page"
SLIDER_FILTER_FILTERS_PAGE = "slider-filters-page"
RANGE_SLIDER_FILTER_FILTERS_PAGE = "range slider-filters-page"

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

FILTER_INTERACTIONS_PAGE = "filter interactions page"
FILTER_INTERACTIONS_PAGE_PATH = "/filter-interactions-page"
SCATTER_INTERACTIONS_ID = "scatter_inter"
BOX_INTERACTIONS_ID = "box_inter"
CARD_INTERACTIONS_ID = "card_inter"

KPI_INDICATORS_PAGE = "kpi indicators page"
KPI_INDICATORS_PAGE_PATH = "/kpi-indicators-page"

EXPORT_PAGE = "export page"
EXPORT_PAGE_PATH = "/exportp"
LINE_EXPORT_ID = "line--export--id"

DATEPICKER_PAGE = "DATEpicker page"
DATEPICKER_PAGE_PATH = "/datepicker-page"
BAR_POP_RANGE_ID = "bar pop range"
BAR_POP_DATE_ID = "bar pop date"
TABLE_POP_RANGE_ID = "table pop range"
TABLE_POP_DATE_ID = "table pop date"

TABLE_AG_GRID_PAGE = "table AG grid page"
TABLE_AG_GRID_PAGE_PATH = "/table-ag-grid-page"
TABLE_AG_GRID_ID = "123_ag_grid_table"
BOX_AG_GRID_PAGE_ID = "B@x on ag grid page"
TABLE_AG_GRID_CONTAINER = "table_ag_grid_container"

TABLE_PAGE = "table page"
TABLE_PAGE_PATH = "/table-page"
TABLE_ID = "123_table"
TABLE_CONTAINER = "table container"

TABLE_INTERACTIONS_PAGE = "table inter page"
TABLE_INTERACTIONS_PAGE_PATH = "/table-inter-page"
TABLE_INTERACTIONS_ID = "interactions-123_table"
LINE_INTERACTIONS_ID = "line inter id"

DYNAMIC_DATA_PAGE = "dynamic data page"
DYNAMIC_DATA_PAGE_PATH = "/dynamic-data-page"
SCATTER_DYNAMIC_CACHED_ID = "scatter_dynamic_cached"
SCATTER_DYNAMIC_ID = "scatter_dynamic"
SLIDER_DYNAMIC_DATA_CACHED_ID = "slider_dynamic_data_cached"
SLIDER_DYNAMIC_DATA_ID = "slider_dynamic_data"

DYNAMIC_FILTERS_CATEGORICAL_PAGE = "dynamic filters categorical"
DYNAMIC_FILTERS_CATEGORICAL_PAGE_PATH = "/dynamic-filters-categorical"
BOX_DYNAMIC_FILTERS_ID = "box dynamic"
DROPDOWN_MULTI_DYNAMIC_FILTER_ID = "dropdown_multi_dynamic"
DROPDOWN_DYNAMIC_FILTER_ID = "dropdown_dynamic"
CHECKLIST_DYNAMIC_FILTER_ID = "checklist_dynamic"
RADIOITEMS_DYNAMIC_FILTER_ID = "radio_dynamic"

DYNAMIC_FILTERS_NUMERICAL_PAGE = "dynamic filters numerical"
DYNAMIC_FILTERS_NUMERICAL_PAGE_PATH = "/dynamic-filters-numerical"
BAR_DYNAMIC_FILTER_ID = "bar_dynamic"
SLIDER_DYNAMIC_FILTER_ID = "slider_dynamic"
RANGE_SLIDER_DYNAMIC_FILTER_ID = "range_slider_dynamic"

PAGE_404_PATH = "/404-page"

# Accordion names

GENERAL_ACCORDION = "generAl"
DATEPICKER_ACCORDION = "DATEpicker"
AG_GRID_ACCORDION = "AGgrid"
AG_GRID_ACCORDION_NUMBER = 3
DYNAMIC_DATA_ACCORDION = "DYNAMIC data"
DYNAMIC_DATA_ACCORDION_NUMBER = 4
KPI_ACCORDION = "KPI"

# Ports

DEFAULT_PORT = 5002
ONE_PAGE_PORT = 5003
NAVBAR_ACCORDIONS_PORT = 5004
NAVBAR_PAGES_PORT = 5005
NAVBAR_NAVLINK_PORT = 5006

# Dashboards

DASHBOARD_DEFAULT = "dashboard_default_gunicorn"

# Themes

THEME_DARK = "dark"
THEME_LIGHT = "light"
RGBA_TRANSPARENT = "rgba(0, 0, 0, 0)"
STYLE_TRANSPARENT = "background: rgba(0, 0, 0, 0);"
AG_GRID_DARK = "ag-theme-quartz-dark ag-theme-vizro"
AG_GRID_LIGHT = "ag-theme-quartz ag-theme-vizro"

# Configs

DYNAMIC_FILTERS_DATA_CONFIG = "tests/e2e/vizro/dashboards/default/dynamic_filters_data.yaml"
PIXELMATCH_THRESHOLD = "0.18"
