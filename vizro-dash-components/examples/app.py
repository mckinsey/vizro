"""Multi-page Dash app showcasing vizro-dash-components."""

import dash_mantine_components as dmc
from dash import Dash, dcc, html, page_container, page_registry

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, pages_folder="pages")

app.layout = dmc.MantineProvider(
    dmc.Container(
        [
            dmc.Group(
                [
                    dmc.Title("vizro-dash-components", order=1),
                    dmc.Group(
                        [
                            dcc.Link(
                                dmc.Button(page["name"], variant="subtle"),
                                href=page["relative_path"],
                            )
                            for page in page_registry.values()
                            if page["path"] != "/"
                        ]
                    ),
                    dmc.ColorSchemeToggle(
                        lightIcon=html.Span("☀", style={"fontSize": 20}),
                        darkIcon=html.Span("☾", style={"fontSize": 20}),
                        size="lg",
                    ),
                ],
                justify="space-between",
                align="center",
                mb="md",
            ),
            dmc.Divider(mb="xl"),
            page_container,
        ],
        size="lg",
        py="xl",
    ),
    defaultColorScheme="light",
)

if __name__ == "__main__":
    app.run()
