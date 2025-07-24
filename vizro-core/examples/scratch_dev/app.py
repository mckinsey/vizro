# Vizro is an open-source toolkit for creating modular data visualization applications.
# check out https://github.com/mckinsey/vizro for more info about Vizro
# and checkout https://vizro.readthedocs.io/en/stable/ for documentation.

import pandas as pd
import numpy as np
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
from vizro.tables import dash_ag_grid

# Create a fake dataset with many columns and longer values
np.random.seed(42)

# Generate data with many columns
n_rows = 50
n_cols = 25

# Create column names that are long enough to get truncated
column_names = [
    "Very_Long_Column_Name_1",
    "Extended_Data_Field_2",
    "Comprehensive_Metric_3",
    "Detailed_Information_4",
    "Complex_Calculation_5",
    "Advanced_Analytics_6",
    "Business_Intelligence_7",
    "Performance_Indicator_8",
    "Statistical_Measure_9",
    "Quantitative_Analysis_10",
    "Operational_Efficiency_11",
    "Customer_Satisfaction_12",
    "Revenue_Generation_13",
    "Cost_Optimization_14",
    "Quality_Assessment_15",
    "Risk_Management_16",
    "Strategic_Planning_17",
    "Market_Research_18",
    "Product_Development_19",
    "Sales_Performance_20",
    "Marketing_Campaign_21",
    "Financial_Reporting_22",
    "Compliance_Monitoring_23",
    "Sustainability_Index_24",
    "Innovation_Score_25",
]

column_names_2 = [
    "Very_Long_Column_Name_1",
    "Extended_Data_Field_2",
    "Comprehensive_Metric_3",
]

# Generate data with longer values that could get truncated
data = {}
for i, col in enumerate(column_names):
    if i % 5 == 0:  # String columns with long values
        data[col] = [f"Long_Text_Value_{j}_{np.random.randint(1000, 9999)}" for j in range(n_rows)]
    elif i % 5 == 1:  # Float columns with many decimal places
        data[col] = np.round(np.random.uniform(1000, 9999, n_rows), 4)
    elif i % 5 == 2:  # Integer columns with large numbers
        data[col] = np.random.randint(10000, 99999, n_rows)
    elif i % 5 == 3:  # Categorical data with long category names
        categories = [
            "Category_A_Very_Long_Name",
            "Category_B_Extended_Label",
            "Category_C_Comprehensive_Description",
            "Category_D_Detailed_Classification",
        ]
        data[col] = np.random.choice(categories, n_rows)
    else:  # Mixed data types
        data[col] = [
            f"Data_{j}_{np.random.randint(100, 999)}_{np.random.choice(['Alpha', 'Beta', 'Gamma'])}"
            for j in range(n_rows)
        ]


def generate_column_data(column_names):
    """
    Generate data for columns with different data types based on column index.

    Args:
        data (dict): Dictionary to store generated data
        column_names (list): List of column names
        n_rows (int): Number of rows to generate
    """
    data = {}

    for i, col in enumerate(column_names):
        if i % 5 == 0:  # String columns with long values
            data[col] = [f"Long_Text_Value_{j}_{np.random.randint(1000, 9999)}" for j in range(n_rows)]
        elif i % 5 == 1:  # Float columns with many decimal places
            data[col] = np.round(np.random.uniform(1000, 9999, n_rows), 4)
        elif i % 5 == 2:  # Integer columns with large numbers
            data[col] = np.random.randint(10000, 99999, n_rows)
        elif i % 5 == 3:  # Categorical data with long category names
            categories = [
                "Category_A_Very_Long_Name",
                "Category_B_Extended_Label",
                "Category_C_Comprehensive_Description",
                "Category_D_Detailed_Classification",
            ]
            data[col] = np.random.choice(categories, n_rows)
        else:  # Mixed data types
            data[col] = [
                f"Data_{j}_{np.random.randint(100, 999)}_{np.random.choice(['Alpha', 'Beta', 'Gamma'])}"
                for j in range(n_rows)
            ]


# Create DataFrame
tips = pd.DataFrame(data)
tips_small = pd.DataFrame({col: data[col] for col in column_names_2})

page0 = vm.Page(
    title="Default columnSize - sizeToFit",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips,
                            )
                        )
                    ],
                )
            ]
        )
    ],
)


page1 = vm.Page(
    title="Default columnSize - sizeToFit - small dataset",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips_small,
                            )
                        )
                    ],
                )
            ]
        )
    ],
)


page2 = vm.Page(
    title="responsiveSizeToFit",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips,
                                columnSize="responsiveSizeToFit",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)

page3 = vm.Page(
    title="responsiveSizeToFit - small dataset",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips_small,
                                columnSize="responsiveSizeToFit",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)


page4 = vm.Page(
    title="autoSize",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips,
                                columnSize="autoSize",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)

page5 = vm.Page(
    title="autoSize - small dataset",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips_small,
                                columnSize="autoSize",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)


page6 = vm.Page(
    title="sizeToFit",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips,
                                columnSize="sizeToFit",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)

page7 = vm.Page(
    title="sizeToFit - small dataset",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips_small,
                                # columnSize="responsiveSizeToFit",
                                # columnSize="autoSize",
                                columnSize="sizeToFit",
                            )
                        )
                    ],
                )
            ]
        )
    ],
)


page8 = vm.Page(
    title="No columnSize",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips,
                                columnSize=None,
                            )
                        )
                    ],
                )
            ]
        )
    ],
)

page9 = vm.Page(
    title="No columnSize - small dataset",
    components=[
        vm.Tabs(
            tabs=[
                vm.Container(
                    title="View Data",
                    components=[
                        vm.AgGrid(
                            figure=dash_ag_grid(
                                tips_small,
                                # columnSize="responsiveSizeToFit",
                                # columnSize="autoSize",
                                columnSize=None,
                            )
                        )
                    ],
                )
            ]
        )
    ],
)

dashboard = vm.Dashboard(pages=[page0, page1, page2, page3, page4, page5, page6, page7, page8, page9])


if __name__ == "__main__":
    Vizro().build(dashboard).run()
