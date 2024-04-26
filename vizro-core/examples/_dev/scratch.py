import pandas as pd


df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")

print(df_complaints["Company response to consumer"].unique())

df_complaints['Date Received'] = pd.to_datetime(df_complaints['Date Received'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints['Date Sumbited'] = pd.to_datetime(df_complaints['Date Sumbited'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints.rename(columns={"Date Sumbited": "Date Submitted"}, inplace=True)



# Group by year and month, and calculate the sum for the numeric column
df_complaints['Date Received YY-MM'] = pd.to_datetime(df_complaints['Date Received'], format='%Y-%m-%d').dt.strftime('%Y-%m')
result = df_complaints.groupby(df_complaints['Date Received YY-MM']).aggregate({"Complaint ID": "count"}).reset_index()
