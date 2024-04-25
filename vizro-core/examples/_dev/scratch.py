import pandas as pd


df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")

print(df_complaints["Company response to consumer"].unique())

df_complaints['Date Received'] = pd.to_datetime(df_complaints['Date Received'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints['Date Sumbited'] = pd.to_datetime(df_complaints['Date Sumbited'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
df_complaints.rename(columns={"Date Sumbited": "Date Submitted"}, inplace=True)

df_agg = df_complaints.groupby(["Issue"]).aggregate({"Complaint ID": "count"}).sort_values(by="Complaint ID", ascending=False).reset_index()
top_n = df_agg.head(10)

# Sum counts for remaining issues
other_sum = df_agg.iloc[10:].sum()
other_row = pd.DataFrame({'Issue': ['Other'], 'Complaint ID': [other_sum['Complaint ID']]})

# Append to top_n dataframe
top_n = pd.concat([top_n, other_row], ignore_index=True)

print(top_n.head(12))
