# /// script
# dependencies = [
#   "pyarrow",
#   "fastparquet",
# ]
# ///

import os

import pandas as pd


def load_and_drop_column(csv_file_path: str, save_output: bool = True) -> pd.DataFrame:
    """Read a filtered CSV file, drop the electric vehicle column, and optionally save the result.

    Args:
        csv_file_path (str): Path to the filtered CSV file
        save_output (bool, optional): Whether to save the modified DataFrame. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with the electric vehicle column dropped
    """
    try:
        # Read the filtered CSV file
        df = pd.read_csv(csv_file_path)

        # Drop the electric vehicle column
        if "in.electric_vehicle" in df.columns:
            df = df.drop(columns=["in.electric_vehicle"])
            print(f"Successfully loaded {csv_file_path} and dropped 'in.electric_vehicle' column")

            # Save the modified DataFrame if requested
            if save_output:
                output_path = os.path.splitext(csv_file_path)[0] + "_no_ev.csv"
                df.to_csv(output_path, index=False)
                print(f"Saved modified DataFrame to {output_path}")
        else:
            print(f"Column 'in.electric_vehicle' not found in {csv_file_path}")

        return df
    except Exception as e:
        print(f"Error processing CSV file: {e!s}")
        return pd.DataFrame()


# Load the filtered CSV and drop the electric vehicle column
csv_path = "/Users/Maximilian_Schulz/Documents_no_backup/Python/Vizro/vizro/vizro-mcp/playground/CA_baseline_metadata_and_annual_results_filtered.csv"
df = load_and_drop_column(csv_path)
