# Refine a generated dashboard
This guide shows you how to make improvements to a Vizro-AI generated dashboard.

Vizro-AI can follow complex user requirements well and generate high-quality dashboards, but the nature of LLMs means that generated dashboards are not always an exact match for user expectations. One option is to refine the request prompt and re-run Vizro-AI, but alternatively, you can iterate the code manually to achieve the desired result.

The following example shows how to use Vizro-AI to generate a Vizro dashboard, and then retrieve the Vizro code for refinement.

## 1. Prepare the data and build the user prompt


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

## 2. Generate and render the dashboard

Submit the data and prompt to Vizro-AI's `dashboard()` function:

```py
dashboard_elements = vizro_ai.dashboard([df], user_question, return_elements=True)
```

Once Vizro-AI finishes dashboard generation, you can now render the dashboard:

!!! example "Generated dashboard"

    === "Code"
        ```py
        Vizro().build(dashboard_elements.dashboard).run()
        ```

    === "Result"
        [![VizroAIDashboardPage1]][VizroAIDashboardPage1]


    [VizroAIDashboardPage1]: ../../assets/user_guides/dashboard/dashboard2_page1.png

## Retrieve the Python code of the dashboard

You can retrieve the code for the dashboard as follows:


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

<!-- TO DO -->
<!--
* How to modify? Need an example
* Return elements, which gives you access to a) code b) dashboard object ?? -->
