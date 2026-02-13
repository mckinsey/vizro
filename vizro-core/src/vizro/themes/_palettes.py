from types import SimpleNamespace

from ._colors import colors

qualitative = [
    colors.blue,
    colors.dark_purple,
    colors.turquoise,
    colors.dark_green,
    colors.light_purple,
    colors.light_green,
    colors.light_pink,
    colors.dark_pink,
    colors.yellow,
    colors.gray,
]

sequential_blue = [
    colors.blue_100,
    colors.blue_200,
    colors.blue_300,
    colors.blue_400,
    colors.blue_500,
    colors.blue_600,
    colors.blue_700,
    colors.blue_800,
    colors.blue_900,
]

sequential_purple = [
    colors.purple_100,
    colors.purple_200,
    colors.purple_300,
    colors.purple_400,
    colors.purple_500,
    colors.purple_600,
    colors.purple_700,
    colors.purple_800,
    colors.purple_900,
]

sequential_turquoise = [
    colors.turquoise_100,
    colors.turquoise_200,
    colors.turquoise_300,
    colors.turquoise_400,
    colors.turquoise_500,
    colors.turquoise_600,
    colors.turquoise_700,
    colors.turquoise_800,
    colors.turquoise_900,
]

sequential_green = [
    colors.green_100,
    colors.green_200,
    colors.green_300,
    colors.green_400,
    colors.green_500,
    colors.green_600,
    colors.green_700,
    colors.green_800,
    colors.green_900,
]

sequential_pink = [
    colors.pink_100,
    colors.pink_200,
    colors.pink_300,
    colors.pink_400,
    colors.pink_500,
    colors.pink_600,
    colors.pink_700,
    colors.pink_800,
    colors.pink_900,
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

sequential_gray = [
    colors.gray_100,
    colors.gray_200,
    colors.gray_300,
    colors.gray_400,
    colors.gray_500,
    colors.gray_600,
    colors.gray_700,
    colors.gray_800,
    colors.gray_900,
]

# These are necessarily the same for dark and light themes.
# For plotly express plots, some colors are taken from the template's palettes and stored in
# fig.data rather than fig.layout. This means they cannot be changed consistently by post-fig
# updates to fig.layout.template (e.g. in the clientside callback we currently use).
palettes = SimpleNamespace(
    qualitative=qualitative,
    sequential=sequential_blue,
    sequential_minus=sequential_pink[::-1],
    sequential_blue=sequential_blue,
    sequential_purple=sequential_purple,
    sequential_turquoise=sequential_turquoise,
    sequential_green=sequential_green,
    sequential_pink=sequential_pink,
    sequential_yellow=sequential_yellow,
    sequential_gray=sequential_gray,
)
