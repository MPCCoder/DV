# --------- NOVA IMS -----------
#  Digital Visualization Project
# --- Space Launch Statistics ---
# Mauro Camarinha 20170333
# Licínio Pereira 20221252

# imports
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Data Load
TotalsByCountry = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountry')
TotalsByCountry.fillna(0, inplace=True)

TotalsByCountryYear = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountryYear')
TotalsByCountryYear.fillna(0, inplace=True)

RawData = pd.read_excel('data/spacelaunches.xlsx', sheet_name='RawData')
# Remove future scheduled launches
RawData = RawData[RawData['Year'] < 2023]

country_options = [dict(label=country, value=country) for country in RawData['Country'].unique()]

# print(TotalsByCountry.head(50).to_string())

# print(TotalsByCountry.shape)

mapbox_token = 'pk.eyJ1IjoibWNhbWFyaW5oYSIsImEiOiJjbGllcm5qNGYwbW5qM2RzMDFkeHlyemZrIn0.ZPA2E7nD2vGQ782y_9iEQA'
# define map data
data_scattermap = dict(type='scattermapbox',
                       lat=TotalsByCountry['Lat'],
                       lon=TotalsByCountry['Lon'],
                       name="",
                       mode="markers",
                       text=TotalsByCountry['Country'],
                       customdata=TotalsByCountry['Total Launches'],
                       marker=dict(color='steelblue',
                                   opacity=0.8,
                                   size=np.log2(TotalsByCountry['Total Launches']) * 5,
                                   sizemin=4
                                   ),
                       hovertext=(TotalsByCountry['Successful'] / TotalsByCountry['Total Launches']),
                       hovertemplate="<b>Country: </b> %{text} <br>" +
                                     "<b>Total Launches: </b> %{customdata} <br>"
                                     "<b>Success Rate: %{hovertext:.0%}",
                       )

layout_scattermap = dict(mapbox=dict(style='light',
                                     accesstoken=mapbox_token
                                     ),
                         autosize=False,
                         margin=dict(
                             l=0,
                             r=0,
                             b=0,
                             t=0
                         ),
                         paper_bgcolor='#cad2d3',
                         hovermode='closest'
                         )

fig_scattermap = go.Figure(data=data_scattermap, layout=layout_scattermap)

# Construction of the App
app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div([
        html.Div(
            html.Img(
                src="https://www.clipartmax.com/png/small/157-1578608_space-rocket-launch-vector-rocket-launch-logo-png.png"),
            id="logo"
        ),
        html.Div([
            html.H1('Space launches worldwide'),
            html.H2('1957 to 2022')],
            id="title"
        )],
        id='top_div', className='row'),

    html.Div([
        html.Label('Year range:'),
        dcc.RangeSlider(
            id='date_range',
            min=RawData['Year'].min(),
            max=RawData['Year'].max(),
            marks={i: '{}'.format(str(i)) for i in range(1960, 2040, 5)},
            value=[1957, 2022],
            tooltip={"placement": "bottom", "always_visible": True},
            step=1
        )],
        className='filter'
    ),
    html.Div([
        html.Div([
            html.Div([
                html.H1('6496',id='grand_total'),
                html.P('launches'),
                html.H1('10', id='nr_countries'),
                html.P('countries')], id='kpi'),
            dcc.Markdown('<h3>In which countries are space missions launched?</h3> '
                         '<h3>How does it vary over time?</h3>'
                         '<p> Explore who got it first in 1959, the cold war, space race and access to space today.</p>'
                         '<p class=\'notes\'>use the slider to change the year interval at the top and position the mouse over the marker for more details.</p>',
                         dangerously_allow_html=True)],
            id='map_sidebar'),
        dcc.Graph(
            id='map',
            figure=fig_scattermap
        )],
        className='row',
        id='map_area'
    ),
    html.Div([
        html.Label('Countries:'),
        dcc.Dropdown(
            id="countries_ddl",
            options=country_options,
            value=['United States','Russia','China'],
            multi=True
            )],
        className='filter'),
    html.Div([html.Div([
        html.H3('Total Launches by Country and Year', className='graph_title'),
        dcc.Graph(
            id='main_players',
        )], id='main_players_div'),
        html.Div([
            html.Div([
                    html.H1('6496',id='sub_total'),
                    html.P('launches'),
                    html.H1('10', id='nr_pads'),
                    html.P('launch locations (pads)')],
                id='kpi2'),
            dcc.Markdown('<h3>What is the timeline evolution for today dominant countries?</h3>'
                         '<h3>Europeans launch from French Guiana, how do they compare to other countries?</h3>'
                         '<p> Explore the rise of China in the last years. '
                         'In the era of Soviet Union, a lot of lauches taked place in Khazakstan,'
                         ' view the evolution.</p>'
                         '<p class=\'notes\'>use the countries selector to add and remove countries, the date range also affects the chart.</p>',
                         dangerously_allow_html=True),
            ],
        id='main_players_sidebar'),
    ],
        className='row',
        id='timeline_area'
    ),
    html.Div('@2023 Mauro Camarinha & Licínio Pereira',style={'margin-top': 20, 'color':'White'})],
    id='main-div')




# Map KPI - total launches
@app.callback(
    Output('grand_total', 'children'),
    [Input('date_range', 'value')]
)
def update_grandtotal(dates):
    if dates is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    raw = TotalsByCountryYear

    # apply filter
    grand_total = raw[raw['Year'].between(dates[0], dates[1])]["Total Launches"].sum()

    return grand_total

# Map kpi nr of countries
@app.callback(
    Output('nr_countries', 'children'),
    [Input('date_range', 'value')]
)
def update_nr_countries(dates):
    if dates is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    raw = TotalsByCountryYear

    # apply filter
    raw = raw[raw['Year'].between(dates[0], dates[1])]
    nr_countries = raw['Country'].nunique()

    return nr_countries

# Map update
@app.callback(
    Output('map', 'figure'),
    Input('date_range', 'value')
)
def update_map(years):
    if years is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    totals = TotalsByCountryYear

    # apply filter
    totals = totals[totals['Year'].between(years[0], years[1])]


    totals_sum = totals.groupby(['Country', 'Lat', 'Lon']).agg(
        {'Total Launches': 'sum', 'Failure': 'sum', 'Successful': 'sum', 'Partial Failure': 'sum'}).reset_index(
        ['Country', 'Lat', 'Lon'])

    # define map data
    data_scattermap = dict(type='scattermapbox',
                           lat=totals_sum['Lat'],
                           lon=totals_sum['Lon'],
                           name="",
                           mode="markers",
                           text=totals_sum['Country'],
                           customdata=totals_sum['Total Launches'],
                           marker=dict(color='steelblue',
                                       opacity=0.8,
                                       size=(np.log(totals_sum['Total Launches']) + 1) * 5,
                                       # totals_sum['Total Launches'] / 10,
                                       sizemin=5
                                       ),
                           hovertext=(totals_sum['Successful'] / totals_sum['Total Launches']),
                           hovertemplate="<b>Country: </b> %{text} <br>" +
                                         "<b>Total Launches: </b> %{customdata} <br>"
                                         "<b>Success Rate: %{hovertext:.0%}",

                           )

    layout_scattermap = dict(mapbox=dict(style='light',
                                         accesstoken=mapbox_token,
                                         # Fix center
                                         # center=dict(lat=,
                                         #             lon=]
                                         #             )
                                         # zoom=0.8
                                         ),
                             autosize=True,
                             margin=dict(
                                 l=0,
                                 r=0,
                                 b=0,
                                 t=0
                             ),
                             paper_bgcolor='#9EDBDA',
                             hovermode='closest'

                             )

    return go.Figure(data=data_scattermap, layout=layout_scattermap)

# Main players line plot
# Filters: years, country
@app.callback(
    Output('main_players', 'figure'),
    Input('countries_ddl', 'value'),
    Input('date_range', 'value')
)
def update_main_players(countries, years):
    if countries is None or years is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    totals = TotalsByCountryYear

    # apply filter by date
    totals = totals[totals['Year'].between(years[0], years[1])]

    # apply filter by country
    totals =  totals[totals['Country'].isin(countries)]

    lines_data = []
    lines_layout = []

    for country in countries:

        line_data = totals[totals['Country'] == country]

        x_line = line_data['Year']
        y_line = line_data['Total Launches']

        lines_data.append(dict(type='scatter',
                               mode='lines',
                               x=x_line,
                               y=y_line,
                               text=y_line.name,
                               customdata=line_data['Country'],
                               name=country,
                               hovertemplate="<b>Country: </b> %{customdata} <br>" +
                                             "<b>Year: </b> %{x} <br>" +
                                             "<b>Tot. Launches: </b> %{y} <br>")
                          )

        lines_layout = dict(
            xaxis=dict(title='Year'),
            yaxis=dict(title='Total Launches'
                       ),

            legend=dict(
                orientation="h",
                font=dict(
                    color='#112d32'
                )
            ),
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0
            ),
            plot_bgcolor='#cad2d3',
            paper_bgcolor='#cad2d3'
        )

    return go.Figure(data=lines_data , layout=lines_layout)

# Lauches by country KPI - subtotal launches
@app.callback(
    Output('sub_total', 'children'),
    Input('countries_ddl', 'value'),
    [Input('date_range', 'value')]
)
def update_mp_launches(countries,dates):
    if dates is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    raw = TotalsByCountryYear

    # apply filter
    grand_total = raw[raw['Year'].between(dates[0], dates[1]) & raw['Country'].isin(countries)]["Total Launches"].sum()

    return grand_total

# Map kpi nr of countries
@app.callback(
    Output('nr_pads', 'children'),
    Input('countries_ddl', 'value'),
    [Input('date_range', 'value')]
)
def update_pads(countries,dates):
    if dates is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    raw = RawData

    # apply filters
    raw = raw[raw['Year'].between(dates[0], dates[1]) & raw['Country'].isin(countries)]

    nr_pads = raw['Pad'].nunique()

    return nr_pads

if __name__ == '__main__':
    app.run_server(debug=True)
