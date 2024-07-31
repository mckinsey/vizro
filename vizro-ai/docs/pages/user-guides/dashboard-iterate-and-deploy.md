# How to update and reuse the Vizro-AI generated dashboard
This guide shows you how to refine a Vizro-AI generated dashboard.

While Vizro-AI can follow complex user requirements well and generate high-quality dashboards, due to the nature of LLMs, the generated dashboards often approximately match user expectations but may not be exact. Besides refining the user prompt and rerunning Vizro-AI, you can also extract the code and iterate manually to achieve the desired result.



<!-- TO DO -->
<!--
can generate a multi-page dashboard including the following features:

- Vizro components including Graph, AgGrid (basic), and Card
- Vizro Filters including Dropdown, Checklist, Dropdown, RadioItems, RangeSlider, Slider, DatePicker(in development)
- Vizro Layout
- Multi-dataframe and multi-page support
-->
<!-- Write how to set up as per tutorial and use the prompt below to generate a dashboard -->
<!-- you get the dashboard object, which you can a) render like xxx, b) modify like xx c) xxx alternatively you can return elements, which gives you access to a) code b) dashboard object -->

## Prepare the data and user prompt
```py
import vizro.plotly.express as px

df = px.data.tips()

user_question = """
Create a one-page dashboard layout with the following components:

1. Card:
   - Position: Left of the page
   - Size: Takes up 1/4 of the total page width
   - Content: Display the text "This is Tips dataset"

2. Table:
   - Position: Right of the card
   - Size: Takes up the remaining 3/4 of the page width
   - Content: Display the Tips dataset
"""
```

## Generate and launch the dashboard
```py
dashboard_elements = vizro_ai.dashboard([df], user_question, return_elements=True)
```
This will trigger the dashboard building process. Once Vizro-AI finishes the dashboard generation process, you can now launch the dashboard.

!!! example "Generated dashboard"

    === "Code"
        ```py
        Vizro().build(dashboard_elements.dashboard).run()
        ```

    === "Result"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]


    [VizroAIDashboardPage1]: ../../assets/user_guides/dashboard/dashboard2_page1.png

## Retrieve the Python code of the dashboard
!!! example "View dashboard code"

    === "Code"
        ```py
        print(dashboard_elements.code)
        ```

    === "Result"
        ```py
        ######## Module Imports ##########
        from vizro import Vizro
        from vizro.managers import data_manager
        from vizro.models.types import capture
        import vizro.models as vm
        from vizro.tables import dash_ag_grid

        ########## Data Imports ##########
        #####!!! UNCOMMENT BELOW !!!######
        # data_manager["restaurant_bills"] = ===> Fill in here <===

        ###### Callable definitions ######


        ########## Object code ###########
        dashboard = vm.Dashboard(
            pages=[
                vm.Page(
                    id="Tips Data Visualization",
                    components=[
                        vm.Card(
                            id="tips_card_tips_data_visualization",
                            type="card",
                            text="This is Tips dataset",
                            href="",
                        ),
                        vm.AgGrid(
                            id="tips_table_tips_data_visualization",
                            figure=dash_ag_grid(data_frame="restaurant_bills"),
                        ),
                    ],
                    title="Tips Data Visualization",
                    layout=vm.Layout(grid=[[0, 1, 1, 1]]),
                    controls=[],
                )
            ],
            title="Tips Dataset Overview",
        )
        ```
