import pandas as pd

data_frame = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str}
)

data_frame.loc[1::2, "unemp"] *= -1
print(data_frame)
