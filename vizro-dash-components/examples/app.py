"""Multi-page Dash app showcasing vizro-dash-components."""

import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, callback, html, page_container, page_registry

app = Dash(__name__, use_pages=True)

_OTHER_MODULES = {"cascader_vs_dropdown", "cascader_stress_test"}


def _components_pages():
    return [p for p in page_registry.values() if p["module"].split(".")[-1] not in _OTHER_MODULES]


def _other_pages():
    return [p for p in page_registry.values() if p["module"].split(".")[-1] in _OTHER_MODULES]


def _page_anchor(page):
    return dmc.Anchor(
        dmc.Button(page["name"], variant="subtle", size="sm"),
        href=page["relative_path"],
        underline="never",
    )


def _navbar_content():
    components = [_page_anchor(p) for p in _components_pages()]
    other = [_page_anchor(p) for p in _other_pages()]
    blocks = [dmc.Stack(components, gap="xs")]
    if other:
        blocks.extend(
            [
                dmc.Divider(my="sm"),
                dmc.Stack(other, gap="xs"),
            ]
        )
    return dmc.Stack(blocks, gap=0, align="stretch")


app.layout = dmc.MantineProvider(
    dmc.AppShell(
        [
            dmc.AppShellHeader(
                dmc.Group(
                    [
                        dmc.Group(
                            [
                                dmc.Burger(id="shell-burger", size="sm", hiddenFrom="sm", opened=False),
                                dmc.Title("vizro-dash-components", order=1),
                            ],
                            gap="md",
                        ),
                        dmc.ColorSchemeToggle(
                            lightIcon=html.Span("☀", style={"fontSize": 20}),
                            darkIcon=html.Span("☾", style={"fontSize": 20}),
                            size="lg",
                        ),
                    ],
                    justify="space-between",
                    style={"flex": 1},
                    h="100%",
                    px="md",
                ),
            ),
            dmc.AppShellNavbar(
                id="shell-navbar",
                children=_navbar_content(),
                p="md",
            ),
            dmc.AppShellMain(dmc.Container(page_container, size="lg", py="xl")),
        ],
        id="appshell",
        header={"height": 60},
        padding="lg",
        navbar={
            "width": 280,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
    ),
    defaultColorScheme="light",
)


@callback(
    Output("appshell", "navbar"),
    Input("shell-burger", "opened"),
    State("appshell", "navbar"),
)
def _toggle_shell_navbar(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


if __name__ == "__main__":
    app.run(debug=True)
