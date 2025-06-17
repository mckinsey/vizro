import dash
from dash import Dash, dcc, html
from watchpoints import watch

# watch(dash._callback.GLOBAL_CALLBACK_LIST)
# watch(dash._callback.GLOBAL_CALLBACK_MAP)
watch(dash._callback.GLOBAL_INLINE_SCRIPTS)
# watch(dash._pages.PAGE_REGISTRY)
# watch(dash._pages.CONFIG)
# watch(dash._pages.CONFIG.__dict__)

app = Dash(__name__, use_pages=True)


from pages.callbacks import Callbacks

Callbacks.define_callbacks()

app.layout = html.Div(
    [
        html.H1("Multi-page app with Dash Pages"),
        html.Div(
            [
                html.Div(dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"]))
                for page in dash.page_registry.values()
            ]
        ),
        dash.page_container,
    ]
)


if __name__ == "__main__":
    app.run(debug=True)
