import os
import pycountry as pyco
import pandas as pd

# Cleaning pipeline for environmental burden of disease data
def clean_env_burden_data(df_raw,
                          country_name_mapping,
                          variable_name_mapping,
                          columns_to_remove = ['measure_id','measure_name','location_id',
                                               'sex_id','sex_name','age_id','age_name',
                                               'cause_id','cause_name','rei_id','metric_id',
                                               'metric_name','upper','lower'],
                          indicators_to_remove=['Unsafe water, sanitation, and handwashing','Non-optimal temperature']):
            """
            Clean raw DALY indicator data.

            Parameters
            ----------
            df_raw :    DataFrame
                        Raw data loaded via the load_env_burden_data() function.
            country_name_mapping : dict
                                   Dictionary mapping country names.
            variable_name_mapping :    dict
                                       Dictionary mapping feature names.
            columns_to_remove : list of str
                                List of column names to remove. Defaults to ['measure_id','measure_name','location_id','sex_id','sex_name',
                                'age_id','age_name','cause_id','cause_name','rei_id','metric_id','metric_name','upper','lower']
            indicators_to_remove :  list of str
                                    List of indicators to remove. Defaults to ['Unsafe water, sanitation, and handwashing','Non-optimal temperature']

            Returns
            ------------
            DataFrame: Cleaned DataFrame with DALY indicators.

            Notes
            ------------
            This function represents a cleaning pipeline for cleaning and transforming DALY indicator data.
            Raw data should be passed as is and should not be manually edited prior to applying this cleaning pipeline.
            
            Steps of the cleaning pipeline:
            1. Filters rows where 'sex_name' is equal to 'Both'.
            2. Drops unnecessary columns specified in columns_to_remove.
            3. Filters rows based on condition of not being in indicators_to_remove for 'rei_name'.
            4. Renames 'location_name' column to 'country'.
            5. Pivots table using 'country' and 'year' as index, 'id' as columns, and 'value' as values.
            6. Resets index of DataFrame.
            7. Renames columns based on daly_indicator_mapping dictionary.
            8. Shortens country names based on country_name_mapping dictionary.
            9. Assign ISO_3166_1_alpha_3 code (three-letter country code) to country names.
            10. Saves the cleaned DataFrame as CSV file to '../data/processed' folder.

            Examples
            --------
            process_env_burden_data(df_raw, {'United States': 'USA'}, {'indicator1': 'feature_A'}, ['column1', 'column2'], ['indicator2', 'indicator3'])

            """
            # Cleaning pipeline
            df_clean = (df_raw
                        .loc[df_raw['sex_name'] == 'Both'] # Step 1
                        .drop(columns=columns_to_remove) # Step 2
                        .loc[lambda x: ~x['rei_name'].isin(indicators_to_remove)] # Step 3
                        .rename(columns={'location_name': 'country'}) # Step 4
                        .pivot_table(index=['country','year'], columns='rei_name', values='val') # Step 5
                        .reset_index() # Step 6
                        .rename(columns=variable_name_mapping) # Step 7
                        .replace({'country': country_name_mapping}) # Step 8
                        .assign(year=lambda x: x['year'].astype('int64'), # step 9
                            ISO_3166_1_alpha_3=lambda x: x['country'].apply(get_country_code))) # step 9
            processed_data_folder  = '../data/processed'
            df_clean.to_csv(os.path.join(processed_data_folder, 'env_burden_clean.csv'), index=False) # Step 10
            print(f'Pipeline successfully completed and cleaned data saved to {processed_data_folder}.\n')
            return df_clean

# Mapping function to retrieve ISO 3166-1 alpha-3 codes (Three-letter country codes) from country names
def get_country_code(country_name):
    """
    Retrieve ISO 3166-1 alpha-3 country code for given country name.

    Parameters:
    ----------
    country_name :  str
                    Name of country for which country code is to be retrieved.

    Returns:
    ----------
    str or None: ISO 3166-1 alpha-3 country code if country name is mapped successfully,
    otherwise None if country name is not found or if an error occurs during lookup.

    Notes:
    ----------
    This function utilizes the `pycountry` library. If country name is not mapped successfully,
    it returns None. It handles LookupError exceptions that might occur during lookup.
    """
    try:
        country = pyco.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        return None

# Cleaning pipeline for health expenditure data
def clean_health_exp_data(df_raw, country_name_mapping):
        """
        Clean health expenditure data.

        Parameters:
        ----------
        df_raw :    DataFrame
                    Raw health expenditure data.
        country_name_mapping : dict
                               Dictionary mapping full country names to their shortened versions.

        Returns:
        ----------
        DataFrame: Cleaned health expenditure data.

        Notes:
        ----------
        This function represents a cleaning pipeline for cleaning and transforming health expenditure data.
        The data should be passed as is and should not be manually edited prior to applying this cleaning pipeline.

        Steps of the cleaning pipeline:
        1. Drop the last row as it contains the source information in a single row.
        2. Drop the 'Unnamed: 11' column.
        3. Rename the first column to 'country'.
        4. Replace full country names with their shortened versions using the provided mapping.
        5. Replace placeholder values ('..' and '...') with NaN.
        6. Drop rows with missing expenditure values for specified year range.
        7. Melt the dataframe to a long-format structure with columns 'country', 'year', and 'HEALTH_EXP'.
        8. Limit years to the range 2010-2019.
        9. Convert the 'year' column to integer type.
        10. Convert the 'HEALTH_EXP' column to float type.
        11. Retrieve ISO 3166-1 alpha-3 country code for country names.
        12. Save data to folder '../data/processed' for further analyses.

        """
        # Cleaning pipeline
        df_clean = (df_raw
                    .drop(df_raw.index[-1]) # step 1
                    .drop('Unnamed: 11', axis=1) # step 2
                    .rename(columns={df_raw.columns[0]: 'country'}) # step 3
                    .replace({'country': country_name_mapping}) # step 4
                    .replace(['..', '...'], pd.NA) # step 5
                    .dropna(subset=['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']) # step 6
                    .melt(id_vars='country', var_name='year', value_name='HEALTH_EXP') # step 7
                    .loc[lambda x: (x['year'] <= '2019') & (x['year'] >= '2010')] # step 8
                    .assign(year=lambda x: x['year'].astype('int64'), # step 9
                            HEALTH_EXP=lambda x: x['HEALTH_EXP'].astype('float64'), # step 10
                            ISO_3166_1_alpha_3=lambda x: x['country'].apply(get_country_code))) # step 11
        processed_data_folder  = '../data/processed'
        df_clean.to_csv(os.path.join(processed_data_folder, 'health_exp_clean.csv'), index=False) # step 12
        print(f'Pipeline successfully completed and cleaned data saved to {processed_data_folder}.\n')
        return df_clean

# Cleaning pipeline for environment expenditure data
def clean_env_exp_data(df_raw, country_name_mapping, variable_name_mapping):
    """
    Clean environment expenditure data.

    Parameters
    ----------
    env_exp_raw :   DataFrame
                    Raw environment expenditure data.
    country_name_mapping : dict
                           Dictionary mapping full country names to their shortened versions.
    variable_name_mapping : dict
                            Dictionary mapping expenditure names to shortened versions.

    Returns:
    ----------
    DataFrame: Cleaned environment expenditure data.

    Notes
    ----------
    This function represents a cleaning pipeline for cleaning and transforming environment expenditure data.
    The data should be passed as is and should not be manually edited prior to applying this cleaning pipeline.

    Steps of the cleaning pipeline:
    1. Drop unnecessary columns specified in columns_to_drop.
    2. Drop years outside the specified range in years_to_drop.
    3. Subset data where 'Unit' column is 'Percent of GDP'.
    4. Drop 'Unit' column.
    5. Rename 'CTS_Name' column to 'expenditure_id' for convenience.
    6. Drop rows with missing expenditure values for specified year range. 
    7. Reshape DataFrame by melting years into a single column.
    8. Expand expenditures into separate columns using pivoting.
    9. Reset index.
    10. Rename expenditure types according to expenditure_mapping.
    11. Calculate ssum of expenditures specified in env_expenditures_to_sum_up.
    12. Drop unnecessary expenditure columns.
    13. Shorten country names using country_mapping.
    14. Rename columns 'Country' to 'country', 'Year' to 'year', and 'ISO3' to 'ISO_3166_1_alpha_3'.
    15. Clean year values by removing 'F'.
    16. Change data type of 'year' column from text to integer.
    17. Limit years to specified range.
    18. Save data to folder '../data/processed' for further analyses.

    """
    # Initialize helper variables
    columns_to_drop = ['ObjectId','ISO2','Indicator','Source','CTS_Code','CTS_Full_Descriptor'] # specify unnecessary columns
    years_to_drop = [f'F{i}' for i in range(1995, 2009)] + [f'F{i}' for i in range(2020, 2023)] # specify years outside range
    env_expenditures_to_sum_up = ['ENV_EXP_Prot', 'ENV_EXP_BIODIV', 'ENV_EXP_OTHER','ENV_EXP_ResDev',
                                'ENV_EXP_POLLUTION', 'ENV_EXP_WASTE','ENV_EXP_WASTEWATER'] # specify columns to row-sum
    # Cleaning pipeline
    df_clean = (df_raw
                .drop(columns=columns_to_drop) # step 1
                .drop(columns=years_to_drop) # step 2
                .loc[df_raw['Unit'] == 'Percent of GDP'] # step 3
                .drop(columns=['Unit']) # step 4
                .rename(columns={'CTS_Name': 'expenditure_id'}) # step 5
                .dropna(subset=['F2010','F2011','F2012','F2013','F2014','F2015','F2016','F2017','F2018','F2019']) # step 6
                .melt(id_vars=['Country','ISO3','expenditure_id'], var_name='Year', value_name='Env_Expenditure') # step 7
                .pivot_table(index=['Country', 'ISO3', 'Year'], columns='expenditure_id', values='Env_Expenditure') # step 8
                .reset_index() # step 9
                .rename(columns=variable_name_mapping) # step 10
                .assign(ENV_EXP_TOTAL=lambda x: x[env_expenditures_to_sum_up].sum(axis=1)) # step 11
                .drop(columns=env_expenditures_to_sum_up) # step 12
                .replace({'Country': country_name_mapping}) # step 13
                .rename(columns={'Country': 'country', 'Year': 'year', 'ISO3': 'ISO_3166_1_alpha_3'}) # step 14
                .assign(year=lambda x: x['year'].str.replace('F', '')) # step 15
                .assign(year=lambda x: x['year'].astype('int64')) # step 16
                .loc[lambda x: (x['year'] <= 2019) & (x['year'] >= 2010)]) # step 17
    processed_data_folder  = '../data/processed'
    df_clean.to_csv(os.path.join(processed_data_folder, 'env_exp_clean.csv'), index=False) # step 18
    print(f'Pipeline successfully completed and cleaned data saved to {processed_data_folder}.\n')
    return df_clean