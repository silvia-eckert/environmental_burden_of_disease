# Necessary packages
import os
import pandas as pd
import zipfile
import shutil
import requests

# Extract DALY indicators from Global Burden of Disease 2019 Study
def load_env_burden_data(raw_data_folder='../data/raw',
                         interim_file_folder='../data/interim/',
                         num_zip_archives=2):
    """
    Extract and concatenate raw DALY indicator data from downloaded ZIP archives to specified folder.

    Parameters:
    ----------
    raw_data_folder :   str
                        Folder name of downloaded ZIP archives. Defaults to '../data/raw'.
    interim_file_folder :   str
                            Folder name of extracted files. Defaults to '../data/interim/'.
    num_zip_archives :  int
                        Number of downloaded ZIP archives to extract and concatenate. Defaults to 2.

    Returns:
    ----------
    DataFrame: The concatenated DataFrame containing extracted data.

    Notes:
    ----------
    The data should be passed as is (i.e. as downloaded ZIP archives)
    and should not be manually edited prior to applying this function.

    Examples:
    ----------
    df = load_env_burden_data()
    print(df.head())

    """
    # Initialize helper variables
    num_files_processed = 0 # counts processed files
    df_append = [] # DataFrame to store concatenated data

    # Iterate through files in 'raw' starting with 'IHME-GBD_2019_DATA' and extract ZIP files
    for file_name in os.listdir(raw_data_folder):
        if num_files_processed >= num_zip_archives:
            break # Exit loop if desired number of files have been processed

        if file_name.endswith('.zip') and file_name.startswith('IHME-GBD_2019_DATA'): # Check if files conditions
            with zipfile.ZipFile(os.path.join(raw_data_folder, file_name), 'r') as zip_file: # Extract files
                zip_file.extractall(interim_file_folder)
            # Iterate through extracted files and combine into one (since they should have the same structure)
            for extracted_file_name in os.listdir(interim_file_folder):
                if num_files_processed >= num_zip_archives:
                    break # Exit loop if desired number of files have been processed
                
                if extracted_file_name.endswith('.csv') and extracted_file_name.startswith('IHME-GBD'): # Check if files match conditions
                    df_loaded = pd.read_csv(os.path.join(interim_file_folder, extracted_file_name)) # Load file
                    df_append.append(df_loaded) # Append loaded data
                    num_files_processed += 1 # Increment counter
                
    print('Data loaded successfully.\n')
    df_raw = pd.concat(df_append, ignore_index=True)
    return df_raw

# Load health expenditure data from World Bank
def load_health_exp_data(raw_file_path = '../data/raw/Data_Extract_FromWorld Development Indicators.xlsx',
                         interim_file_folder = '../data/interim/',
                         interim_file_name = 'WorldBank-DataBank_HealthExpenditure_Global_1990_2022.xlsx'
                        ):
        """
        Load raw health expenditure data to specified folder and rename for convenience.

        Parameters:
        ----------
        raw_file_path : str
                        Path to downloaded file with health expenditure data.
                        Defaults to '../data/raw/Data_Extract_FromWorld Development Indicators.xlsx'.
        interim_file_folder :   str
                                Folder name of extracted files. Defaults to '../data/interim/'.
        interim_file_name : str
                            Desired name for downloaded file after renaming.
                            Defaults to 'WorldBank-DataBank_HealthExpenditure_Global_1990_2022.xlsx'.

        Returns:
        ----------
        DataFrame or None: DataFrame containing the downloaded data if successful, otherwise None.

        Notes:
        ----------
        The data should be passed as is (i.e. as downloaded and placed manually into the './data/raw' folder)
        and should not be manually edited prior to applying this function.

        Examples:
        ----------
        df = load_health_exp_data()
        print(df.head())
        
        """
        # Initialize helper variable
        interim_file_path = os.path.join(interim_file_folder, interim_file_name) # path to move the renamed file to (created from Parameters)
        try:
            shutil.copy(raw_file_path, interim_file_path) # copy to interim data folder
            df_raw = pd.read_excel(interim_file_path, header=0) # read into DataFrame
            print("File renamed and loaded successfully.\n")
            return df_raw
        except OSError as e:
            print(f"Error: {e.strerror}")

# Load environment expenditure data from International Monetary Fund
def fetch_env_exp_data(ev_exp_url='https://opendata.arcgis.com/datasets/d22a6decd9b147fd9040f793082b219b_0.csv',
                       raw_file_folder = '../data/raw/',
                       raw_file_name = 'IMF-CCD_EnvironmentalExpenditures_Global_1995_2022.csv'):
    """
    Download data from given URL, rename it, save it to specified folder, and read it as DataFrame.

    Parameters:
    ----------
    data_url :  str
                URL from which to download the data. Default is 'https://opendata.arcgis.com/datasets/d22a6decd9b147fd9040f793082b219b_0.csv'.
    raw_file_folder :   str
                        Folder path to downloaded file. Defaults to '../data/raw/'.
    raw_file_name : str
                    New name of downloaded file for convenience.
                    Defaults to 'IMF-CCD_EnvironmentalExpenditures_Global_1995_2022.csv'.

    Returns:
    ----------
    DataFrame or None: The pandas DataFrame containing the downloaded data if successful, otherwise None.

    Examples:
    ----------
    df = fetch_env_exp_data()
    print(df)

    """
    # Initialize helper variable and send request to download data
    raw_file_path = os.path.join(raw_file_folder, raw_file_name)
    response = requests.get(ev_exp_url)

    # Check if request was successful (then save file and read data)
    if response.status_code == 200:
        with open(raw_file_path, 'wb') as file:
            file.write(response.content)
        df_raw = pd.read_csv(raw_file_path, header=0)
        print('Data fetched, saved and loaded successfully.\n')
        return df_raw
    else:
        print("Failed to retrieve data from the URL.")