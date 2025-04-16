# /// script
# dependencies = [
#   "pyarrow",
#   "fastparquet",
# ]
# ///

import pandas as pd


def select_and_save_columns(csv_file_path: str, output_csv_path: str) -> None:
    """
    Read a CSV file, select specific columns, and save as a new CSV file.

    Args:
        csv_file_path (str): Path to the input CSV file
        output_csv_path (str): Path where the filtered CSV file will be saved

    Returns:
        None
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Select the specified columns
        columns_to_keep = [
            "in.sqft",
            "in.county_name",
            "in.electric_vehicle",
            "in.has_pv",
            "in.income",
            "in.occupants",
            "in.state",
            "in.tenure",
            "in.vintage",
            "out.bills.all_fuels.usd",
            "out.bills.electricity.usd",
            "out.bills.fuel_oil.usd",
            "out.bills.natural_gas.usd",
            "out.bills.propane.usd",
            "out.energy_burden.percentage",
        ]

        filtered_df = df[columns_to_keep]

        # Save as CSV
        filtered_df.to_csv(output_csv_path, index=False)

        print(f"Successfully filtered and saved {csv_file_path} to {output_csv_path}")
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")


# Process the specific file
csv_path = "/Users/Maximilian_Schulz/Documents_no_backup/Python/Vizro/vizro/vizro-mcp/playground/CA_baseline_metadata_and_annual_results.csv"
output_path = "/Users/Maximilian_Schulz/Documents_no_backup/Python/Vizro/vizro/vizro-mcp/playground/CA_baseline_metadata_and_annual_results_filtered.csv"
select_and_save_columns(csv_path, output_path)
