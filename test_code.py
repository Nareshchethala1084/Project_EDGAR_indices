import pandas as pd
import os

# Adjust pandas display options for more comprehensive data viewing
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def load_data(year, source_dir):
    """
    Loads the EDGAR index files for the specified year and returns a dataframe.
    """
    colspecs = [(0, 62), (62, 74), (74, 86), (86, 98), (98, None)]
    column_names = ['Company Name', 'Form Type', 'CIK', 'Date Filed', 'Filename']
    dataframe_collection = []

    for quarter in ['QTR1', 'QTR2', 'QTR3', 'QTR4']:
        file_name = f'{year}_{quarter}_company.idx'
        file_path = os.path.join(source_dir, file_name)

        if os.path.exists(file_path):
            try:
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

    all_data_df = pd.concat(dataframe_collection, ignore_index=True)
    all_data_df.columns = all_data_df.columns.str.strip()
    return all_data_df

def find_companies_or_cik(all_data_df, search_term, search_type):
    """
    Filters the dataframe for companies matching the search term or a CIK.
    """
    try:
        if search_type == 'name':
            matching = all_data_df[all_data_df['Company Name'].str.contains(search_term, case=False, na=False)]
        else:  # search by 'cik'
            matching = all_data_df[all_data_df['CIK'].astype(str) == str(search_term)]
        return matching[['Company Name', 'CIK']].drop_duplicates().reset_index(drop=True)
    except Exception as e:
        print(f"An error occurred during search: {e}")
        return pd.DataFrame()

def get_filings_for_company(all_data_df, cik, year):
    """
    Returns all filings for a specific CIK and year, with reset index.
    """
    try:
        filings_df = all_data_df[
            (all_data_df['CIK'] == cik) &
            (all_data_df['Date Filed'].str.contains(str(year)))
        ].reset_index(drop=True)
        return filings_df
    except Exception as e:
        print(f"An error occurred while fetching filings for company CIK {cik}: {e}")
        return pd.DataFrame()

def display_and_choose_filings(filings_df):
    """
    Displays filings and prompts user to choose one to view the URL.
    """
    try:
        if filings_df.empty:
            print("No filings found for this company.")
            return None

        print(filings_df[['Form Type', 'Date Filed', 'Filename']])
        index_to_display = int(input("Enter the index number of the filing to display: "))
        if index_to_display >= len(filings_df):
            print("Invalid index number. Please enter a valid index from the list.")
            return None

        selected_filing = filings_df.iloc[index_to_display]
        filing_url = 'https://www.sec.gov/Archives/' + selected_filing['Filename']
        print(f"You can view the filing at the following URL:\n{filing_url}")
        return filing_url
    except ValueError:
        print("Invalid input. Please enter a numerical index.")
        return None
    except Exception as e:
        print(f"An error occurred while selecting filings: {e}")
        return None

# Main flow
if __name__ == "__main__":
    try:
        # Prompting the user for the exact year of the filings
        year = int(input("Enter the exact year of the filings you want to search: "))
        print('Your Range of Data is:', year)
        
        # Prompting the user for the choice of search type wither 'name' or 'CIK'.
        search_type = input("Enter your choice of search : 'name' or 'CIK'? : ").lower()

        # Prompting the user for input based on the search type
        if search_type == 'name':
            search_term = input("Enter the company name to search for: ")
        else:
            search_term = input("Enter the CIK to search for: ").lstrip('0')

        # Directory where .idx files are stored
        source_dir = ('Please input the directory of your .idx files : ')
        
        #Creating a Dataframe to store the user selected year and search type
        user_data_df = load_data(year, source_dir)
        if user_data_df.empty:
            print("Data loading failed. Please check the file paths and year input.")
        else:
            print("Data loaded successfully. Here are the column names:")
            print(all_data_df.columns.tolist())

            if search_type not in ['name', 'cik']:
                print("Invalid search type entered. Please restart and enter either 'name' or 'CIK'.")
            else:
                matching_entities = find_companies_or_cik(user_data_df, search_term, search_type)
                if matching_entities.empty:
                    # Checking the search type to determine the prompt message
                    if search_type == 'name':
                        search_type_message = 'name'
                    else:
                        search_type_message = 'CIK'

                    # Constructing the message based on the search type
                    message = f"No matching entities found for the given {search_type_message}."

                    # Print the message
                    print(message)

                else:
                    print("Matching companies/CIKs:")
                    print(matching_entities)

                    # Directly retrieve filings if searching by CIK
                    if search_type == 'cik':
                        filings_df = get_filings_for_company(user_data_df, search_term, year)
                        display_and_choose_filings(filings_df)
                    elif search_type == 'name':  # Ask to choose a company when searching by name
                        company_index = int(input("Enter the index number of the company to display filings for: "))
                        if company_index not in matching_entities.index:
                            print("Invalid index number. Please enter a valid index from the list.")
                        else:
                            selected_cik = matching_entities.at[company_index, 'CIK']
                            filings_df = get_filings_for_company(user_data_df, selected_cik, year)
                            display_and_choose_filings(filings_df)

    except ValueError:
        print("You have entered an invalid year or index number. Please restart and enter a valid number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
