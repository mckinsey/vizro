# How to render Dash components in responses

This guide shows you how to return rich content — charts, tables, alerts — from a chat action instead of plain text.

A [`ChatAction`][vizro_experimental.chat.ChatAction]'s `generate_response` can return any Dash component (or any object Plotly's JSON encoder can serialise). The component is rendered directly inside the assistant bubble.

## Return a chart

Return a [`dcc.Graph`][dash.dcc.Graph] (or any other Dash element) and the chat renders it inline.

!!! example "Chat that replies with a chart"

    ```python
    import vizro.models as vm
    import vizro.plotly.express as px
    from dash import dcc
    from vizro import Vizro
    from vizro_experimental.chat import Chat, ChatAction, Message


    class IrisChartChat(ChatAction):
        def generate_response(self, messages: list[Message]) -> dcc.Graph:
            df = px.data.iris()
            figure = px.scatter(df, x="sepal_width", y="sepal_length", color="species")
            return dcc.Graph(figure=figure)


    vm.Page.add_type("components", Chat)

    page = vm.Page(
        title="Mixed content chat",
        components=[Chat(actions=[IrisChartChat()])],
    )

    Vizro().build(vm.Dashboard(pages=[page])).run()
    ```

## Return a layout that mixes text, tables, and charts

You can return any Dash element tree. The example below combines Markdown, a Mantine table, and a Plotly chart in a single response.

!!! example "Component showcase"

    ```python
    import dash_mantine_components as dmc
    import vizro.plotly.express as px
    from dash import dcc, html
    from vizro_experimental.chat import ChatAction, Message


    class Showcase(ChatAction):
        def generate_response(self, messages: list[Message]) -> html.Div:
            prompt = messages[-1]["content"]
            figure = px.scatter(px.data.iris(), x="sepal_width", y="sepal_length", color="species")

            return html.Div(
                [
                    dcc.Markdown(f"**You said:** {prompt}"),
                    dmc.Table(
                        striped=True,
                        withTableBorder=True,
                        data={
                            "head": ["Feature", "Status"],
                            "body": [
                                ["Streaming", "Supported"],
                                ["File upload", "Supported"],
                                ["Code highlight", "Supported"],
                            ],
                        },
                    ),
                    dcc.Graph(figure=figure),
                ]
            )
    ```

## Streaming caveat

[`StreamingChatAction`][vizro_experimental.chat.StreamingChatAction] only streams strings. To return a Dash component, use the synchronous `ChatAction` instead.

## What's next

- [Add example questions](example-questions.md) — guide users with predefined prompts.
- [Combine features](combine-features.md) — pair rich responses with file upload and example questions.
