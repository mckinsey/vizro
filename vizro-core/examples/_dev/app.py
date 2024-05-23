"""Dev app to try things out."""

import numpy as np
import vizro.models as vm
import vizro.plotly.express as px
from vizro import Vizro
from vizro.tables import dash_data_table

df = px.data.gapminder()

dropdown_column = "Label"
dropdown_options = ["-- A --", "-- B --", "-- C --"]

# Add a 'Label' column to the data where options are randomly selected between 'A', 'B', 'C'
df[dropdown_column] = np.random.choice(dropdown_options, size=len(df))

# Drop the 'iso_alpha' and 'iso_num' columns
df.drop(["iso_alpha", "iso_num"], axis=1, inplace=True)


page = vm.Page(
    title="Table Page",
    components=[
        vm.Table(
            title="Table",
            figure=dash_data_table(
                data_frame=df,
                columns=[
                    {"name": i, "id": i, "presentation": "dropdown"} if i == dropdown_column else {"name": i, "id": i}
                    for i in df.columns
                ],
                editable=True,
                dropdown={
                    dropdown_column: {
                        "options": [{"label": i, "value": i} for i in dropdown_options],
                        "clearable": False,
                    },
                },
            ),
        ),
    ],
    controls=[vm.Filter(column="continent")],
)

dashboard = vm.Dashboard(pages=[page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()
