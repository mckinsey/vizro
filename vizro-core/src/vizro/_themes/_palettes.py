"""Color palettes by Vizro."""

from types import SimpleNamespace

from ._colors import colors

qualitative = [
    colors.cyan,
    colors.orange,
    colors.dark_purple,
    colors.red,
    colors.teal,
    colors.amber,
    colors.green,
    colors.purple,
    colors.pink,
    colors.dark_green,
]

sequential_cyan = [
    colors.cyan_100,
    colors.cyan_200,
    colors.cyan_300,
    colors.cyan_400,
    colors.cyan_500,
    colors.cyan_600,
    colors.cyan_700,
    colors.cyan_800,
    colors.cyan_900,
]

sequential_orange = [
    colors.orange_100,
    colors.orange_200,
    colors.orange_300,
    colors.orange_400,
    colors.orange_500,
    colors.orange_600,
    colors.orange_700,
    colors.orange_800,
    colors.orange_900,
]

sequential_indigo = [
    colors.indigo_100,
    colors.indigo_200,
    colors.indigo_300,
    colors.indigo_400,
    colors.indigo_500,
    colors.indigo_600,
    colors.indigo_700,
    colors.indigo_800,
    colors.indigo_900,
]

sequential_yellow = [
    colors.yellow_100,
    colors.yellow_200,
    colors.yellow_300,
    colors.yellow_400,
    colors.yellow_500,
    colors.yellow_600,
    colors.yellow_700,
    colors.yellow_800,
    colors.yellow_900,
]

sequential_teal = [
    colors.teal_100,
    colors.teal_200,
    colors.teal_300,
    colors.teal_400,
    colors.teal_500,
    colors.teal_600,
    colors.teal_700,
    colors.teal_800,
    colors.teal_900,
]

sequential_red = [
    colors.red_100,
    colors.red_200,
    colors.red_300,
    colors.red_400,
    colors.red_500,
    colors.red_600,
    colors.red_700,
    colors.red_800,
    colors.red_900,
]

sequential_grey = [
    colors.grey_100,
    colors.grey_200,
    colors.grey_300,
    colors.grey_400,
    colors.grey_500,
    colors.grey_600,
    colors.grey_700,
    colors.grey_800,
    colors.grey_900,
]

diverging_indigo_orange = [
    colors.indigo_900,
    colors.indigo_800,
    colors.indigo_700,
    colors.indigo_600,
    colors.indigo_500,
    colors.indigo_400,
    colors.indigo_300,
    colors.indigo_200,
    colors.indigo_100,
    colors.grey_100,
    colors.orange_100,
    colors.orange_200,
    colors.orange_300,
    colors.orange_400,
    colors.orange_500,
    colors.orange_600,
    colors.orange_700,
    colors.orange_800,
    colors.orange_900,
]

diverging_orange_teal = [
    colors.orange_900,
    colors.orange_800,
    colors.orange_700,
    colors.orange_600,
    colors.orange_500,
    colors.orange_400,
    colors.orange_300,
    colors.orange_200,
    colors.orange_100,
    colors.grey_100,
    colors.teal_100,
    colors.teal_200,
    colors.teal_300,
    colors.teal_400,
    colors.teal_500,
    colors.teal_600,
    colors.teal_700,
    colors.teal_800,
    colors.teal_900,
]

diverging_red_cyan = [
    colors.red_900,
    colors.red_800,
    colors.red_700,
    colors.red_600,
    colors.red_500,
    colors.red_400,
    colors.red_300,
    colors.red_200,
    colors.red_100,
    colors.grey_100,
    colors.cyan_100,
    colors.cyan_200,
    colors.cyan_300,
    colors.cyan_400,
    colors.cyan_500,
    colors.cyan_600,
    colors.cyan_700,
    colors.cyan_800,
    colors.cyan_900,
]

# These are necessarily the same for dark and light themes.
# For plotly express plots, some colors are taken from the template's palettes and stored in
# fig.data rather than fig.layout. This means they cannot be changed consistently by post-fig
# updates to fig.layout.template (e.g. in the clientside callback we currently use).
palettes = SimpleNamespace(
    qualitative=qualitative,
    sequential_cyan=sequential_cyan,
    sequential_orange=sequential_orange,
    sequential_indigo=sequential_indigo,
    sequential_yellow=sequential_yellow,
    sequential_teal=sequential_teal,
    sequential_red=sequential_red,
    sequential_grey=sequential_grey,
    diverging_indigo_orange=diverging_indigo_orange,
    diverging_orange_teal=diverging_orange_teal,
    diverging_red_cyan=diverging_red_cyan,
)
