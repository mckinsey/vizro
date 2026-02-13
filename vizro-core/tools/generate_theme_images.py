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
            "gray",
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


def make_palette_gradients(palette_groups, show_group_names=True, theme="light"):
    """Create continuous gradient bars for palettes using heatmap."""
    import numpy as np

    # Theme settings
    bg_color = "white" if theme == "light" else "#0e1117"
    text_color = "black" if theme == "light" else "white"

    BAR_HEIGHT = 80  # Height of each bar in pixels
    BAR_WIDTH = 600
    GAP = 10

    groups = list(palette_groups.keys())
    num_palettes = len(groups)

    # Calculate dimensions
    left_margin = 220 if show_group_names else 10
    total_height = num_palettes * (BAR_HEIGHT + GAP) - GAP + 40

    fig = go.Figure()

    # Create gradient bar for each palette using heatmap
    for idx, (name, palette) in enumerate(palette_groups.items()):
        y_pos = idx * (BAR_HEIGHT + GAP)

        # Create colorscale from palette
        if len(palette) == 1:
            colorscale = [[0, palette[0]], [1, palette[0]]]
        else:
            colorscale = [[i / (len(palette) - 1), color] for i, color in enumerate(palette)]

        # Create a 2D heatmap with multiple rows to fill vertical space
        # Rows determine the height, columns determine the gradient
        num_rows = 50  # More rows = better fill
        num_cols = 500  # More columns = smoother gradient

        # Create gradient data: each row has the same gradient values
        gradient_row = np.linspace(0, 1, num_cols)
        gradient_data = np.tile(gradient_row, (num_rows, 1))

        # Create y coordinates that span the bar height
        y_coords = np.linspace(y_pos, y_pos + BAR_HEIGHT, num_rows)
        x_coords = np.linspace(0, BAR_WIDTH, num_cols)

        # Add heatmap trace
        fig.add_trace(
            go.Heatmap(
                z=gradient_data,
                y=y_coords,
                x=x_coords,
                colorscale=colorscale,
                showscale=False,
                hoverinfo="skip",
                zmin=0,
                zmax=1,
            )
        )

    # Add group names on side
    if show_group_names:
        for idx, name in enumerate(groups):
            y_pos = idx * (BAR_HEIGHT + GAP) + BAR_HEIGHT / 2
            fig.add_annotation(
                x=-15,
                y=y_pos,
                text=name,
                showarrow=False,
                font={"size": 14, "color": text_color},
                xanchor="right",
                yanchor="middle",
            )

    # Configure layout
    fig.update_layout(
        width=left_margin + BAR_WIDTH + 40,
        height=total_height,
        margin={"l": left_margin, "r": 40, "t": 20, "b": 20},
        xaxis={
            "visible": False,
            "range": [-20, BAR_WIDTH + 10],
        },
        yaxis={
            "visible": False,
            "range": [-10, total_height - 30],
        },
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font={"color": text_color, "size": 12},
        showlegend=False,
    )

    return fig


def make_qualitative_palette(palette, show_label=True, theme="light"):
    """Create discrete color boxes for qualitative palette."""
    # Theme settings
    bg_color = "white" if theme == "light" else "#0e1117"
    text_color = "black" if theme == "light" else "white"

    BOX_SIZE = 80
    GAP = 0.15

    num_colors = len(palette)

    # Generate coordinates
    xs = [i * (1 + GAP) for i in range(num_colors)]
    ys = [0] * num_colors

    # Create figure with colored squares
    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker={"symbol": "square", "size": BOX_SIZE, "color": palette, "line": {"width": 0}},
            hoverinfo="skip",
        )
    )

    # Add label on the side
    if show_label:
        fig.add_annotation(
            x=-0.6,
            y=0,
            text="qualitative",
            showarrow=False,
            font={"size": 14, "color": text_color},
            xanchor="right",
            yanchor="middle",
        )

    # Configure layout
    left_margin = 220 if show_label else 10
    fig.update_layout(
        width=num_colors * (1 + GAP) * BOX_SIZE + left_margin + 40,
        height=140,
        margin={"l": left_margin, "r": 10, "t": 20, "b": 20},
        xaxis={"visible": False, "range": [-1.5, num_colors * (1 + GAP) - 0.5]},
        yaxis={"visible": False, "range": [-0.6, 0.6], "scaleanchor": "x", "scaleratio": 1},
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font={"color": text_color, "size": 12},
        showlegend=False,
    )

    return fig


def generate_qualitative_palette_image(output_path, theme="light"):
    """Generate qualitative palette reference image with discrete boxes."""
    qualitative = palettes.qualitative
    fig = make_qualitative_palette(qualitative, show_label=True, theme=theme)
    _save_image(fig, output_path)


def generate_palettes_image(output_path, theme="light"):
    """Generate palettes reference image with continuous gradients (excluding qualitative)."""
    # Get all palettes except qualitative
    palette_groups = {name: getattr(palettes, name) for name in vars(palettes) if name != "qualitative"}

    fig = make_palette_gradients(palette_groups, show_group_names=True, theme=theme)
    _save_image(fig, output_path)


def main():
    """Generate theme reference images."""
    output_dir = Path(__file__).parent.parent / "docs" / "assets" / "user_guides" / "themes"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating theme reference images...")  # noqa: T201
    generate_colors_image(output_dir / "colors.png")

    # Generate light theme palette images
    generate_qualitative_palette_image(output_dir / "palette_qualitative_light.png", theme="light")
    generate_palettes_image(output_dir / "palettes_light.png", theme="light")

    # Generate dark theme palette images
    generate_qualitative_palette_image(output_dir / "palette_qualitative_dark.png", theme="dark")
    generate_palettes_image(output_dir / "palettes_dark.png", theme="dark")

    print("\n✅ All theme images generated successfully!")  # noqa: T201


if __name__ == "__main__":
    main()
