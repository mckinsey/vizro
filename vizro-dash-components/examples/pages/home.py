"""Home page with links to component showcases."""

# ruff: noqa: D103

import dash
import dash_mantine_components as dmc
from dash import dcc, html, page_registry

dash.register_page(__name__, path="/", name="Home", order=-1)


def layout():
    pages = [p for p in page_registry.values() if p["path"] != "/"]
    return html.Div(
        [
            dmc.Text(
                "Select a component showcase from the navigation above, or jump to one below:",
                c="dimmed",
                size="lg",
                mb="lg",
            ),
            dmc.Stack(
                [
                    dcc.Link(dmc.Button(page["name"], variant="light", size="lg", fullWidth=False), href=page["path"])
                    for page in pages
                ],
            ),
        ]
    )
