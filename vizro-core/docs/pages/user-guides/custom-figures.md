# How to create custom Figures

If the existing figure function from [`vizro.figures`](../API-reference/figure-callables.md) do not serve your purpose,
there is always the option to create a [custom Figure](custom-figures.md).

For this, similar to how one would create a [custom chart](../user-guides/custom-charts.md), do the following:

- Define a function that returns a `Dash` component.
- Decorate it with the `@capture("figure")` respectively.
- The function must accept a `data_frame` argument (of type `pandas.DataFrame`).
- The figure should be derived from and require only one `pandas.DataFrame` (for example, any further dataframes added through other arguments will not react to dashboard components such as `Filter`).

The example below shows how to create a custom figure — a list of cards created from a `pandas.DataFrame` where the
number of cards displayed dynamically adjusts based on a `vm.Parameter`.

```python

??? example "Custom Figure - Dynamic number of cards"
    === "app.py"
        ```py
        from typing import List, Optional

        import pandas as pd
        import vizro.models as vm
        from vizro import Vizro
        from vizro.models.types import capture
        
        df = pd.DataFrame(
            {
                "text": [
                    "Lorem ipsum dolor sit amet, consetetur sadipscing no sea elitr sed diam nonumy.",
                    "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
                    "Sed diam voluptua. At vero eos et accusam et justo no duo dolores et ea rebum.",
                    "Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
                    "Lorem ipsum dolor sit amet, consetetur sadipscing no sea est elitr dolor sit amet.",
                    "Sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat.",
                ]
                * 2
            }
        )
        
        
        @capture("figure")
        def multiple_cards(data_frame: pd.DataFrame, n_rows: Optional[int] = 1) -> List[vm.Card]:
            """Creates a list with a variable number of `vm.Card` components from the provided data_frame.
        
            Args:
                data_frame: Data frame containing the data.
                n_rows: Number of rows to use from the data_frame. Defaults to 1.
        
            Returns:
                List of dbc.Card objects generated from the data.
        
            """
            texts = data_frame.head(n_rows)["text"]
            return [vm.Card(text=f"### Card #{i+1}\n{text}").build() for i, text in enumerate(texts)]
        
        
        page = vm.Page(
            title="Page with variable number of cards",
            # This is where you use the multiple_cards function you wrote:
            components=[vm.Figure(id="my-figure", figure=multiple_cards(data_frame=df))],
            controls=[
                vm.Parameter(
                    targets=["my-figure.n_rows"],
                    selector=vm.Slider(min=2, max=12, step=2, value=8, title="Number of cards to display"),
                ),
            ],
        )
        
        dashboard = vm.Dashboard(pages=[page])
        Vizro().build(dashboard).run()
        ```
    === "css"
        ```css
        #my-figure {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }
        
        .card {
          height: 210px;
          width: 240px;
        }
        
        .figure-container {
          height: unset;
          width: unset;
        }
        ```
    === "app.yaml"
        ```yaml
        # Custom figures are currently only possible via python configuration
        ```
    === "Result"
        [![CustomFigure]][CustomFigure]

    [CustomFigure]: ../../assets/user_guides/figure/custom_figure.png
