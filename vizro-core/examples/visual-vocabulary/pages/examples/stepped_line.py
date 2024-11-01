import pandas as pd
import vizro.plotly.express as px

stepped_line_data = pd.DataFrame(
    {
        "year": [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
        "rate": [0.10, 0.12, 0.15, 0.13, 0.14, 0.13, 0.14, 0.16, 0.15],
    }
)

fig = px.line(data_frame=stepped_line_data, x="year", y="rate", line_shape="vh")
