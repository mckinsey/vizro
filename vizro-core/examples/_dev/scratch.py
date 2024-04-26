import numpy as np
import pandas as pd
from utils._helper import clean_data_and_add_columns
df_complaints = pd.read_csv("data/Financial Consumer Complaints.csv")
df_complaints = clean_data_and_add_columns(df_complaints)
print(df_complaints.columns)
