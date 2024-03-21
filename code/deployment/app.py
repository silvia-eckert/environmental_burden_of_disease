import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import pycountry as pyco
import plotly.express as px
import plotly.figure_factory as ff

# ===========================================================================================================
# ################## DATA ###################################################################################
# ===========================================================================================================

# Import data
df_global = pd.read_csv('./code/datasets/env_burden_data.csv', sep=",", header=0)
# Mapping indicator names for convenience
dict_feature_mapping = {'HEALTH_EXP': 'Health Expenses',
                        'ENV_EXP_TOTAL': 'Environment Expenses',
                        'DALY_OZONE_POLLUTION': 'Ozone Pollution',
                        'DALY_HIGH_TEMP': 'High Temperature', 'DALY_LEAD_EXPOSURE': 'Lead Exposure',
                        'DALY_LOW_TEMP': 'Low Temperature', 'DALY_NO_ACCESS_HANDWASHING': 'No Access to Handwashing Facilities',
                        'DALY_PARTICULATE_MATTER_POLLUTION': 'Particulate Matter Pollution',
                        'DALY_RESIDENTIAL_RADON': 'Residential Radon',
                        'DALY_UNSAFE_SANITATION': 'Unsafe Sanitation Facilities',
                        'DALY_UNSAFE_WATER_SOURCE': 'Unsafe Water Sources',
                        'ISO_3166_1_alpha_3': 'iso3_code'}
df_global = df_global.rename(columns=dict_feature_mapping)
# Create variables
vars_daly = df_global.loc[:, ~df_global.columns.str.contains('iso|country|year|Health|Environment', case=False)].columns.tolist()
vars_country = [var for var in df_global['country'].unique()]
vars_year = [var for var in df_global['year'].unique()]
country_number = df_global['country'].nunique()
# Expenditure data
df_subset = df_global.loc[:, df_global.columns.str.contains('country|year|Health|Environment', case=False)]
df_subset['Other'] = 100 - (df_subset['Health Expenses'] + df_subset['Environment Expenses'])
df_exp = pd.melt(df_subset, id_vars=['country', 'year'], var_name='exp_type', value_name='exp_value')
df_exp['exp_type'] = df_exp['exp_type'].replace({'Health Expenses': 'Health', 'Environment Expenses': 'Environment'})
# Mapping country names to ISO 3166-1 alpha-3 code (kept for compatibility)
#def get_country_code(country_name):
#    try:
#        country = pyco.countries.lookup(country_name)
#        return country.alpha_3
#    except LookupError:
#        return None
#df_global['iso3_code'] = df_global['country'].apply(get_country_code)

# ===========================================================================================================
# ################## APPLICATION ############################################################################
# ===========================================================================================================

# Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN])
app.title = 'Environmental Burden Dashboard'

# Sidebar containers
sidebar = html.Div(
[
    dbc.Row(
        [
            html.H5('Environmental burden of disease',
                    style={'margin-top': '12px', 'margin-left': '24px', 'color': 'white'})
        ],
        style={"height": "7vh"},
        className='bg-primary text-white font-italic'
    ),
    dbc.Row(
        [
            html.Div([
                html.P([
                    'Suboptimal environments increase health risks and the loss of healthy life years, potentially demanding increased governmental expenditure on health and environment. This dashboard displays age-adjusted indicators of ',
                     html.A('environmental burden', href='https://www.who.int/activities/environmental-health-impacts', target='_blank'),
                     ' provided as disability-adjusted life years (',
                    html.A('DALYs', href='https://www.who.int/data/gho/indicator-metadata-registry/imr-details/158', target='_blank'),
                    f') per 100,000 people for {country_number} countries across the years {min(vars_year)}-{max(vars_year)}. ',
                     html.B('The lower the value of DALYs the better. '),
                     '\nSource: ',
                     html.A('Global Burden of Disease Study 2019', href='https://www.healthdata.org/research-analysis/gbd', target='_blank'),
                ], style={'text-align': 'justify', 'text-justify': 'inter-word',
                          'marginRight': '35px', 'font-size': '0.8rem'},
                className='font-weight-bold')
            ],
            style={"height": "18vh",
                   'marginLeft': '20px', 'marginRight': '10px',
                   'marginTop': '10px', 'marginBottom': '10px'}
            )
        ]
    ),
    dbc.Row(
        [
            html.Div([
                html.P('Select Country',
                       style={'margin-top': '8px', 'margin-bottom': '4px', 'font-size': '0.8rem'},
                       className='font-weight-bold'),
                dcc.Dropdown(id='country-picker', multi=False, value=vars_country[0],
                             options=[{'label': x, 'value': x}
                                      for x in vars_country],
                             style={'width': '320px', 'font-size': '0.8rem'}
                             ),
                html.P('Select Year',
                       style={'margin-top': '16px', 'margin-bottom': '4px', 'font-size': '0.8rem'},
                       className='font-weight-bold'),
                dcc.Dropdown(id='year-picker', multi=False, value=min(vars_year),
                             options=[{'label': x, 'value': x}
                                      for x in vars_year],
                             style={'width': '320px', 'font-size': '0.8rem'}
                             ),
                html.P('Select Indicator(s) for Correlation',
                       style={'margin-top': '16px', 'margin-bottom': '4px', 'font-size': '0.8rem'},
                       className='font-weight-bold'),
                dcc.Dropdown(id='corr-picker', multi=True,
                             value=vars_daly,
                             options=[{'label': x, 'value': x}
                                      for x in vars_daly],
                             style={'width': '320px', 'font-size': '0.8rem'}
                             ),
                html.P('Select Indicator for Annual Variation',
                       style={'margin-top': '16px', 'margin-bottom': '4px', 'font-size': '0.8rem'},
                       className='font-weight-bold'),
                dcc.Dropdown(id='indicator-picker', multi=False,
                             value=vars_daly[0],
                             options=[{'label': x, 'value': x}
                                      for x in vars_daly],
                             style={'width': '320px', 'font-size': '0.8rem'}
                             ),
                html.Button(id='apply-button', n_clicks=0, children='Apply Selection',
                            style={'margin-top': '16px', 'font-size': '0.8rem'},
                            className='bg-dark text-white'),
                html.Hr()
            ]
            )
        ],
        style={'height': '50vh', 'margin': '10px'}
    )
]
)

# Content containers
content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P(id='pie-title',
                                   className='font-weight-bold'),
                            dcc.Graph(id="pie-chart",
                                      className='bg-light')])
                        ], width=5),
                dbc.Col(
                    [
                        html.Div([
                            html.P(id='corr-title',
                                   className='font-weight-bold'),
                            dcc.Graph(id='corr-chart',
                                      className='bg-light')])
                        ], width=7)
                ],
            style={'height': '45vh',
                   'marginTop': '20px', 'marginBottom': '30px',
                   'marginLeft': '10px', 'marginRight': '10px'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([
                            html.P(id='map-title',
                                   className='font-weight-bold'),
                            dcc.Graph(id='map',
                                      className='bg-light')])
                        ], width=7),
                dbc.Col(
                    [
                        html.Div([
                            html.P(id='line-title',
                                   className='font-weight-bold'),
                            dcc.Graph(id="line-chart",
                                      className='bg-light')])
                        ], width=5)
                ],
            style={"height": "50vh",
                   'marginTop': '10px', 'marginBottom': '10px',
                   'marginLeft': '10px', 'marginRight': '10px'})
        ]
    )

# App layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-light'),
                dbc.Col(content, width=9)
                ]
            ),
        ],
    fluid=True
    )
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-light'),
                dbc.Col(content, width=9)
                ]
            ),
        ],
    fluid=True
    )

# ===========================================================================================================
# ################## VISUALISATIONS #########################################################################
# ===========================================================================================================

# Pie chart
@app.callback(Output('pie-chart', 'figure'),
              Output('pie-title', 'children'),
              Input('apply-button', 'n_clicks'),
              [State('country-picker', 'value'),
              State('year-picker', 'value')])
def update_pie_chart(n_clicks, country, year):
    filtered_df = df_exp[(df_exp['country'] == country) & (df_exp['year'] == year)]

    fig_pie = px.pie(filtered_df,
                 values='exp_value',
                 names='exp_type',
                 hole=0.5,
                 color_discrete_sequence=['#d4d4d4', '#b7d2e8', '#03045e'])

    fig_pie.update_layout(autosize=True,
       #ä width=450,
        height=300,
        margin=dict(l=2, r=2, t=2, b=2),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig_pie.update_traces(textposition='outside',
                          textinfo='percent+label',
                          showlegend=False,
                          rotation=90)

    title_pie = 'Expenditures (% GDP) in ' + str(year) + ' for ' + country

    return fig_pie, title_pie

# Heatmap
@app.callback(Output('corr-chart', 'figure'),
              Output('corr-title', 'children'),
              Input('apply-button', 'n_clicks'),
              [State('country-picker', 'value'),
              State('corr-picker', 'value')])
def update_heatmap(n_clicks, country, corr_pick):
    df_country = df_global[df_global['country'] == country]
    columns_to_correlate = df_country.filter(regex='xpenses').columns.tolist()
    columns_to_correlate.extend(corr_pick)

    df_corr = df_country[columns_to_correlate].corr()
    y = list(filter(lambda x: 'xpenses' not in x, df_corr.index))
    x = list(filter(lambda x: 'xpenses' in x, df_corr.index))
    z = df_corr.loc[y, x].values
    
    custom_colorscale = [
        [0, '#034c73'], # minimum
        [0.5, 'white'], # midpoint
        [1, '#429e9d'] # maximum
    ]
    fig_heatmap = ff.create_annotated_heatmap(
        z,
        x=x,
        y=y,
        annotation_text=np.around(z, decimals=2),
        hoverinfo='z',
        colorscale=custom_colorscale#'Blues'
    )

    fig_heatmap.update_layout(autosize=True,
                        height=300,
                        margin=dict(l=10, r=10, t=10, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=None,
                        yaxis_title=None,
                        xaxis_title=None
                        )
    
    title_heatmap = 'Correlation of DALY indicators for ' + country

    return fig_heatmap, title_heatmap

# Map
@app.callback(Output('map', 'figure'),
              Output('map-title', 'children'),
              Input('apply-button', 'n_clicks'),
              [State('year-picker', 'value'),
               State('indicator-picker', 'value')])
def update_map(n_clicks, year, indicator):
    year_df = df_global[df_global['year'] == year]
    indicator_df = year_df[['country', 'iso3_code', indicator]]

    fig_map = px.choropleth(locations=indicator_df['iso3_code'],
                            color=indicator_df[indicator].fillna('red'),
                            hover_name=indicator_df['country'],
                            projection='natural earth',
                            color_continuous_scale='Blues',
                            range_color=(0, indicator_df[indicator].max())
                        )

    # Set border color to gray
    fig_map.update_geos(
        showocean=False,
        showland=True, landcolor='rgba(0,0,0,0)',
        showcountries=True, countrycolor="#242424",
        showsubunits=False, subunitcolor="white",
        showframe=False
    )

    fig_map.update_layout(autosize=True,
                           height=300,
                           margin=dict(l=10, r=10, t=10, b=10),
                           geo=dict(bgcolor= 'rgba(0,0,0,0)'),
                           coloraxis_colorbar=None,
                           plot_bgcolor='red',
                           paper_bgcolor='rgba(0,0,0,0)'
                           )

    title_map = 'Global Variation of ' + indicator + ' DALYs in ' + str(year)

    return fig_map, title_map

# Line chart
@app.callback(Output('line-chart', 'figure'),
              Output('line-title', 'children'),
              Input('apply-button', 'n_clicks'),
              [State('country-picker', 'value'),
              State('indicator-picker', 'value')])

def update_line(n_clicks, country, indicator):
    country_df = df_global[df_global['country'] == country]
    indicator_df = country_df[['year', indicator]]

    fig_line = px.line(indicator_df,
                       x='year',
                       y=indicator,
                       labels='none',
                       color_discrete_sequence=px.colors.qualitative.Dark24)

    fig_line.update_layout(autosize=True,#width=450,
                           height=300,
                           margin=dict(t=10, b=10, l=10, r=10),
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)',
                           xaxis_title="",
                           yaxis_title="",
                           legend=dict(
                               orientation="h",
                               yanchor="bottom",
                               y=1.02,
                               xanchor="right",
                               x=1
                               )
                           )

    title_line = 'Annual Variation of ' + indicator + ' DALYs for ' + country

    return fig_line, title_line

# Run app
if __name__ == "__main__":
    app.run_server(debug=True, port=1234)