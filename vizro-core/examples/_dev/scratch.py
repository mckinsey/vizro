import pandas as pd


df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")

print(df_complaints["Company response to consumer"].unique())

df_complaints['Date Received'] = pd.to_datetime(df_complaints['Date Received'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints['Date Sumbited'] = pd.to_datetime(df_complaints['Date Sumbited'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints.rename(columns={"Date Sumbited": "Date Submitted"}, inplace=True)

rain =  "![alt text: rain](https://www.ag-grid.com/example-assets/weather/rain.png)"
sun = "![alt text: sun](https://www.ag-grid.com/example-assets/weather/sun.png)"

df_complaints["Timely response?"] = df_complaints["Timely response?"].apply(lambda x: rain if x == 'No' else sun)
