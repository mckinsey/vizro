"""Generate color and palette reference images for documentation."""

import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from vizro.themes import colors, palettes


def _load_theme_colors(theme):
    """Load background and text colors from Plotly template JSON files."""
    template_file = Path(__file__).parent.parent / "src" / "vizro" / "themes" / f"vizro_{theme}.json"
    with open(template_file) as f:
        template = json.load(f)
    return template["layout"]["plot_bgcolor"], template["layout"]["font"]["color"]


def _get_text_color(hex_color):
    """Determine contrasting text color (black/white) for a given hex color."""
    BRIGHTNESS_THRESHOLD = 128
    if not hex_color.startswith("#"):
        return "black"
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    return "white" if (r * 299 + g * 587 + b * 114) / 1000 < BRIGHTNESS_THRESHOLD else "black"


def _save_image(fig, output_path):
    """Save figure to image file."""
    fig.write_image(output_path, width=fig.layout.width, height=fig.layout.height, scale=2)
    print(f"✓ Generated {output_path}")  # noqa: T201


def make_color_swatches(color_groups, cols, labels):
    """Create color swatch visualization."""
    BOX_SIZE, GAP = 100, 0.15
    counts = [len(group) for group in color_groups.values()]

    # Generate coordinates
    xs = [i * (1 + GAP) for count in counts for i in range(count)]
    ys = [r * (1 + GAP) for r, count in enumerate(counts) for _ in range(count)]

    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker={"symbol": "square", "size": BOX_SIZE, "color": cols, "line": {"width": 1, "color": "#ddd"}},
            hoverinfo="skip",
        )
    )

    # Add labels inside boxes
    for x, y, label, col in zip(xs, ys, labels, cols):
        fig.add_annotation(
            x=x,
            y=y,
            text=label,
            showarrow=False,
            font={"size": 12, "color": _get_text_color(col)},
        )

    fig.update_layout(
        width=max(counts) * (1 + GAP) * BOX_SIZE + 50,
        height=len(counts) * (1 + GAP) * BOX_SIZE + 60,
        margin={"l": 0, "r": 0, "t": 10, "b": 10},
        xaxis={"visible": False},
        yaxis={"visible": False, "autorange": "reversed", "scaleanchor": "x", "scaleratio": 1},
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )

    return fig


def generate_colors_image(output_path):
    """Generate colors reference image."""
    color_groups = {
        "Qualitative": [
            "blue",
            "dark_purple",
            "turquoise",
            "dark_green",
            "light_purple",
            "light_green",
            "light_pink",
            "dark_pink",
            "yellow",
            "gray",
        ],
        "Blue": [f"blue_{i}00" for i in range(1, 10)],
        "Purple": [f"purple_{i}00" for i in range(1, 10)],
        "Turquoise": [f"turquoise_{i}00" for i in range(1, 10)],
        "Green": [f"green_{i}00" for i in range(1, 10)],
        "Pink": [f"pink_{i}00" for i in range(1, 10)],
        "Yellow": [f"yellow_{i}00" for i in range(1, 10)],
        "Grey": [f"gray_{i}00" for i in range(1, 10)],
        "Special": ["transparent", "white", "black"],
    }

    labels = [name for group in color_groups.values() for name in group]
    cols = [getattr(colors, name) for name in labels]
    _save_image(make_color_swatches(color_groups, cols, labels), output_path)


def make_palette_gradients(palette_groups, theme="light"):
    """Create continuous gradient bars for palettes using heatmap."""
    bg_color, text_color = _load_theme_colors(theme)
    BAR_HEIGHT, BAR_WIDTH, GAP = 80, 600, 10
    NUM_ROWS, NUM_COLS = 50, 500

    left_margin = 260
    total_height = len(palette_groups) * (BAR_HEIGHT + GAP) - GAP + 40

    fig = go.Figure()
    y_tickvals, y_ticktext = [], []

    for idx, (name, palette) in enumerate(palette_groups.items()):
        y_pos = idx * (BAR_HEIGHT + GAP)
        y_tickvals.append(y_pos + BAR_HEIGHT / 2)
        y_ticktext.append(name)

        fig.add_trace(
            go.Heatmap(
                z=np.tile(np.linspace(0, 1, NUM_COLS), (NUM_ROWS, 1)),
                y=np.linspace(y_pos, y_pos + BAR_HEIGHT, NUM_ROWS),
                x=np.linspace(0, BAR_WIDTH, NUM_COLS),
                colorscale=[[i / (len(palette) - 1), color] for i, color in enumerate(palette)],
                showscale=False,
                hoverinfo="skip",
                zmin=0,
                zmax=1,
            )
        )

    fig.update_layout(
        width=left_margin + BAR_WIDTH + 40,
        height=total_height,
        margin={"l": left_margin, "r": 40, "t": 20, "b": 20},
        xaxis={"visible": False, "range": [-20, BAR_WIDTH + 10]},
        yaxis={
            "visible": True,
            "range": [-10, total_height - 30],
            "tickmode": "array",
            "tickvals": y_tickvals,
            "ticktext": y_ticktext,
            "tickfont": {"size": 24, "color": text_color},
            "showgrid": False,
            "zeroline": False,
            "autorange": "reversed",
        },
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=False,
    )

    return fig


def make_qualitative_palette(palette, theme="light"):
    """Create discrete color boxes for qualitative palette."""
    bg_color, text_color = _load_theme_colors(theme)
    BOX_SIZE, GAP = 80, 0.15

    fig = go.Figure(
        go.Scatter(
            x=[i * (1 + GAP) for i in range(len(palette))],
            y=[0] * len(palette),
            mode="markers",
            marker={"symbol": "square", "size": BOX_SIZE, "color": palette, "line": {"width": 0}},
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        width=len(palette) * (1 + GAP) * BOX_SIZE + 260,
        height=140,
        margin={"l": 220, "r": 10, "t": 20, "b": 20},
        xaxis={"visible": False},
        yaxis={
            "visible": True,
            "range": [-0.6, 0.6],
            "scaleanchor": "x",
            "scaleratio": 1,
            "tickmode": "array",
            "tickvals": [0],
            "ticktext": ["qualitative"],
            "tickfont": {"size": 24, "color": text_color},
            "showgrid": False,
            "zeroline": False,
        },
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        showlegend=False,
    )

    return fig


def generate_qualitative_palette_image(output_path, theme="light"):
    """Generate qualitative palette reference image with discrete boxes."""
    _save_image(make_qualitative_palette(palettes.qualitative, theme), output_path)


def generate_palettes_image(output_path, theme="light"):
    """Generate palettes reference image with continuous gradients (excluding qualitative)."""
    palette_groups = {name: getattr(palettes, name) for name in vars(palettes) if name != "qualitative"}
    _save_image(make_palette_gradients(palette_groups, theme), output_path)


def main():
    """Generate theme reference images."""
    output_dir = Path(__file__).parent.parent / "docs" / "assets" / "user_guides" / "themes"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating theme reference images...")  # noqa: T201

    generate_colors_image(output_dir / "colors.png")

    for theme in ["light", "dark"]:
        generate_qualitative_palette_image(output_dir / f"palette_qualitative_{theme}.png", theme)
        generate_palettes_image(output_dir / f"palettes_continuous_{theme}.png", theme)

    print("\n✅ All theme images generated successfully!")  # noqa: T201


if __name__ == "__main__":
    main()
