import pandas as pd
import numpy as np

# Seed for reproducibility
np.random.seed(42)

# ---------------------------
# Industry Vertical Data
# ---------------------------
industry_verticals = ["Dairy", "Bakery", "Culinary", "Bars & Confectionary", "Industrial", "Beverages"]

industry_data = pd.DataFrame({
    "Industry": industry_verticals,
    "2024_Revenue": np.random.randint(15, 45, size=len(industry_verticals)),
    "Opportunity": np.random.randint(10, 35, size=len(industry_verticals)),
})

industry_data["Total"] = industry_data["2024_Revenue"] + industry_data["Opportunity"]
industry_data["Estimated_Share"] = [f"{low}-{high}%" for low, high in zip(np.random.randint(30, 70, len(industry_verticals)),
                                                                         np.random.randint(60, 85, len(industry_verticals)))]

# ---------------------------
# Product Category Data
# ---------------------------
product_categories = ["Protein Solutions", "Emulsifiers & Sweeteners", "Cellulosics & Food Protection",
                      "Core Texturants", "Systems", "Savory Solutions", "Inclusions"]

product_data = pd.DataFrame({
    "Product": product_categories,
    "2024_Revenue": np.random.randint(2, 65, size=len(product_categories)),
    "Opportunity": np.random.randint(2, 40, size=len(product_categories)),
})

product_data["Total"] = product_data["2024_Revenue"] + product_data["Opportunity"]

# ---------------------------
# Summary Info
# ---------------------------
summary = {
    "Number_of_Leads": np.random.randint(500, 1000),
    "Serviceable_Available_Market_M": f"${product_data['Total'].sum()}M"
}

# Display results
print("Industry Vertical Data:\n", industry_data, "\n")
print("Product Category Data:\n", product_data, "\n")
print("Summary:\n", summary)
