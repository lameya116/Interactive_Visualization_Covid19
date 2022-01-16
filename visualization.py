import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

df = pd.read_excel("datas/choropleth.xlsx")
bar_df = pd.read_excel (r'datas/barData.xlsx')
line_df = pd.read_excel('datas/line.xlsx')

health_support_ratio=[]
country=[]
recovered=[]
infected=[]

total_infected=bar_df['Total Population']
hospital_beds=bar_df['Hospital beds in Recent years']
doctor_number=bar_df['Hospital doctors in Recent years']
nurse_number=bar_df['Hospital nurses in Recent years']
recovered_case=bar_df['Recovered Case']
countries = bar_df['Country']
for i in range(len(recovered_case)):
    recovered.append(np.log(recovered_case[i]))

for i in range(len(total_infected)):
    infected.append(np.log(total_infected[i]))

for i in range(len(total_infected)):
    health_support_ratio.append((np.log((hospital_beds[i])+(doctor_number[i])+(nurse_number[i]))))
    
for i in range(len(countries)):
    country.append(countries[i])

trace1 = go.Bar(x=country, y=health_support_ratio, name='Health Support Ratio',offsetgroup=1)
trace2 = go.Bar(x=country, y=recovered, name='Recovered_Case',offsetgroup=0)
trace3 = go.Bar(x=country, y=infected, name='Total Infected Cases',offsetgroup=0)

for col in df.columns:
    df[col] = df[col].astype(str)
df['text'] = df['location'] + '<br>' + \
'Total Cases ' + df['total_cases'] + '<br>' +  ' Total Death ' + df['total_deaths'] + '<br>' + \
'Life Expectancy ' + df['life_expectancy'] +'<br>' + ' New cases ' + df['new_cases']

app.layout = html.Div([html.Div( 
        children=[html.Img(src=app.get_asset_url('download.png'), 
                style={
                'height': '20%',
                'width': '20%',
                 'textAlign': 'left'
            })]
      ),
    
    html.Div(className="app-header",
        children=[html.H1('COVID-19 Dashboard by the Master of Computer Science WS 2019',className="app-header--title",
                          style={'textAlign':'center'})
                 ]),
    dcc.Tabs(id='bar-tab',value='map',children=[
        dcc.Tab(label='Map',value='map'),
        dcc.Tab(label='Bar',value='bar'),
        dcc.Tab(label='Line',value='line')
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('bar-tab', 'value')])
def render_content(tab):
    if tab == 'map':
        return html.Div([
            html.Div(children=[dcc.Markdown("""
                      _**Map** - showing the Total number of Infected cases around the world and giving information on 
                      Total deaths, New Cases and Life Expectancy per country_"""
            )]),

            dcc.Graph(id='example-graph'),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[
                {'label': 'World', 'value': 'world'},
                {'label': 'Asia', 'value': 'asia'},
                {'label': 'Africa', 'value': 'africa'},
                {'label': 'Europe', 'value': 'europe'},
                {'label': 'North America', 'value': 'north america'},
                {'label': 'South America', 'value': 'south america'}
                ],
            value='world'
            )
    ])

    elif tab == 'bar':
        return html.Div([ html.Div(children=[dcc.Markdown("""
                      _**Stacked Bar graph** - visualize data of Total Infected Cases, Recovered Case and Health Ratio of countries_"""
            )]),
               html.Div('Health Ratio - calculated based on Medical Resources such as Number of Hospital Beds, Practising Doctors, Practising Nurses per 1000 population',className='line-title'),

            dcc.Graph(id='graph',
                     figure=go.Figure(data=[trace1, trace2, trace3],
                               layout=go.Layout(barmode='stack',title='Medical Resources and Epidemic COVID-19 Report, 2020',
                                                yaxis_title="Number of COVID-19 cases (per 1000)",xaxis_title="Countries"))
            )
        ])
    elif tab == 'line':
        return html.Div([
            
            html.Div(children=[dcc.Markdown("""
                      _**Line Graph** - showing the Total number of Infected cases and Death cases per Country over time_"""
            )]),html.Div('Select Continent ...',className="line-title"),
            dcc.Dropdown(
                id='continent-dropdown-line',
                options=[
                {'label': 'Asia', 'value': 'asia'},
                {'label': 'Africa', 'value': 'africa'},
                {'label': 'Europe', 'value': 'europe'},
                {'label': 'North America', 'value': 'north america'},
                {'label': 'South America', 'value': 'south america'}
                ],
            value='asia',clearable=False
            ),
            html.Div('Select Country ...',className="line-title"),
            dcc.Dropdown(id='country-dropdown'),
            dcc.Graph(id='display-selected-values'),

            ])


@app.callback(
    Output('country-dropdown', 'options'),
    [Input('continent-dropdown-line', 'value')])
def set_country_options(selected_continent):
    return [{'label': i, 'value': i} for i in 
            df.location[df.continent==selected_continent]]

@app.callback(
    dash.dependencies.Output('country-dropdown', 'value'),
    [dash.dependencies.Input('country-dropdown', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('display-selected-values', 'figure'),
    [Input('continent-dropdown-line', 'value'),
     Input('country-dropdown', 'value')])            
def set_display_children(selected_continent,selected_country):
    mod_df=line_df[line_df.location==selected_country]
    x=mod_df['date']
    y=mod_df['total_cases']
    z=mod_df['total_deaths']
    fig = px.line(mod_df, x=x, y=[y,z], title='Total Infected Cases and Death Cases of COVID-19 in {}, 2020'.format(selected_country))
    fig.update_layout(yaxis_title="Number of COVID-19 cases")
    return fig
            
@app.callback(
    Output('example-graph','figure'),
    [Input('continent-dropdown', 'value')])
def update_figure(value):
    if value=='world':
        fig = go.Figure(data=go.Choropleth(
    locations=df['location'], # Spatial coordinates
    z = df['total_cases'].astype(float), # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Sunsetdark',
    colorbar_title = "Total Cases",
    autocolorscale=False,
    text=df['text'], # hover text
    marker_line_color='white', # line markers between states
    ))

        fig.update_layout(
    title_text = 'Novel COVID-19 Outbreak, 2020',
    geo=dict(
        scope=value,
        projection=go.layout.geo.Projection(type = 'equirectangular'),
        lataxis_range=[-55,90], lonaxis_range=[-200, 200]
    )
    )
    else:
        filtered_df=df[df.continent==value]
        for col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].astype(str)
        filtered_df['text'] = filtered_df['location'] + '<br>' + \
        'Total Cases ' + filtered_df['total_cases'] + '<br>' +  ' Total Death ' + filtered_df['total_deaths'] + '<br>' + \
        'Life Expectancy ' + filtered_df['life_expectancy'] +'<br>' + ' New cases ' + filtered_df['new_cases']

        fig = go.Figure(data=go.Choropleth(
    locations=filtered_df['location'], # Spatial coordinates
    z = filtered_df['total_cases'].astype(float), # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Sunsetdark',
    colorbar_title = "Total Cases",
    autocolorscale=False,
    text=filtered_df['text'], # hover text
    marker_line_color='white', # line markers between states
    ))

        fig.update_layout(
    title_text = 'Novel COVID-19 outbreak in {}, 2020'.format(value),
    geo=dict(
        scope=value,
        projection=go.layout.geo.Projection(type = 'equirectangular'),
    )
    )
    return fig





if __name__ == '__main__':
    app.run_server(debug=True,port=8050,use_reloader=False)