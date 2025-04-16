import random

import e2e.vizro.constants as cnst

import vizro.models as vm
import vizro.plotly.express as px
from vizro.tables import dash_ag_grid, dash_data_table

tips = px.data.tips()


def generate_lorem_ipsum(length=None):
    lorem_ipsum = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sed elementum ligula, in pharetra velit.
            In ultricies est ac mauris vehicula fermentum. Curabitur faucibus elementum lectus, vitae luctus libero
            fermentum.
            Name ut ipsum tortor. Praesent ut nulla risus. Praesent in dignissim nulla. In quis blandit ipsum.
        """
    words = lorem_ipsum.split()
    length = random.randint(100, 500) if length is None else length
    while len(" ".join(words)) < length:
        words += words  # repeat the words to extend the length
    return " ".join(words)[:length]


layout_flex_without_params = vm.Page(
    title=cnst.LAYOUT_FLEX_DEFAULT,
    layout=vm.Flex(),
    components=[
        vm.Card(text=generate_lorem_ipsum(300)),
        vm.Card(text=generate_lorem_ipsum(300)),
        vm.Card(text=generate_lorem_ipsum(300)),
        vm.Card(text=generate_lorem_ipsum(100)),
        vm.Card(text=generate_lorem_ipsum(500)),
        vm.Card(text=generate_lorem_ipsum(400)),
    ],
)

layout_flex_with_all_params_and_card = vm.Page(
    title=cnst.LAYOUT_FLEX_ALL_PARAMS,
    layout=vm.Flex(direction="row", gap="40px", wrap=True),
    components=[
        vm.Card(text=generate_lorem_ipsum(300), extra={"style": {"width": "240px"}}),
        vm.Card(text=generate_lorem_ipsum(300), extra={"style": {"width": "240px"}}),
        vm.Card(text=generate_lorem_ipsum(300), extra={"style": {"width": "240px"}}),
        vm.Card(text=generate_lorem_ipsum(100), extra={"style": {"width": "240px"}}),
        vm.Card(text=generate_lorem_ipsum(500), extra={"style": {"width": "240px"}}),
        vm.Card(text=generate_lorem_ipsum(400), extra={"style": {"width": "240px"}}),
    ],
)

layout_flex_with_direction_param_and_graph = vm.Page(
    title=cnst.LAYOUT_FLEX_DIRECTION_AND_GRAPH,
    layout=vm.Flex(direction="row"),
    components=[vm.Graph(figure=px.violin(tips, y="tip", x="day", color="day", box=True, width=300)) for i in range(6)],
)

layout_flex_with_gap_param_and_table = vm.Page(
    title=cnst.LAYOUT_FLEX_GAP_AND_TABLE,
    layout=vm.Flex(gap="40px"),
    components=[vm.Table(figure=dash_data_table(tips, style_table={"width": "1000px"})) for i in range(3)],
)

layout_flex_with_wrap_param_and_ag_grid = vm.Page(
    title=cnst.LAYOUT_FLEX_WRAP_AND_AG_GRID,
    layout=vm.Flex(wrap=True),
    components=[vm.AgGrid(figure=dash_ag_grid(tips, style={"width": 1000})) for i in range(3)],
)

buttons_page = vm.Page(
    title=cnst.BUTTONS_PAGE,
    layout=vm.Flex(direction="row"),
    components=[
        vm.Button(text="default"),
        vm.Button(text="filled", variant="filled"),
        vm.Button(text="outlined", variant="outlined"),
        vm.Button(text="plain", variant="plain"),
        vm.Button(extra={"color": "success"}),
        vm.Button(variant="outlined", extra={"color": "success"}),
    ],
)
