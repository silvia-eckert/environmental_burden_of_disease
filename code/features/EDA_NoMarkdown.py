# LOAD DATA
# Necessary packages
import os
import shutil
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
from IPython.display import display
from sklearn.decomposition import PCA
from adjustText import adjust_text
import geopandas as gpd
import requests
import pycountry as pyco
import subprocess
import sys
sys.path.insert(0, '../code')
import features.data_delivery as dd # .py script stored in ../code/features folder
import features.data_cleaning as dc # .py script stored in ../code/features folder

# Load necessary dictionaries for country name and variable mapping
# This subprocess wil create two .json files in the ../code/datasets folder
subprocess.run(["python", "../code/features/country_and_variable_mapping.py"])

# Load country_name_mapping dictionary
with open('../code/datasets/country_name_mapping.json', 'r') as json_file:
    country_name_mapping = json.load(json_file)
# Load variable_name_mapping dictionary
with open('../code/datasets/variable_name_mapping.json', 'r') as json_file:
    variable_name_mapping = json.load(json_file)

# Load health expenditure data
health_exp_raw = dd.load_health_exp_data()
# Clean health expenditure data
# This will create a .csv file in the ../data/processed folder
health_exp_clean = dc.clean_health_exp_data(health_exp_raw, country_name_mapping)
#print(health_exp_clean.head())

# Load environment expenditure data
env_exp_raw = dd.fetch_env_exp_data()
# Clean environment expenditure data
# This will create a .csv file in the ../data/processed folder
env_exp_clean = dc.clean_env_exp_data(env_exp_raw, country_name_mapping, variable_name_mapping)
#print(env_exp_clean.head())

# Load environmental burden data
env_burden_raw = dd.load_env_burden_data()
# Clean environmental burden data
# This will create a .csv file in the ../data/processed folder
env_burden_clean = dc.clean_env_burden_data(env_burden_raw, country_name_mapping, variable_name_mapping)
#print(env_burden_clean.head())

# Inner join data on country names and years
# Countries without expenditures reported will be removed from dataset
expenditures_merged = pd.merge(health_exp_clean, env_exp_clean, on=['country','year','ISO_3166_1_alpha_3'], how='inner') # merge expenditures
env_burden_data = pd.merge(expenditures_merged, env_burden_clean, on=['country','year','ISO_3166_1_alpha_3'], how='inner') # merge with burden of disease indicators
env_burden_data.to_csv('../code/datasets/env_burden_data.csv', index=False)
print('Data merged and saved succesfully\n')
display(env_burden_data.dtypes)
env_burden_data

# EXPLORATORY ANALYSES
## Summary statistics
# Calculate basic summary stats across years 2010-2019
DALY_indicators_to_include = ['DALY_OZONE_POLLUTION','DALY_HIGH_TEMP','DALY_LOW_TEMP','DALY_NO_ACCESS_HANDWASHING',
                              'DALY_PARTICULATE_MATTER_POLLUTION','DALY_UNSAFE_SANITATION','DALY_UNSAFE_WATER_SOURCE']
summary_stats = pd.DataFrame({
    'mean': env_burden_clean[DALY_indicators_to_include].mean(), # arithmetic mean (= average)
    'median': env_burden_data[DALY_indicators_to_include].median(), # median
    'mode': env_burden_data[DALY_indicators_to_include].mode().iloc[0], # first value of mode
    'std': env_burden_data[DALY_indicators_to_include].std(), # standard deviation
    'min': env_burden_data[DALY_indicators_to_include].min(), # maximum
    'max': env_burden_data[DALY_indicators_to_include].max(), # minimum
    'unit': ['DALY per 100,000'] * len(env_burden_data[DALY_indicators_to_include].columns) # units of measurement
})
display(summary_stats)

# ## Expenditure exploration
## Variation of expenditures (% GDP) over years 2010-2019
expenditures_melted = pd.melt(env_burden_data,
                              id_vars=['country', 'year'], 
                              value_vars=['HEALTH_EXP', 'ENV_EXP_TOTAL'],
                              var_name='category', value_name='expenditure') # melt data for use in seaborn 
# Create a grid for the plots
fig = plt.figure(figsize=(8, 4))
gs = GridSpec(nrows=2, ncols=2, width_ratios=[2, 1])
# Health expenditure over time
ax0 = fig.add_subplot(gs[0, 0])
sns.lineplot(data=expenditures_melted[expenditures_melted['category'] == 'HEALTH_EXP'],
             x='year', y='expenditure', hue='category', err_kws={'fc': 'gray'}, ax=ax0)
ax0.set_title('Health expenditure over time')
ax0.legend().remove()
ax0.set_xlabel('')
ax0.set_ylabel('Expenditure in % GDP')
ax0.lines[0].set_color('gray')
# Line plots on the first subplot
ax1 = fig.add_subplot(gs[1, 0])
sns.lineplot(data=expenditures_melted[expenditures_melted['category'] == 'ENV_EXP_TOTAL'],
             x='year', y='expenditure', hue='category', err_kws={'fc': 'gray'}, ax=ax1)
ax1.set_title('Environmental expenditure over time')
ax1.legend().remove()
ax1.set_xlabel('Years')
ax1.set_ylabel('Expenditure in % GDP')
ax1.lines[0].set_color('gray')
# Violin plot showing the distribution of expenditures
ax2 = fig.add_subplot(gs[:, 1])
sns.violinplot(x='category', y='expenditure', data=expenditures_melted, color="gray", ax=ax2)
ax2.set_title('Distribution of expenditures')
ax2.set_xlabel('')
ax2.set_xticklabels(['Health','Environment'])
ax2.set_ylabel('Expenditure in % GDP')
# show plots
plt.tight_layout()
plt.show()

# Top 3 countries with highest/lowest expenditures
# Calculate median and sort according to health expenditure
data_by_health = env_burden_data.groupby('country').apply(lambda x: x.drop(['year','ISO_3166_1_alpha_3'], axis=1).median()).reset_index()
data_by_health = data_by_health.sort_values(by='HEALTH_EXP', ascending=False)
print(data_by_health.head())

# Calculate median and sort according to health expenditure
data_by_environment = env_burden_data.groupby('country').apply(lambda x: x.drop(['year','ISO_3166_1_alpha_3'], axis=1).median()).reset_index()
data_by_environment = data_by_environment.sort_values(by='ENV_EXP_TOTAL', ascending=False)
print(data_by_environment.head())

# Create a 2-by-2 bar chart
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 5))
# Top 5 with highest health expenditure
sns.barplot(x='HEALTH_EXP', y='country', data=data_by_health.head(5), ax=axes[0, 0], color='#404040')
axes[0, 0].set_title('Top 5 Countries: Highest Health Expenditure (% GDP)')
axes[0, 0].set_xlabel('')
axes[0, 0].set_ylabel('')
# Top 5 with highest environment expenditure
sns.barplot(x='ENV_EXP_TOTAL', y='country', data=data_by_environment.head(5), ax=axes[0, 1], color='#404040')
axes[0, 1].set_title('Top 5 Countries: Highest Environment Expenditure (% GDP)')
axes[0, 1].set_xlabel(' ')
axes[0, 1].set_ylabel('')
# Top 5 with least health expenditure
sns.barplot(x='HEALTH_EXP', y='country', data=data_by_health.tail(5), ax=axes[1, 0], color='#b5b5b5')
axes[1, 0].set_title('Top 5 Countries: Least Health Expenditure (% GDP)')
axes[1, 0].set_xlabel(' ')
axes[1, 0].set_ylabel('')
# Top 5 with least environemnt expenditure
sns.barplot(x='ENV_EXP_TOTAL', y='country', data=data_by_environment.tail(5), ax=axes[1, 1], color='#b5b5b5')
axes[1, 1].set_title('Top 5 Countries: Least Environment Expenditure (% GDP)')
axes[1, 1].set_xlabel(' ')
axes[1, 1].set_ylabel('')
plt.tight_layout()
plt.show()

# DALY indicator exploration
# Melt the DataFrame to convert it from wide to long format
melted_indicators = (env_burden_data
                     .drop(columns=['HEALTH_EXP','ENV_EXP_TOTAL'])
                     .melt(id_vars=['country', 'year','ISO_3166_1_alpha_3'], var_name='feature', value_name='value'))
# Visualize indicators across years
plt.figure(figsize=(10, 6))
sns.lineplot(data=melted_indicators, x='year', y='value', hue='feature')
plt.title('DALY indicators over the years 2010-2019')
plt.xlabel('Year')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
plt.tight_layout()
plt.show()

# Melt the DataFrame to convert it from wide to long format
melted_indicators = (env_burden_data
                     .drop(columns=['HEALTH_EXP','ENV_EXP_TOTAL','DALY_PARTICULATE_MATTER_POLLUTION'])
                     .melt(id_vars=['country', 'year','ISO_3166_1_alpha_3'], var_name='feature', value_name='value'))
# Visualize indicators across years
plt.figure(figsize=(10, 6))
sns.lineplot(data=melted_indicators, x='year', y='value', hue='feature')
plt.title('DALY indicators over the years 2010-2019')
plt.xlabel('Year')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
plt.tight_layout()
plt.show()

# Outlier analysis
# Conduct principal components analysis (PCA)
# Presets
numerical_features = env_burden_data.drop(columns=['year','HEALTH_EXP','ENV_EXP_TOTAL'], axis=1).select_dtypes(include=['number'])
countries = env_burden_data['country']
mean_per_country = numerical_features.groupby(countries).mean() # aggregate mean per country
z_scores = (mean_per_country - mean_per_country.mean()) / mean_per_country.std() # z-scores to use in PCA instead of raw mean
# Calculate PCA
pca = PCA(n_components=2) # keep first two components
principal_components = pca.fit_transform(z_scores) # calculate scores
# Visualize PCA
plt.figure(figsize=(10, 6))
texts = []
for i, country in enumerate(mean_per_country.index):
    plt.scatter(principal_components[i, 0], principal_components[i, 1], label=country)
    texts.append(plt.text(principal_components[i, 0], principal_components[i, 1], country, fontsize=8, ha='left', va='bottom'))
adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', alpha=0.5))
plt.title('Principal Components Analysis')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(ncol=3, loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(True)
loadings = pca.components_.T # add loadings
texts_loadings = []
for i, feature in enumerate(mean_per_country.columns):
    arrow_length = np.sqrt(loadings[i, 0]**2 + loadings[i, 1]**2)
    label_offset = 0.5 * arrow_length
    plt.arrow(0, 0, loadings[i, 0]*1.5, loadings[i, 1]*5, color='r', alpha=0.5, head_width=0.05)
    texts_loadings.append(plt.text(loadings[i, 0]*1.5 + label_offset, loadings[i, 1]*5, feature, color='g',
                                   fontsize=8, ha='left', va='bottom'))
adjust_text(texts_loadings, arrowprops=dict(arrowstyle="->", color='r', alpha=0.5))
plt.show()

# Feature correlation
## Create heatmap
plt.figure(figsize=(10, 4))
heatmap_features = sns.heatmap(env_burden_data.select_dtypes(include=['float64']).corr(), vmin=-1, vmax=1, annot=True, cmap='BrBG', annot_kws={"fontsize": 8})
heatmap_features.set_xticklabels(heatmap_features.get_xticklabels(), fontsize=8)
heatmap_features.set_yticklabels(heatmap_features.get_yticklabels(), fontsize=8)
heatmap_features.set_title('Features correlating with health and environmental expenditures per country', fontdict={'fontsize':10}, pad=20)
plt.show()

# Create heatmap specific to expenditures
plt.figure(figsize=(4, 4))
heatmap_specific = sns.heatmap(env_burden_data.select_dtypes(include=['float64']).corr()[['HEALTH_EXP', 'ENV_EXP_TOTAL']].sort_values(by='HEALTH_EXP', ascending=False), vmin=-1, vmax=1, annot=True, cmap='BrBG', annot_kws={"fontsize": 8})
heatmap_specific.set_xticklabels(heatmap_specific.get_xticklabels(), fontsize=8)
heatmap_specific.set_yticklabels(heatmap_specific.get_yticklabels(), fontsize=8)
heatmap_specific.set_title('Features correlating with health and environmental expenditures per country', fontdict={'fontsize':10}, pad=20)
plt.show()

# Repository Link
# The original repository containing the code used in this analysis can be found [here](https://github.com/silvia-eckert).


