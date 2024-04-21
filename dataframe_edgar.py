import pandas as pd
import os

# Adjusting pandas display options for more optimized data viewing
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.width', None)  # Automatically adjust display width to terminal size
pd.set_option('display.max_colwidth', None)  # Display full content of each cell

#Load data from all EDGAR index files in the specified director
def load_data_from_directory(source_dir):
    colspecs = [(0, 62), (62, 74), (74, 86), (86, 98), (98, None)]
    column_names = ['Company Name', 'Form Type', 'CIK', 'Date Filed', 'Filename']
    dataframe_collection = []

    # Iterate over each file in the directory
    for file_name in os.listdir(source_dir):
        if file_name.endswith('.idx'):  # Check for .idx files
            file_path = os.path.join(source_dir, file_name)
            try:
                # Read fixed-width file with specified columns and skip header rows
                temp_df = pd.read_fwf(file_path, colspecs=colspecs, skiprows=9, names=column_names)
                dataframe_collection.append(temp_df)
            except UnicodeDecodeError as e:
                print(f'Error reading {file_name}: {e}')
                continue
            except Exception as e:
                print(f'An unexpected error occurred while reading {file_name}: {e}')
                continue

    if not dataframe_collection:
        print("No data was loaded. Please check your file paths and names.")
        return pd.DataFrame()

    # Concatenate all DataFrames into one DataFrame
    combined_df = pd.concat(dataframe_collection, ignore_index=True)
    combined_df.columns = combined_df.columns.str.strip()  # Strip any leading/trailing whitespace from column names
    return combined_df

def save_to_csv(df, output_path):
    """Save DataFrame to a CSV file."""
    try:
        df.to_csv(output_path, index=False)
        print(f"Data saved successfully to {output_path}")
    except Exception as e:
        print(f"Failed to save the DataFrame: {e}")

# Main execution logic
if __name__ == "__main__":
    source_directory = input('Enter/path/to/data/directory: ')  # Get directory containing the data files from user
    csv_name = input('Enter the filename for the CSV (e.g., combined_data.csv): ')
    output_path = os.path.join(source_directory, csv_name)  # Construct the full path to save the CSV file

    # Load data from the specified directory
    all_data_df = load_data_from_directory(source_directory)

    # Save the data to a CSV file
    if not all_data_df.empty:
        save_to_csv(all_data_df, output_path)
    else:
        print("No data to save.")

