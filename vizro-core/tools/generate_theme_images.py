"""Generate color and palette reference images for documentation."""

from pathlib import Path

import plotly.graph_objects as go

from vizro.themes import colors, palettes


def _get_text_color(hex_color):
    """Determine contrasting text color (black/white) for a given hex color."""
    BRIGHTNESS_THRESHOLD = 128
    if not hex_color.startswith("#"):
        return "black"
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "white" if brightness < BRIGHTNESS_THRESHOLD else "black"


def make_color_swatches(color_groups, cols, labels, show_labels_in_boxes=True, show_group_names=False):
    """Create color swatch visualization."""
    BOX_SIZE, GAP = 70, 0.15

    groups = list(color_groups.keys())
    counts = [len(color_groups[g]) for g in groups]

    # Generate coordinates
    xs = [i * (1 + GAP) for count in counts for i in range(count)]
    ys = [r * (1 + GAP) for r, count in enumerate(counts) for _ in range(count)]

    # Create figure with colored squares
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
    if show_labels_in_boxes:
        for x, y, label, col in zip(xs, ys, labels, cols):
            fig.add_annotation(
                x=x,
                y=y,
                text=label,
                showarrow=False,
                font={"size": 10, "color": _get_text_color(col)},
                xanchor="center",
                yanchor="middle",
            )

    # Add group names on side
    if show_group_names:
        for i, name in enumerate(groups):
            fig.add_annotation(
                x=-0.6,
                y=i * (1 + GAP),
                text=name,
                showarrow=False,
                font={"size": 20, "color": "black"},
                xanchor="right",
                yanchor="middle",
            )

    # Configure layout
    left_margin = 220 if show_group_names else 10
    fig.update_layout(
        width=max(counts) * (1 + GAP) * BOX_SIZE + left_margin + 40,
        height=len(groups) * (1 + GAP) * BOX_SIZE + 60,
        margin={"l": left_margin, "r": 10, "t": 10, "b": 10},
        xaxis={"visible": False, "range": [-1.5, max(counts) * (1 + GAP) - 0.5]},
        yaxis={"visible": False, "autorange": "reversed", "scaleanchor": "x", "scaleratio": 1},
        plot_bgcolor="white",
        paper_bgcolor="white",
        font={"color": "black", "size": 12},
        showlegend=False,
    )

    return fig


def _save_image(fig, output_path):
    """Save figure to image file."""
    fig.write_image(output_path, width=fig.layout.width, height=fig.layout.height, scale=2)
    print(f"✓ Generated {output_path}")  # noqa: T201


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
            "grey",
        ],
        "Cyan": [f"cyan_{i}00" for i in range(1, 10)],
        "Orange": [f"orange_{i}00" for i in range(1, 10)],
        "Indigo": [f"indigo_{i}00" for i in range(1, 10)],
        "Yellow": [f"yellow_{i}00" for i in range(1, 10)],
        "Teal": [f"teal_{i}00" for i in range(1, 10)],
        "Red": [f"red_{i}00" for i in range(1, 10)],
        "Grey": [f"gray_{i}00" for i in range(1, 10)],
        "Special": ["transparent", "white", "black"],
    }

    labels = [name for group in color_groups.values() for name in group]
    cols = [getattr(colors, name) for name in labels]

    fig = make_color_swatches(color_groups, cols, labels, show_labels_in_boxes=True, show_group_names=False)
    _save_image(fig, output_path)


def generate_palettes_image(output_path):
    """Generate palettes reference image."""
    palette_groups = {name: getattr(palettes, name) for name in vars(palettes)}
    labels = [f"{name}[{i}]" for name, palette in palette_groups.items() for i in range(len(palette))]
    cols = [color for palette in palette_groups.values() for color in palette]

    fig = make_color_swatches(palette_groups, cols, labels, show_labels_in_boxes=False, show_group_names=True)
    _save_image(fig, output_path)


def main():
    """Generate theme reference images."""
    output_dir = Path(__file__).parent.parent / "docs" / "assets" / "user_guides" / "themes"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating theme reference images...")  # noqa: T201
    generate_colors_image(output_dir / "colors.png")
    generate_palettes_image(output_dir / "palettes.png")
    print("\n✅ All theme images generated successfully!")  # noqa: T201


if __name__ == "__main__":
    main()
