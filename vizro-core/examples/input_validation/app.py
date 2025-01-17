"""Validation of inputs example"""

from datetime import datetime
import pandas as pd

import vizro.models as vm
import vizro.plotly.express as px

from vizro import Vizro
from vizro.managers import data_manager
from vizro.tables import dash_ag_grid
from vizro.models.types import capture

from custom_components import InitiallyHiddenCard, LoadingSpinner, NumberInput, ValidationComponent, ContainerWithLine
from vizro.models._components.form._user_input import UserInput

from dash import clientside_callback, exceptions, Input, Output
from pathlib import Path

# ============================== CONSTANTS ==============================
DF_COLUMNS = ["Item", "Discount", "Rebate", "Final Sales", "Profit", "Offer Name"]
MAIN_DATA_RELATIVE_PATH = "data.csv"


# ============================== Data Manager ==============================
# More about data_manager and dynamic data in Vizro:
# https://vizro.readthedocs.io/en/stable/pages/user-guides/data/#dynamic-data
def load_main_data(file_path=None):
    file_path = file_path or Path.cwd().joinpath(MAIN_DATA_RELATIVE_PATH)

    try:
        return pd.read_csv(file_path)
    except:
        return pd.DataFrame(columns=DF_COLUMNS)


def load_main_data_sorted():
    return load_main_data().sort_values("Profit", ascending=False)


cost_price_data_frame = pd.DataFrame({
    "Item": ["Apple", "Banana", "Cherry"],
    "Cost": [1, 2, 3],
    "Price": [40, 45, 50]
})

data_manager["load_main_data_key"] = load_main_data
data_manager["load_main_data_sorted_key"] = load_main_data_sorted


# ============================== Actions ==============================
@capture("action")
def run_pipeline_action(button_n_clicks: int, item: str, discount: float, rebate: float, offer_name: str):
    if button_n_clicks is None:
        raise exceptions.PreventUpdate

    output_validation_message = ""

    # Read main data
    df = load_main_data()

    # TODO: Remove this sleep statement in production.
    # Artificial delay to simulate a long-running script
    from time import sleep
    sleep(1)

    if None in [item, discount, rebate, offer_name]:
        output_validation_message = "Please properly fill all the fields."
    elif item == "Apple" and discount > 0.9:
        output_validation_message = "Discount for Apple must be less than 0.9."
    elif offer_name in df["Offer Name"].values:
        output_validation_message = f"An offer named '{offer_name}' already exists. Please try a different name."

    # After validation check, if there is an error, return the error message and hide the navigation card.
    if output_validation_message:
        return output_validation_message, "", {"display": "none"}

    # Get item cost and price
    item_cost = float(cost_price_data_frame[cost_price_data_frame['Item'] == item]['Cost'].iloc[0])
    item_price = float(cost_price_data_frame[cost_price_data_frame['Item'] == item]['Price'].iloc[0])

    # Calculate results
    final_sales = item_price * discount - rebate
    profit = final_sales - item_cost

    # Append new row to the dataframe
    df.loc[len(df.index)] = [item, discount, rebate, final_sales, profit, offer_name]

    # Write data back to the file
    df.to_csv(MAIN_DATA_RELATIVE_PATH, index=False)

    return f"Success! Your calculations for offer '{offer_name}' are ready. ({datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')})", "", {"display": "block"}


# ============================== Page Create New Offer ==============================

# Enable the custom components in the Vizro Container
vm.Container.add_type("components", ValidationComponent)
vm.Container.add_type("components", LoadingSpinner)
vm.Container.add_type("components", UserInput)
vm.Page.add_type("components", ContainerWithLine)
ContainerWithLine.add_type("components", InitiallyHiddenCard)
ContainerWithLine.add_type("components", LoadingSpinner)

page_create_new_offer = vm.Page(
    title="Offer Analysis Creation",
    layout=vm.Layout(grid=[
        [1, 1, 2],
        [1, 1, 2],
        [0, 0, 3],
        [0, 0, 3],
        [0, 0, 3],
    ]),
    components=[
        vm.Container(
            title="Create New Offer",
            layout=vm.Layout(grid=[
                [0, -1],
                [1, 2],
                [3, 4],
                [5, 6],
            ]),
            components=[
                ValidationComponent(
                    id="offer-name-input",
                    wrapped_component=UserInput(
                        title="Offer Name:",
                        placeholder="Enter offer name",
                    ),
                ),
                ValidationComponent(
                    id="item-input",
                    wrapped_component=vm.Dropdown(
                        title="Choose an item:",
                        options=cost_price_data_frame["Item"].tolist(),
                        multi=False,
                    )
                ),
                ValidationComponent(
                    id="discount-input",
                    wrapped_component=NumberInput(
                        title="Discount:",
                        min=0.8,
                        max=1,
                        step=0.01,
                        value=0.9,
                    ),
                ),
                ValidationComponent(
                    id="rebate-input",
                    wrapped_component=NumberInput(
                        title="Rebate ($):",
                        min=0,
                        max=5,
                        step=0.1,
                        value=1,
                    ),
                ),
                ValidationComponent(
                    id="dummy-input1",
                    wrapped_component=vm.Dropdown(
                        title="(Placeholder) Dummy Input 1:",
                        options=[
                            {"label": "Option 1", "value": "1"},
                            {"label": "Option 2", "value": "2"},
                            {"label": "option 3", "value": "3"},
                        ],
                        multi=False,
                    )
                ),
                ValidationComponent(
                    id="dummy-input2",
                    wrapped_component=UserInput(
                        title="(Placeholder) Dummy Input 2:",
                        placeholder="Placeholder text",
                    ),
                ),
                ValidationComponent(
                    id="dummy-input3",
                    wrapped_component=UserInput(
                        title="(Placeholder) Dummy Input 3:",
                        placeholder="Placeholder text",
                    ),
                ),
            ]
        ),
        vm.AgGrid(
            title="Reference Data",
            figure=dash_ag_grid(data_frame=cost_price_data_frame, columnSize="sizeToFit")
        ),
        ContainerWithLine(
            title="Run Pipeline",
            id="run-pipeline-container",
            layout=vm.Layout(grid=[
                [0, 1],
            ]),
            components=[
                vm.Button(
                    id="run-pipeline-submit-button",
                    text="Calculate Results",
                    actions=[
                        vm.Action(
                            function=run_pipeline_action(),
                            inputs=[
                                "run-pipeline-submit-button.n_clicks",
                                "item-input.value",
                                "discount-input.value",
                                "rebate-input.value",
                                "offer-name-input.value",
                            ],
                            outputs=[
                                "run-pipeline-message-card.children",
                                "run-pipeline-loading-spinner.children",
                                "run-pipeline-nav-card-outer-div.style",
                            ],
                        ),
                    ]
                ),
                LoadingSpinner(id="run-pipeline-loading-spinner"),
            ]
        ),
        ContainerWithLine(
            title="Run Status",
            id="run-pipeline-status-container",
            layout=vm.Layout(grid=[
                [0,],
                [0,],
                [1,]
            ]),
            components=[
                vm.Card(id="run-pipeline-message-card", text=""),
                InitiallyHiddenCard(
                    id=f"run-pipeline-nav-card",
                    href="offer-analysis-results",
                    text=(
                        """
                            ### Click Here  &#10132;

                            to see the results on the offer-analysis-results.
                        """
                    ),
                )
            ],
        ),
    ],
)

# ============================== Validation ==============================

clientside_callback(
    """
    function validate_discount_input(input_value) {
      const value = parseFloat(input_value);

      if (value < 0.8 || value > 1 || (value * 100) % 1 !== 0) {
        return "Enter a discount value from 0.80 to 1.00 (0.01 increments).";
      }
      return "";
    }
    """,
    Output("discount-input-error-id", "children"),
    Input("discount-input", "value"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function validate__input(input_value) {
      const value = parseFloat(input_value);

      if (value < 0 || value > 5 || (value * 10) % 1 !== 0) {
        return "Enter a rebate value between 0-5 with one decimal place.";
      }
      return "";
    }
    """,
    Output("rebate-input-error-id", "children"),
    Input("rebate-input", "value"),
    prevent_initial_call=True,
)

clientside_callback(
    """
    function validate_offer_name_input(input_value) {
      const value = input_value.trim(); // Remove leading/trailing whitespace

      if (value === '') {
        return "The input cannot be empty. Please enter some text.";
      }
      return "";
    }
    """,
    Output("offer-name-input-error-id", "children"),
    Input("offer-name-input", "value"),
    prevent_initial_call=True,
)

# ============================== Page Results ==============================

page_results = vm.Page(
    title="Offer Analysis Results",
    layout=vm.Layout(grid=[
        [0, 1],
        [2, 2],
    ]),
    components=[
        vm.Graph(
            title="Profit by offer",
            figure=px.bar(
                data_frame="load_main_data_sorted_key",
                y="Offer Name",
                x="Profit",
                color="Item",
                orientation="h",
            )
        ),
        vm.Graph(
            title="Offer by Item",
            figure=px.pie(
                data_frame="load_main_data_sorted_key",
                names="Item",
            )
        ),
        vm.AgGrid(
            title="Offer Analysis Data",
            figure=dash_ag_grid(
                data_frame="load_main_data_key",
            )
        ),
    ],
    controls=[
        vm.Filter(column="Item", selector=vm.Dropdown(options=["Apple", "Banana", "Cherry"], multi=True, title="Select Item")),
        vm.Filter(column="Profit", selector=vm.RangeSlider(step=0.01, marks=None, min=0, max=100, title="Select Profit Range")),
    ]
)

# ============================== Dashboard ==============================

dashboard = vm.Dashboard(pages=[
    page_create_new_offer,
    page_results,
])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
