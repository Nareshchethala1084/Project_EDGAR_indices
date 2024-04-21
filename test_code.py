import pandas as pd  # Importing pandas for data manipulation
import os  # Importing os for file and directory operations

# Adjusting pandas display options for more optimized data viewing
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.width', None)  # Automatically adjust display width to terminal size
pd.set_option('display.max_colwidth', None)  # Display full content of each cell

# Function to load EDGAR index files from a specified year and directory
def load_data(year, source_dir):
    colspecs = [(0, 62), (62, 74), (74, 86), (86, 98), (98, None)]  # Column widths in fixed-width file
    column_names = ['Company Name', 'Form Type', 'CIK', 'Date Filed', 'Filename']  # Names of columns
    dataframe_collection = []  # List to store dataframes for each quarter

    # Loop through each quarter
    for quarter in ['QTR1', 'QTR2', 'QTR3', 'QTR4']:
        file_name = f'{year}_{quarter}_company.idx'  # Construct filename for each quarter
        file_path = os.path.join(source_dir, file_name)  # Create full path to the file

        # Check if the file exists before trying to open it
        if os.path.exists(file_path):
            try:
                # Read fixed-width file with specified columns and skip header rows using skiprows
                temp_df = pd.read_fwf(file_path, colspecs=colspecs, skiprows=9, names=column_names)
                dataframe_collection.append(temp_df)  # Add dataframe to the collection
            except UnicodeDecodeError as e:
                # Handle errors that occur if the file has encoding issues
                print(f'Error reading {file_name}: {e}')
                continue
            except Exception as e:
                # Handle other unexpected errors during file reading
                print(f'An unexpected error occurred while reading {file_name}: {e}')
                continue

    # Check if any data was loaded successfully
    if not dataframe_collection:
        print("No data was loaded. Please check your file paths and names.")
        return pd.DataFrame()  # Return an empty DataFrame if no data was loaded

    # Concatenate all quarterly DataFrames into one DataFrame
    all_data_df = pd.concat(dataframe_collection, ignore_index=True)
    all_data_df.columns = all_data_df.columns.str.strip()  # Strip any leading/trailing whitespace from column names
    return all_data_df  # Return the concatenated DataFrame

# Function to filter the DataFrame by company name or CIK
def find_companies_or_cik(all_data_df, search_term, search_type):
    try:
        if search_type == 'name':
            # Filter DataFrame by company name, ignoring case
            matching = all_data_df[all_data_df['Company Name'].str.contains(search_term, case=False, na=False)]
        else:  # search by 'cik'
            # Filter DataFrame by CIK
            matching = all_data_df[all_data_df['CIK'].astype(str) == str(search_term)]
        # Return filtered DataFrame with duplicate entries removed
        return matching[['Company Name', 'CIK']].drop_duplicates().reset_index(drop=True)
    except Exception as e:
        # Handle any errors that occur during filtering
        print(f"An error occurred during search: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs

# Function to get all filings for a specific CIK in a given year
def get_filings_for_company(all_data_df, cik, year):
    try:
        # Filter DataFrame for filings by the specified CIK and year
        filings_df = all_data_df[
            (all_data_df['CIK'] == cik) &
            (all_data_df['Date Filed'].str.contains(str(year)))
        ].reset_index(drop=True)
        return filings_df  # Return the filtered DataFrame
    except Exception as e:
        # Handle any errors during the filtering
        print(f"An error occurred while fetching filings for company CIK {cik}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs

# Function to display filings and allow the user to select one to view its URL
def display_and_choose_filings(filings_df):
    try:
        if filings_df.empty:
            # Check if the DataFrame is empty (no filings found)
            print("No filings found for this company.")
            return None

        # Display available filings for selection
        print(filings_df[['Form Type', 'Date Filed', 'Filename']])
        index_to_display = int(input("Enter the index number of the filing to display: "))
        # Validate user input
        if index_to_display >= len(filings_df):
            print("Invalid index number. Please enter a valid index from the list.")
            return None

        # Get the selected filing based on user input
        selected_filing = filings_df.iloc[index_to_display]
        # Construct the URL to view the filing
        filing_url = 'https://www.sec.gov/Archives/' + selected_filing['Filename']
        print(f"You can view the filing at the following URL:\n{filing_url}")
        return filing_url  # Return the URL
    except ValueError:
        # Handle invalid numeric input
        print("Invalid input. Please enter a numerical index.")
        return None
    except Exception as e:
        # Handle any other errors
        print(f"An error occurred while selecting filings: {e}")
        return None

if __name__ == "__main__":
    try:
        # Prompt user for the year of the filings to search
        year = int(input("Enter the exact year of the filings you want to search: "))
        print('Your Range of Data is:', year)
        
        # Prompt user for the type of search (name or CIK)
        search_type = input("Enter your choice of search : 'name' or 'CIK'? : ").lower()

        # Get the search term from the user based on the search type
        if search_type == 'name':
            search_term = input("Enter the company name to search for: ")
        else:
            search_term = input("Enter the CIK to search for: ").lstrip('0')

        # Ask user for the directory where the .idx files are stored
        source_dir = input('Please input the directory of your .idx files : ')
        
        # Load data from the specified year and directory
        user_data_df = load_data(year, source_dir)
        if user_data_df.empty:
            # Check if data was loaded successfully
            print("Data loading failed. Please check the file paths and year input.")
        else:
            print("Data loaded successfully. Here are the column names:")
            print(user_data_df.columns.tolist())

            # Validate the search type
            if search_type not in ['name', 'cik']:
                print("Invalid search type entered. Please restart and enter either 'name' or 'CIK'.")
            else:
                # Find matching companies or CIKs based on the search term and type
                matching_entities = find_companies_or_cik(user_data_df, search_term, search_type)
                if matching_entities.empty:
                    print(f"No matching entities found for the given {search_type}.")
                else:
                    print("Matching companies/CIKs:")
                    print(matching_entities)

                    # Handle filings retrieval based on the search type
                    if search_type == 'cik':
                        filings_df = get_filings_for_company(user_data_df, search_term, year)
                        display_and_choose_filings(filings_df)
                    elif search_type == 'name':
                        # Allow user to select a company from the list
                        company_index = int(input("Enter the index number of the company to display filings for: "))
                        if company_index not in matching_entities.index:
                            print("Invalid index number. Please enter a valid index from the list.")
                        else:
                            # Retrieve and display filings for the selected company
                            selected_cik = matching_entities.at[company_index, 'CIK']
                            filings_df = get_filings_for_company(user_data_df, selected_cik, year)
                            display_and_choose_filings(filings_df)

    except ValueError:
        # Handle errors caused by incorrect numeric input
        print("You have entered an invalid year or index number. Please restart and enter a valid number.")
    except Exception as e:
        # Handle any other exceptions that may occur
        print(f"An unexpected error occurred: {e}")
